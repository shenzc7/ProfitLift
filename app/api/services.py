"""Service layer for ProfitLift FastAPI endpoints."""

from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path
from tempfile import NamedTemporaryFile
import sys
from typing import Dict, List, Optional, TYPE_CHECKING

import yaml
from fastapi import UploadFile

# Lazy import pandas to avoid hanging on module import
if TYPE_CHECKING:
    import pandas as pd
else:
    def _get_pandas():
        import pandas as pd
        return pd

from app.assets.database import DatabaseManager
from app.causal.causal_estimator import CausalEstimator, UpliftResult
from app.ingest.csv_importer import CSVImporter, ImportResult
from app.mining.context_aware_miner import ContextAwareMiner
from app.mining.context_types import Context, ContextualRule
from app.score.multi_objective import MultiObjectiveScorer
from app.api.models import (
    BundleResponse,
    ContextFilter,
    ContextSummary,
    MaintenanceActionRequest,
    MaintenanceActionResponse,
    MaintenanceSnapshot,
    RuleFilter,
    RuleResponse,
    UpliftMetrics,
    WhatIfRequest,
    WhatIfResponse,
)

DEFAULT_CONFIG_PATH = Path("config/default.yaml")
DEFAULT_SCORING_PATH = Path("config/scoring.yaml")


def _resolve_path(relative: Path) -> Path:
    """Resolve resource paths for both dev and frozen builds."""
    candidates = [
        relative,
        Path(__file__).resolve().parents[2] / relative,
        Path(getattr(sys, "_MEIPASS", "")) / relative,  # type: ignore[attr-defined]
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return relative


def _load_yaml(path: Path) -> Dict:
    """Load a YAML file if it exists."""
    resolved = _resolve_path(path)
    if resolved.exists():
        with resolved.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}
    return {}


def _build_context_summary(context: Context) -> ContextSummary:
    """Convert internal Context dataclass to API response summary."""
    return ContextSummary(
        label=str(context),
        store_id=context.store_id,
        time_bin=context.time_bin,
        weekday_weekend=context.weekday_weekend,
        quarter=context.quarter,
        festival_period=context.festival_period,
    )


def _make_rule_explanation(rule: ContextualRule, uplift: Optional[UpliftResult]) -> str:
    """Generate a concise, business-facing explanation for a rule."""
    ant_str = ", ".join(sorted(rule.antecedent))
    cons_str = ", ".join(sorted(rule.consequent))
    context_label = str(rule.context)
    base = (
        f"When shoppers buy {ant_str}, they also tend to add {cons_str} "
        f"({rule.confidence:.0%} of the time, lift {rule.lift:.2f})."
    )
    if context_label != "Overall":
        base = f"In {context_label.lower()}, {base[0].lower()}{base[1:]}"

    if uplift and uplift.incremental_attach_rate > 0:
        base += (
            f" True uplift of {uplift.incremental_attach_rate:.1%} "
            f"drives about ${uplift.incremental_margin:.2f} extra margin per basket."
        )
    elif rule.profit_score:
        base += f" Expect roughly ${rule.profit_score:.2f} extra margin per basket."

    return base


def _rule_to_response(
    rule: ContextualRule,
    uplift: Optional[UpliftResult],
) -> RuleResponse:
    """Convert a contextual rule into a RuleResponse payload."""
    uplift_payload: Optional[UpliftMetrics] = None
    if uplift:
        uplift_payload = UpliftMetrics(
            incremental_attach_rate=uplift.incremental_attach_rate,
            incremental_revenue=uplift.incremental_revenue,
            incremental_margin=uplift.incremental_margin,
            control_rate=uplift.control_rate,
            treatment_rate=uplift.treatment_rate,
            confidence_interval=uplift.confidence_interval,
            sample_size=uplift.sample_size,
        )

    return RuleResponse(
        antecedent=sorted(rule.antecedent),
        consequent=sorted(rule.consequent),
        context=_build_context_summary(rule.context),
        support=rule.support,
        confidence=rule.confidence,
        lift=rule.lift,
        profit_score=rule.profit_score,
        diversity_score=rule.diversity_score,
        overall_score=rule.overall_score,
        explanation=_make_rule_explanation(rule, uplift),
        uplift=uplift_payload,
    )


