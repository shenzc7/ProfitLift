"""Pydantic models for the ProfitLift FastAPI backend."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel, Field, ConfigDict


class ContextFilter(BaseModel):
    """Optional context filters for narrowing analytics queries."""

    store_id: Optional[str] = Field(
        default=None, description="Restrict to a specific store identifier."
    )
    time_bin: Optional[str] = Field(
        default=None,
        description="Restrict to a context time bin such as morning, midday, evening.",
    )
    weekday_weekend: Optional[str] = Field(
        default=None, description="Filter by weekday or weekend transactions."
    )
    quarter: Optional[int] = Field(
        default=None, ge=1, le=4, description="Filter by calendar quarter (1-4)."
    )
    festival_period: Optional[str] = Field(
        default=None, 
        description="Filter by festival period (diwali, holi, navratri, eid, christmas)."
    )


class RuleFilter(ContextFilter):
    """Filter and tuning parameters for association rule retrieval."""

    min_support: float = Field(
        default=0.01,
        ge=0.0,
        le=1.0,
        description="Minimum support threshold for mining contextual rules.",
    )
    min_confidence: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold for association rules.",
    )
    min_lift: float = Field(
        default=1.0, ge=0.0, description="Minimum lift score for returned rules."
    )
    limit: int = Field(
        default=25,
        ge=1,
        le=200,
        description="Maximum number of rules to return after scoring.",
    )
    min_rows_per_context: int = Field(
        default=50,
        ge=5,
        description=(
            "Minimum rows required per context segment before auto-backoff to broader context."
        ),
    )
    include_causal: bool = Field(
        default=True,
        description="Whether to estimate causal uplift metrics for top-ranked rules.",
    )
    max_depth: int = Field(
        default=0,
        ge=0,
        le=2,
        description="Context depth for mining (0=overall only, 1=add single dimensions, 2=double combinations).",
    )


class ContextSummary(BaseModel):
    """Context metadata included with responses."""

    label: str = Field(description="Human-readable description of the context.")
    store_id: Optional[str] = Field(
        default=None, description="Store identifier if the context is store specific."
    )
    time_bin: Optional[str] = Field(
        default=None, description="Time bin such as morning, midday, afternoon, evening."
    )
    weekday_weekend: Optional[str] = Field(
        default=None, description="Whether the context covers weekday or weekend baskets."
    )
    quarter: Optional[int] = Field(
        default=None, ge=1, le=4, description="Calendar quarter represented by the context."
    )
    festival_period: Optional[str] = Field(
        default=None, description="Festival period (diwali, holi, navratri, etc.)."
    )


class UpliftMetrics(BaseModel):
    """Causal uplift metrics derived from the T-Learner."""

    incremental_attach_rate: float = Field(description="Estimated lift in attach rate.")
    incremental_revenue: float = Field(
        description="Projected incremental revenue per basket."
    )
    incremental_margin: float = Field(
        description="Projected incremental margin per basket."
    )
    control_rate: float = Field(description="Baseline attach rate for the control group.")
    treatment_rate: float = Field(
        description="Observed attach rate for the treatment group."
    )
    confidence_interval: Optional[Tuple[float, float]] = Field(
        default=None,
        description="Approximate bootstrap confidence interval for attach rate uplift.",
    )
    sample_size: int = Field(
        default=0, description="Combined sample size used for uplift estimation."
    )


class RuleResponse(BaseModel):
    """Response payload for a scored association rule."""

    model_config = ConfigDict(from_attributes=True)

    antecedent: List[str] = Field(description="Trigger items in the association rule.")
    consequent: List[str] = Field(
        description="Recommended add-on items predicted by the rule."
    )
    context: ContextSummary = Field(description="Context segment for this rule.")
    support: float = Field(description="Support of the rule within its context.")
    confidence: float = Field(description="Confidence of the rule within its context.")
    lift: float = Field(description="Lift value of the rule within its context.")
    profit_score: Optional[float] = Field(
        default=None,
        description="Expected incremental profit contribution used in multi-objective scoring.",
    )
    diversity_score: Optional[float] = Field(
        default=None,
        description="Diversity score indicating variety contributed by the rule.",
    )
    overall_score: Optional[float] = Field(
        default=None,
        description="Composite multi-objective score used for ranking rules.",
    )
    explanation: str = Field(
        description="Plain-English explanation of why the recommendation makes sense."
    )
    uplift: Optional[UpliftMetrics] = Field(
        default=None,
        description="Optional causal uplift metrics when available.",
    )


class BundleResponse(BaseModel):
    """Aggregated bundle recommendation derived from high-value rules."""

    bundle_id: str = Field(description="Stable identifier for the bundle recommendation.")
    anchor_items: List[str] = Field(
        description="Items frequently purchased together that anchor the bundle."
    )
    recommended_items: List[str] = Field(
        description="Add-on items to suggest alongside the anchor items."
    )
    context: ContextSummary = Field(description="Context segment for the bundle.")
    overall_score: float = Field(
        description="Composite score used to rank bundle opportunities."
    )
    expected_margin: Optional[float] = Field(
        default=None, description="Expected incremental margin per basket."
    )
    expected_attach_rate: Optional[float] = Field(
        default=None, description="Projected attach rate for the recommended bundle."
    )
    narrative: str = Field(
        description="Plain-English reasoning for sharing with merchandising partners."
    )
    uplift: Optional[UpliftMetrics] = Field(
        default=None, description="Optional causal uplift metrics attached to the bundle."
    )


class WhatIfRequest(BaseModel):
    """Inputs for the what-if simulator."""

    antecedent: List[str] = Field(
        description="Anchor items that will trigger the promotion scenario.", min_length=1
    )
    consequent: List[str] = Field(
        description="Target items to evaluate under the what-if scenario.", min_length=1
    )
    context: Optional[ContextFilter] = Field(
        default=None,
        description="Optional context constraints representing the campaign window.",
    )
    anticipated_discount_pct: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Estimated fractional discount applied to the consequent items.",
    )
    expected_traffic: Optional[int] = Field(
        default=None,
        ge=0,
        description="Projected number of baskets exposed during the campaign window.",
    )


class WhatIfResponse(BaseModel):
    """Result of a what-if simulation for a proposed promotion."""

    projected_attach_rate: float = Field(
        description="Expected attach rate under the proposed scenario."
    )
    incremental_attach_rate: float = Field(
        description="Incremental attach rate compared to historical control."
    )
    incremental_revenue: float = Field(
        description="Estimated incremental revenue per basket from the promotion."
    )
    incremental_margin: float = Field(
        description="Estimated incremental margin per basket from the promotion."
    )
    projected_margin_total: Optional[float] = Field(
        default=None,
        description="Total incremental margin over the expected traffic window.",
    )
    uplift: Optional[UpliftMetrics] = Field(
        default=None, description="Detailed uplift metrics used in the projection."
    )
    narrative: str = Field(
        description="Plain-English summary for business stakeholders."
    )


class MaintenanceSnapshot(BaseModel):
    """Operational snapshot used by the Settings page."""

    db_path: str = Field(description="Resolved path to the active SQLite database.")
    table_counts: Dict[str, int] = Field(
        default_factory=dict, description="Row counts for key tables."
    )
    cache_entries: int = Field(
        default=0, description="Number of cached rule mining results in memory."
    )
    last_ingest_at: Optional[str] = Field(
        default=None, description="Timestamp of the most recent ingested transaction."
    )
    api_version: Optional[str] = Field(
        default=None, description="Version of the running API service."
    )


class MaintenanceActionRequest(BaseModel):
    """Request payload for clearing cached/ingested data."""

    clear_rules: bool = Field(
        default=True,
        description="Clear mined rules/uplift tables (covers bundle recommendations too).",
    )
    clear_bundles: bool = Field(
        default=True,
        description="Alias for clearing rule-derived bundle recommendations.",
    )
    clear_uploads: bool = Field(
        default=False, description="Clear uploaded transaction/item data (Excel/CSV)."
    )
    clear_cache: bool = Field(
        default=True, description="Reset in-memory caches for mined rules."
    )


class MaintenanceActionResponse(BaseModel):
    """Response payload after a maintenance/clear operation."""

    tables_cleared: List[str] = Field(description="Tables that were cleared.")
    counts_before: Dict[str, int] = Field(
        description="Row counts before clearing for each affected table."
    )
    cache_cleared: bool = Field(description="Whether in-memory caches were reset.")
