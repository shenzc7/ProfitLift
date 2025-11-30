"""
India Festival Calendar & GST Margin Utilities

Simple, presentation-ready utilities for Indian retail context.
"""

from datetime import date, datetime
from typing import Optional, Dict, List

# ============================================================
# FESTIVAL CALENDAR (Approximate dates - can be configured)
# ============================================================

# Festival windows: (month, start_day, end_day, name)
# These are approximate - festivals shift by lunar calendar each year
FESTIVAL_WINDOWS_2023 = {
    "makar_sankranti": [(1, 13, 16)],      # Jan 14
    "republic_day": [(1, 24, 28)],          # Jan 26
    "holi": [(3, 6, 10)],                   # March 8
    "eid_ul_fitr": [(4, 20, 24)],           # April 21-22
    "independence_day": [(8, 13, 17)],      # Aug 15
    "raksha_bandhan": [(8, 28, 31)],        # Aug 30
    "janmashtami": [(9, 5, 8)],             # Sep 6-7
    "ganesh_chaturthi": [(9, 18, 28)],      # Sep 19-28
    "navratri": [(10, 15, 24)],             # Oct 15-24
    "dussehra": [(10, 23, 26)],             # Oct 24
    "diwali": [(11, 10, 16)],               # Nov 12 (biggest retail week)
    "christmas": [(12, 23, 27)],            # Dec 25
    "new_year": [(12, 29, 31), (1, 1, 3)],  # Dec 31 - Jan 2
}

# Simplified: Major festivals only (for presentation)
MAJOR_FESTIVALS = ["diwali", "holi", "navratri", "eid_ul_fitr", "christmas", "new_year"]


def get_festival_period(dt: datetime) -> Optional[str]:
    """
    Detect if a date falls within a festival period.
    
    Returns festival name or None.
    
    Example:
        >>> get_festival_period(datetime(2023, 11, 12))
        'diwali'
    """
    if dt is None:
        return None
    
    month = dt.month
    day = dt.day
    
    for festival, windows in FESTIVAL_WINDOWS_2023.items():
        for window in windows:
            w_month, w_start, w_end = window
            if month == w_month and w_start <= day <= w_end:
                return festival
    
    return None


def is_festival_week(dt: datetime) -> bool:
    """Check if date is in any festival week."""
    return get_festival_period(dt) is not None


def get_major_festival(dt: datetime) -> Optional[str]:
    """Get festival only if it's a major one (Diwali, Holi, etc.)."""
    festival = get_festival_period(dt)
    if festival in MAJOR_FESTIVALS:
        return festival
    return None


# ============================================================
# GST MARGIN CALCULATOR (India-specific)
# ============================================================

# GST slabs by category (simplified)
GST_SLABS = {
    # 0% - Essentials
    "rice": 0.0,
    "wheat": 0.0,
    "atta": 0.0,
    "dal": 0.0,
    "vegetables": 0.0,
    "fruits": 0.0,
    "milk_fresh": 0.0,
    
    # 5% - Packaged foods
    "dairy": 0.05,
    "packaged_food": 0.05,
    "tea": 0.05,
    "coffee": 0.05,
    "spices": 0.05,
    "oil": 0.05,
    
    # 12% - Processed foods
    "processed_food": 0.12,
    "frozen_food": 0.12,
    "ready_to_eat": 0.12,
    "beverages": 0.12,
    
    # 18% - Premium / Non-food
    "electronics": 0.18,
    "cosmetics": 0.18,
    "personal_care": 0.18,
    "snacks_branded": 0.18,
    
    # 28% - Luxury
    "luxury": 0.28,
    "tobacco": 0.28,
}

DEFAULT_GST = 0.12  # Default to 12% if category unknown


def get_gst_rate(category: str) -> float:
    """
    Get GST rate for a product category.
    
    Args:
        category: Product category (case-insensitive)
    
    Returns:
        GST rate as decimal (0.0 to 0.28)
    """
    if not category:
        return DEFAULT_GST
    
    category_lower = category.lower().replace(" ", "_")
    
    # Direct match
    if category_lower in GST_SLABS:
        return GST_SLABS[category_lower]
    
    # Partial match
    for key, rate in GST_SLABS.items():
        if key in category_lower or category_lower in key:
            return rate
    
    return DEFAULT_GST


