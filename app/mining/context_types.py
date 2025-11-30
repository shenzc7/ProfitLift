from dataclasses import dataclass
from typing import Optional, Set, Dict, Any


@dataclass(frozen=True)
class Context:
    """
    Context dimensions for segmenting transactions.
    
    India-aware: Includes festival_period for Diwali, Holi, Eid, etc.
    """
    store_id: Optional[str] = None
    time_bin: Optional[str] = None  # morning, midday, afternoon, evening
    weekday_weekend: Optional[str] = None  # weekday, weekend
    quarter: Optional[int] = None  # Q1, Q2, Q3, Q4
    festival_period: Optional[str] = None  # diwali, holi, eid, christmas, navratri, etc.

    def __str__(self) -> str:
        """Human-readable context description."""
        parts = []
        if self.store_id:
            parts.append(f"Store {self.store_id}")
        if self.festival_period:
            # Festival takes priority in display
            parts.append(f"{self.festival_period.title()}")
        if self.time_bin:
            parts.append(f"{self.time_bin.title()}")
        if self.weekday_weekend:
            parts.append(f"{self.weekday_weekend.title()}")
        if self.quarter and not self.festival_period:
            # Don't show quarter if festival is shown
            parts.append(f"Q{self.quarter}")

        return " + ".join(parts) if parts else "Overall"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "store_id": self.store_id,
            "time_bin": self.time_bin,
            "weekday_weekend": self.weekday_weekend,
            "quarter": self.quarter,
            "festival_period": self.festival_period,
            "label": str(self)
        }


@dataclass
class ContextualRule:
    """Association rule with context information."""
    antecedent: frozenset
    consequent: frozenset
    support: float
    confidence: float
    lift: float
    context: Context

    # Additional fields for scoring
    profit_score: Optional[float] = None
    diversity_score: Optional[float] = None
    overall_score: Optional[float] = None

    def __str__(self) -> str:
        """Human-readable rule description."""
        ant_str = " + ".join(sorted(self.antecedent))
        cons_str = " + ".join(sorted(self.consequent))
        return f"{ant_str} → {cons_str} (context: {self.context})"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "antecedent": sorted(list(self.antecedent)),
            "consequent": sorted(list(self.consequent)),
            "support": self.support,
            "confidence": self.confidence,
            "lift": self.lift,
            "context": self.context.to_dict(),
            "profit_score": self.profit_score,
            "diversity_score": self.diversity_score,
            "overall_score": self.overall_score
        }