def _rule_to_bundle_response(
    rule: ContextualRule,
    uplift: Optional[UpliftResult],
) -> BundleResponse:
    """Convert contextual rule into bundle recommendation payload."""
    uplift_payload: Optional[UpliftMetrics] = None
    if uplift:
        uplift_payload = UpliftMetrics(
            incremental_attach_rate=uplift.incremental_attach_rate,
            incremental_revenue=uplift.incremental_revenue,
            incremental_margin=uplift.incremental_margin,
            control_rate=uplift.control_rate,
            treatment_rate=uplift.treatment_rate,
            confidence_interval=uplift.confidence_interval,
            sample_size=uplift.sample_size,
        )

    bundle_id = f"{'-'.join(sorted(rule.antecedent))}__{('-'.join(sorted(rule.consequent)))}__{str(rule.context)}"
    anchor_items = sorted(rule.antecedent)
    recommended_items = sorted(rule.consequent)
    expected_margin = uplift.incremental_margin if uplift else rule.profit_score
    expected_attach = (
        uplift.treatment_rate if uplift and uplift.treatment_rate > 0 else rule.confidence
    )

    if uplift and uplift.incremental_attach_rate > 0:
        narrative = (
            f"{str(rule.context)} shoppers who buy {', '.join(anchor_items)} respond to "
            f"featuring {', '.join(recommended_items)}, adding {uplift.incremental_attach_rate:.1%} "
            f"more baskets and about ${expected_margin:.2f} margin."
        )
    else:
        narrative = (
            f"Bundle {', '.join(anchor_items)} with {', '.join(recommended_items)} in "
            f"{str(rule.context)} to capture {expected_attach:.0%} attach rate and "
            f"roughly ${expected_margin:.2f} extra margin per basket."
        )

    return BundleResponse(
        bundle_id=bundle_id,
        anchor_items=anchor_items,
        recommended_items=recommended_items,
        context=_build_context_summary(rule.context),
        overall_score=rule.overall_score or 0.0,
        expected_margin=expected_margin,
        expected_attach_rate=expected_attach,
        narrative=narrative,
        uplift=uplift_payload,
    )