def calculate_margin_indian(
    mrp: float,
    purchase_price: float,
    category: Optional[str] = None,
    gst_rate: Optional[float] = None
) -> float:
    """
    Calculate profit margin the Indian way.
    
    Indian retailers think: "I bought at ₹80, sold at ₹100 MRP, what's my margin?"
    
    Formula:
        Net Selling Price = MRP / (1 + GST)
        Margin % = (Net Selling - Purchase) / Net Selling
    
    Args:
        mrp: Maximum Retail Price (inclusive of GST)
        purchase_price: What the retailer paid
        category: Product category (to lookup GST rate)
        gst_rate: Override GST rate (optional)
    
    Returns:
        Margin as decimal (0.0 to 1.0)
    
    Example:
        >>> calculate_margin_indian(100, 70, "dairy")
        0.265  # ~26.5% margin after accounting for 5% GST
    """
    if mrp <= 0:
        return 0.0
    
    if gst_rate is None:
        gst_rate = get_gst_rate(category) if category else DEFAULT_GST
    
    # Net selling price (excluding GST)
    net_selling = mrp / (1 + gst_rate)
    
    # Margin calculation
    if net_selling <= purchase_price:
        return 0.0
    
    margin = (net_selling - purchase_price) / net_selling
    return max(0.0, min(1.0, margin))


def estimate_margin_simple(price: float, category: Optional[str] = None) -> float:
    """
    Estimate margin when purchase price is unknown.
    
    Uses category-based defaults common in Indian retail.
    
    Args:
        price: Selling price (MRP)
        category: Product category
    
    Returns:
        Estimated margin as decimal
    """
    # Default margins by category (based on Indian retail norms)
    CATEGORY_MARGINS = {
        "dairy": 0.15,
        "produce": 0.30,
        "vegetables": 0.25,
        "fruits": 0.30,
        "grocery": 0.20,
        "packaged_food": 0.18,
        "beverages": 0.25,
        "snacks": 0.22,
        "personal_care": 0.28,
        "household": 0.20,
        "meat": 0.15,
        "bakery": 0.35,
        "prepared": 0.40,
    }
    
    DEFAULT_MARGIN = 0.22  # ~22% is common retail margin
    
    if not category:
        return DEFAULT_MARGIN
    
    category_lower = category.lower()
    
    for key, margin in CATEGORY_MARGINS.items():
        if key in category_lower or category_lower in key:
            return margin
    
    return DEFAULT_MARGIN


# ============================================================
# DATA VOLUME DETECTION (Sparse Data Handling)
# ============================================================

def detect_data_mode(transaction_count: int) -> Dict:
    """
    Detect appropriate mining parameters based on data volume.
    
    This enables ProfitLift to work for both:
    - Large supermarket chains (100k+ transactions)
    - Small kiranas (500-2000 transactions)
    
    Returns recommended settings.
    """
    if transaction_count >= 10000:
        # Large dataset - full context mining
        return {
            "mode": "full",
            "max_depth": 2,
            "min_support": 0.01,
            "min_confidence": 0.3,
            "min_rows_per_context": 100,
            "description": "Full context analysis with store × time combinations"
        }
    elif transaction_count >= 2000:
        # Medium dataset - single-dimension contexts only
        return {
            "mode": "standard",
            "max_depth": 1,
            "min_support": 0.02,
            "min_confidence": 0.25,
            "min_rows_per_context": 50,
            "description": "Standard analysis with single context dimensions"
        }
    elif transaction_count >= 500:
        # Small dataset - limited context mining
        return {
            "mode": "compact",
            "max_depth": 1,
            "min_support": 0.05,
            "min_confidence": 0.2,
            "min_rows_per_context": 30,
            "description": "Compact analysis optimized for smaller data"
        }
    else:
        # Very small - overall patterns only
        return {
            "mode": "minimal",
            "max_depth": 0,
            "min_support": 0.08,
            "min_confidence": 0.15,
            "min_rows_per_context": 10,
            "description": "Basic patterns from overall data (limited context)"
        }







