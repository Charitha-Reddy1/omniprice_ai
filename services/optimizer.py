"""
Pricing Optimizer Service.
Calculates optimal selling price and transparent revenue impact based on demand elasticity,
inventory scarcity, competitor benchmarking, urgency, and customer segment.
"""

import time
import numpy as np
from typing import Dict, Any


class PricingOptimizer:
    """Core mathematical optimization engine for dynamic pricing."""

    def __init__(self):
        # Elasticity defaults per customer segment
        self.elasticity_map = {
            "Budget": -1.6,
            "Bargain Hunter": -1.7,
            "Student Traveler": -1.5,
            "Standard": -1.1,
            "Leisure": -1.0,
            "Leisure Flyer": -1.0,
            "Prime Member": -0.8,
            "Loyal Customer": -0.7,
            "Family Group": -0.9,
            "Business": -0.4,
            "Corporate Traveler": -0.35,
            "Last-minute Rush": -0.25,
            "Honeymooners": -0.3,
            "Luxury": -0.2
        }

    def optimize_price(
        self,
        base_price: float,
        current_price: float,
        competitor_price: float,
        demand_score: float,
        inventory_remaining: int,
        total_capacity: int,
        days_remaining: int,
        booking_velocity: float,
        season_multiplier: float,
        customer_segment: str = "Standard",
        event_multiplier: float = 1.0,
        special_event: str = "Normal Day",
        price_sensitivity: float = None,
        conversion_rate: float = None
    ) -> Dict[str, Any]:
        """
        Calculates optimal price factor considering multiple business signals.
        Returns detailed decomposition for explainability and revenue projections.
        """
        start_t = time.perf_counter()

        # 1. Demand Factor (Baseline: 50 demand score is neutral 1.0)
        # Scores > 50 give upward pressure up to +35%; scores < 50 discount up to -25%
        demand_factor = 1.0 + ((demand_score - 50.0) / 100.0) * 0.45

        # 2. Inventory Scarcity Factor
        # As occupancy rises / inventory empties, willingness to extract premium increases
        occupancy_ratio = 1.0 - (inventory_remaining / max(total_capacity, 1))
        if occupancy_ratio >= 0.85:
            scarcity_factor = 1.0 + ((occupancy_ratio - 0.70) * 0.50)  # High scarcity boost
        elif occupancy_ratio <= 0.25:
            scarcity_factor = 1.0 - ((0.30 - occupancy_ratio) * 0.35)  # Surplus discount pressure
        else:
            scarcity_factor = 1.0 + (occupancy_ratio - 0.50) * 0.15

        # 3. Competitor Benchmarking Factor
        # If competitor is higher, we can comfortably capture consumer surplus without losing volume
        price_diff_ratio = (competitor_price - current_price) / max(current_price, 1)
        competitor_factor = 1.0 + (price_diff_ratio * 0.25)
        competitor_factor = np.clip(competitor_factor, 0.85, 1.25)

        # 4. Booking Velocity Factor
        # If velocity is high (e.g. > 4 bookings/day), momentum justifies capturing upside
        velocity_factor = 1.0 + ((booking_velocity - 2.5) / 10.0) * 0.12
        velocity_factor = np.clip(velocity_factor, 0.92, 1.15)

        # 5. Urgency / Time-decay Factor (Approaching deadline with high stock -> discount; low stock -> premium)
        if days_remaining <= 3:
            urgency_factor = 1.15 if occupancy_ratio > 0.75 else 0.90
        elif days_remaining <= 7:
            urgency_factor = 1.08 if occupancy_ratio > 0.60 else 0.95
        else:
            urgency_factor = 1.0

        # 6. Combined Raw Multiplier with Event & Temporal Effects
        temporal_event_multiplier = season_multiplier * event_multiplier * urgency_factor
        raw_multiplier = (
            demand_factor * 0.35
            + scarcity_factor * 0.25
            + competitor_factor * 0.20
            + temporal_event_multiplier * 0.12
            + velocity_factor * 0.08
        )

        # Apply multiplier to base price benchmark
        raw_recommended_price = base_price * raw_multiplier

        # 7. Revenue Simulation & Expected Conversion Rate
        if price_sensitivity is not None:
            elasticity = -float(price_sensitivity)
        else:
            elasticity = self.elasticity_map.get(customer_segment, -1.0)
        
        # Expected demand volume under current vs recommended
        # Price elasticity of demand: %ΔQ = ε * %ΔP
        price_change_pct = (raw_recommended_price - current_price) / max(current_price, 1)
        
        # Baseline conversion units at current price
        base_conversion_rate = np.clip(0.20 + (demand_score / 200.0), 0.05, 0.80)
        expected_demand_units_current = min(
            inventory_remaining,
            max(0.5, booking_velocity * base_conversion_rate * 3.0)
        )
        
        expected_demand_units_rec = min(
            inventory_remaining,
            max(0.2, expected_demand_units_current * (1.0 + (elasticity * price_change_pct)))
        )

        # Revenue estimates
        current_est_revenue = round(current_price * expected_demand_units_current, 2)
        rec_est_revenue = round(raw_recommended_price * expected_demand_units_rec, 2)
        rev_impact_pct = round(((rec_est_revenue - current_est_revenue) / max(current_est_revenue, 1)) * 100.0, 2)

        calc_latency_ms = round((time.perf_counter() - start_t) * 1000, 2)

        return {
            "raw_recommended_price": float(round(raw_recommended_price, 2)),
            "price_change_pct": round(price_change_pct * 100.0, 2),
            "expected_demand_units_current": round(float(expected_demand_units_current), 2),
            "expected_demand_units_recommended": round(float(expected_demand_units_rec), 2),
            "current_estimated_revenue": float(current_est_revenue),
            "recommended_estimated_revenue": float(rec_est_revenue),
            "estimated_revenue_impact_pct": float(rev_impact_pct),
            "factors": {
                "demand_factor": round(float(demand_factor), 3),
                "scarcity_factor": round(float(scarcity_factor), 3),
                "competitor_factor": round(float(competitor_factor), 3),
                "velocity_factor": round(float(velocity_factor), 3),
                "urgency_factor": round(float(urgency_factor), 3),
                "season_multiplier": round(float(season_multiplier), 3),
                "elasticity": float(elasticity)
            },
            "calc_latency_ms": calc_latency_ms
        }


# Global instance
pricing_optimizer = PricingOptimizer()
