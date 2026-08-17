"""
Base Domain Adapter.
Standardizes domain-specific business entities into the normalized schema expected by the Dynamic Pricing Engine.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseDomainAdapter(ABC):
    """Abstract adapter ensuring seamless reusability across all 4 business domains."""

    def __init__(self, domain_name: str, currency_symbol: str = "₹"):
        self.domain_name = domain_name
        self.currency_symbol = currency_symbol

    @abstractmethod
    def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert domain-specific dictionary into the normalized pricing engine schema:
        {
            "domain": str,
            "item_id": str,
            "item_name": str,
            "sub_type": str,
            "base_price": float,
            "current_price": float,
            "competitor_price": float,
            "inventory_remaining": int,
            "total_capacity": int,
            "occupancy_rate": float,
            "days_remaining": int,
            "is_weekend": int,
            "season": str,
            "season_multiplier": float,
            "customer_segment": str,
            "booking_velocity": float
        }
        """
        pass

    @abstractmethod
    def format_display(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Format common pricing engine output into domain-specific display attributes."""
        pass