class AnalyticsService:
    """Encapsulates business logic required by the API routes."""

    def __init__(self, config_path: Path = DEFAULT_CONFIG_PATH):
        self.logger = logging.getLogger(__name__)
        config = _load_yaml(config_path)

        db_path = (
            config.get("database", {}).get("path")
            if isinstance(config.get("database"), dict)
            else None
        ) or "profitlift.db"
        self.db = DatabaseManager(db_path)
        self.csv_importer = CSVImporter(db_path=db_path)

        scoring_config = _load_yaml(DEFAULT_SCORING_PATH)
        weights = scoring_config.get("weights") if isinstance(scoring_config, dict) else None
        self.scorer = MultiObjectiveScorer(weights=weights)

        uplift_config = config.get("uplift", {}) if isinstance(config, dict) else {}
        min_incremental_lift = uplift_config.get("min_incremental_lift", 0.05)
        self.causal_estimator = CausalEstimator(min_incremental_lift=min_incremental_lift)
        
        # Simple in-memory cache for mined rules
        self._rules_cache: Dict[str, List[ContextualRule]] = {}

    def clear_cache(self):
        """Clear the rules cache."""
        self._rules_cache = {}

    # ------------------------------------------------------------------ #
    # Data loading helpers
    # ------------------------------------------------------------------ #
    def _load_transactions(self, filters: ContextFilter | None = None) -> 'pd.DataFrame':
        """Load transaction-level data, applying context filters if provided."""
        pd = _get_pandas()
        query = """
            SELECT
                t.transaction_id,
                t.timestamp,
                t.store_id,
                t.customer_id_hash,
                t.context_time_bin,
                t.context_weekday_weekend,
                t.context_quarter,
                t.discount_flag,
                ti.item_id,
                ti.quantity,
                ti.price,
                i.item_name,
                i.category,
                i.margin_pct
            FROM transactions t
            JOIN transaction_items ti ON t.transaction_id = ti.transaction_id
            JOIN items i ON ti.item_id = i.item_id
        """
        conditions = []
        params: List = []

        if filters:
            if filters.store_id:
                conditions.append("t.store_id = ?")
                params.append(filters.store_id)
            if filters.time_bin:
                conditions.append("t.context_time_bin = ?")
                params.append(filters.time_bin)
            if filters.weekday_weekend:
                conditions.append("t.context_weekday_weekend = ?")
                params.append(filters.weekday_weekend)
            if filters.quarter:
                conditions.append("t.context_quarter = ?")
                params.append(filters.quarter)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        rows = self.db.execute_query(query, tuple(params) if params else None)
        df = pd.DataFrame(rows)

        if df.empty:
            self.logger.info("No transactions matched the provided filters.")
            return df

        # Ensure timestamp is datetime for downstream components
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

        return df

    # ------------------------------------------------------------------ #
    # CSV import
    # ------------------------------------------------------------------ #
    async def import_csv(self, upload_file: UploadFile) -> ImportResult:
        """Persist uploaded CSV to a temp file and run the CSV importer."""
        suffix = Path(upload_file.filename or "data.csv").suffix or ".csv"
        with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(await upload_file.read())
            temp_path = Path(temp_file.name)

        try:
            result = self.csv_importer.import_csv(str(temp_path))
            self.clear_cache() # Invalidate cache on new data
            return result
        finally:
            temp_path.unlink(missing_ok=True)

    # ------------------------------------------------------------------ #
    # Rule mining
    # ------------------------------------------------------------------ #
    def get_rules(self, filters: RuleFilter) -> List[RuleResponse]:
        """Mine, score, and format association rules."""
        # Check cache for exact filter match (simplified caching strategy)
        cache_key = f"rules_{filters.min_support}_{filters.min_confidence}_{filters.min_rows_per_context}_{filters.max_depth}"
        
        transactions = self._load_transactions(filters)
        if transactions.empty:
            return []

        if cache_key in self._rules_cache:
            rules = self._rules_cache[cache_key]
        else:
            miner = ContextAwareMiner(
                min_support=filters.min_support,
                min_confidence=filters.min_confidence,
                min_rows_per_context=filters.min_rows_per_context,
            )
            rules = miner.mine_all_contexts(transactions, max_depth=filters.max_depth)
            self._rules_cache[cache_key] = rules

        if not rules:
            return []

        # Filter by lift threshold
        rules = [rule for rule in rules if rule.lift >= filters.min_lift]
        if not rules:
            return []

        # Cap candidates to keep scoring performant
        max_candidates = max(filters.limit * 10, 500)
        rules = rules[:max_candidates]

        scored_rules = self.scorer.score_rules(rules, transactions)
        top_rules = scored_rules[: filters.limit]

        uplift_results: Dict[int, UpliftResult] = {}
        if filters.include_causal:
            for idx, rule in enumerate(top_rules[: min(10, len(top_rules))]):
                uplift_result = self.causal_estimator.estimate_uplift(rule, transactions)
                uplift_results[idx] = uplift_result

        responses: List[RuleResponse] = []
        for idx, rule in enumerate(top_rules):
            uplift = uplift_results.get(idx)
            responses.append(_rule_to_response(rule, uplift))

        return responses

    # ------------------------------------------------------------------ #
    # Bundles
    # ------------------------------------------------------------------ #
    def get_bundles(self, filters: RuleFilter) -> List[BundleResponse]:
        """Derive bundle recommendations from top scored rules."""
        bundles: List[BundleResponse] = []

        # Mine contextual rules once for deriving bundle opportunities
        transactions = self._load_transactions(filters)
        if transactions.empty:
            return []

        # Enforce a higher min_support for bundles to avoid combinatorial explosion
        # with dense datasets or multiple uploads.
        safe_min_support = max(filters.min_support, 0.05)
        
        # Use a distinct cache key for bundles since params are different
        # Also limit max_depth to 1 (Overall + Single Dims) to speed up loading
        cache_key = f"bundles_{safe_min_support}_{filters.min_confidence}_{filters.min_rows_per_context}"

        if cache_key in self._rules_cache:
            rules = self._rules_cache[cache_key]
        else:
            miner = ContextAwareMiner(
                min_support=safe_min_support,
                min_confidence=filters.min_confidence,
                min_rows_per_context=filters.min_rows_per_context,
            )
            # Limit depth to 0 (Overall only) for instant loading
            # Context-specific rules can be explored in the Rules page
            rules = miner.mine_all_contexts(transactions, max_depth=0)
            self._rules_cache[cache_key] = rules

        rules = [rule for rule in rules if rule.lift >= filters.min_lift]
        if not rules:
            return []

        scored_rules = self.scorer.score_rules(rules, transactions)[: filters.limit]

        uplift_cache: Dict[str, UpliftResult] = {}

        seen_keys: set[str] = set()

        for idx, rule in enumerate(scored_rules):
            cache_key = f"{sorted(rule.antecedent)}->{sorted(rule.consequent)}|{str(rule.context)}"

            if cache_key in seen_keys:
                continue
            seen_keys.add(cache_key)

            uplift: Optional[UpliftResult] = None

            if filters.include_causal:
                if cache_key not in uplift_cache and idx < 10:
                    uplift_cache[cache_key] = self.causal_estimator.estimate_uplift(
                        rule, transactions
                    )
                uplift = uplift_cache.get(cache_key)

            bundles.append(_rule_to_bundle_response(rule, uplift))

            if len(bundles) >= filters.limit:
                break

        return bundles

    # ------------------------------------------------------------------ #
    # What-if simulation
    # ------------------------------------------------------------------ #
    def simulate_what_if(self, request: WhatIfRequest) -> WhatIfResponse:
        """Run the what-if simulator for a custom scenario."""
        context_filter = request.context or ContextFilter()
        transactions = self._load_transactions(context_filter)

        if transactions.empty:
            return WhatIfResponse(
                projected_attach_rate=0.0,
                incremental_attach_rate=0.0,
                incremental_revenue=0.0,
                incremental_margin=0.0,
                projected_margin_total=0.0
                if request.expected_traffic
                else None,
                uplift=None,
                narrative="Not enough matching history to simulate this scenario yet.",
            )

        context = Context(
            store_id=context_filter.store_id,
            time_bin=context_filter.time_bin,
            weekday_weekend=context_filter.weekday_weekend,
            quarter=context_filter.quarter,
        )

        placeholder_rule = ContextualRule(
            antecedent=frozenset(request.antecedent),
            consequent=frozenset(request.consequent),
            support=0.0,
            confidence=0.0,
            lift=0.0,
            context=context,
        )

        uplift = self.causal_estimator.estimate_uplift(placeholder_rule, transactions)

        discount_multiplier = 1 - request.anticipated_discount_pct
        incremental_revenue = uplift.incremental_revenue * discount_multiplier
        incremental_margin = uplift.incremental_margin * discount_multiplier
        incremental_attach = uplift.incremental_attach_rate
        projected_attach = max(uplift.treatment_rate, uplift.control_rate + incremental_attach)

        projected_margin_total = (
            incremental_margin * request.expected_traffic
            if request.expected_traffic is not None
            else None
        )

        uplift_payload = UpliftMetrics(
            incremental_attach_rate=incremental_attach,
            incremental_revenue=incremental_revenue,
            incremental_margin=incremental_margin,
            control_rate=uplift.control_rate,
            treatment_rate=uplift.treatment_rate,
            confidence_interval=uplift.confidence_interval,
            sample_size=uplift.sample_size,
        )

        context_label = str(context) if str(context) != "Overall" else "overall shopper base"
        narrative = (
            f"If you spotlight {' & '.join(request.antecedent)} and nudge "
            f"{', '.join(request.consequent)} in the {context_label}, "
            f"attach rate is projected to reach {projected_attach:.1%} "
            f"({incremental_attach:.1%} uplift) with about ${incremental_margin:.2f} "
            f"extra margin per basket."
        )

        if request.expected_traffic and projected_margin_total is not None:
            narrative += (
                f" Over roughly {request.expected_traffic:,} baskets that adds up "
                f"to ${projected_margin_total:,.0f} incremental margin."
            )

        return WhatIfResponse(
            projected_attach_rate=projected_attach,
            incremental_attach_rate=incremental_attach,
            incremental_revenue=incremental_revenue,
            incremental_margin=incremental_margin,
            projected_margin_total=projected_margin_total,
            uplift=uplift_payload,
            narrative=narrative,
        )

    # ------------------------------------------------------------------ #
    # Dashboard Stats
    # ------------------------------------------------------------------ #
    def get_stats(self) -> Dict:
        """Calculate real dashboard statistics from the database."""
        # 1. Active Rules Count (approximate by running a quick mining pass or caching)
        # For speed, we'll do a quick count of high-lift rules on overall data
        transactions = self._load_transactions()
        if transactions.empty:
            return {
                "avg_lift": 0.0,
                "profit_opportunity": 0.0,
                "active_rules": 0,
                "top_opportunities": []
            }

        # We can reuse get_rules with default filters to get a sense of "Active Rules"
        # In a real prod system, this might be cached or stored in a 'rules' table
        default_filter = RuleFilter(min_support=0.05, min_confidence=0.1, min_lift=1.2, limit=200, max_depth=0)
        rules = self.get_rules(default_filter)
        
        if not rules:
             return {
                "avg_lift": 0.0,
                "profit_opportunity": 0.0,
                "active_rules": 0,
                "top_opportunities": []
            }

        avg_lift = sum(r.lift for r in rules) / len(rules)
        
        # Estimate profit opportunity: sum of profit_score of top 10 rules * estimated monthly volume (e.g. 1000)
        # This is a heuristic for the dashboard
        profit_opportunity = sum((r.profit_score or 0) for r in rules[:20]) * 1000
        
        return {
            "avg_lift": round(avg_lift, 2),
            "profit_opportunity": round(profit_opportunity, 2),
            "active_rules": len(rules),
            # Return top 5 for a mini-chart or list if needed
            "top_opportunities": [
                {"label": f"{', '.join(r.antecedent)} + {', '.join(r.consequent)}", "value": r.profit_score}
                for r in rules[:5]
            ]
        }

    # ------------------------------------------------------------------ #
    # Maintenance / Settings
    # ------------------------------------------------------------------ #
    def get_system_overview(self) -> MaintenanceSnapshot:
        """Return a lightweight operational snapshot for the Settings page."""
        tables = [
            "items",
            "transactions",
            "transaction_items",
            "association_rules",
            "uplift_results",
        ]
        counts = {table: self.db.get_table_count(table) for table in tables}

        return MaintenanceSnapshot(
            db_path=str(Path(self.db.db_path).resolve()),
            table_counts=counts,
            cache_entries=len(self._rules_cache),
            last_ingest_at=self.db.get_last_transaction_timestamp(),
            api_version="1.0.0",
        )

    def clear_data(self, request: MaintenanceActionRequest) -> MaintenanceActionResponse:
        """Clear cached rules/bundles and optionally uploaded transaction data."""
        tables_to_clear: List[str] = []

        if request.clear_rules or request.clear_bundles:
            tables_to_clear.extend(["uplift_results", "association_rules"])

        if request.clear_uploads:
            tables_to_clear.extend(["transaction_items", "transactions", "items"])

        ordered_unique = list(dict.fromkeys(tables_to_clear))
        counts_before = {table: self.db.get_table_count(table) for table in ordered_unique}

        if ordered_unique:
            self.db.clear_tables(ordered_unique)

        if request.clear_cache:
            self.clear_cache()

        return MaintenanceActionResponse(
            tables_cleared=ordered_unique,
            counts_before=counts_before,
            cache_cleared=request.clear_cache,
        )


@lru_cache(maxsize=1)
def get_analytics_service() -> AnalyticsService:
    """Singleton accessor for the analytics service."""
    return AnalyticsService()
