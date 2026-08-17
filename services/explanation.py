"""
Explainable AI (XAI) Engine for Dynamic Pricing.
Generates human-readable, transparent reasoning and attribution breakdowns for every price recommendation.
"""

from typing import Dict, Any, List


class ExplainabilityEngine:
    """Produces natural language explanations and visual driver breakdowns for pricing decisions."""

    def generate_explanation(
        self,
        current_price: float,
        final_price: float,
        demand_score: float,
        demand_level: str,
        occupancy_rate: float,
        inventory_remaining: int,
        competitor_price: float,
        booking_velocity: float,
        days_remaining: int,
        is_weekend: int,
        season: str,
        customer_segment: str,
        is_capped: bool,
        cap_reason: str,
        factors: Dict[str, float],
        special_event: str = "Normal Day",
        event_multiplier: float = 1.0,
        price_sensitivity: float = None
    ) -> Dict[str, Any]:
        """
        Synthesizes all pricing drivers into an executive summary and granular bullet points.
        """
        price_diff = final_price - current_price
        pct_change = round((price_diff / max(current_price, 1)) * 100.0, 1)
        direction = "increased" if price_diff > 0 else ("decreased" if price_diff < 0 else "maintained")
        
        reasons: List[str] = []
        drivers: List[Dict[str, Any]] = []

        # 1. Demand driver
        if demand_score >= 70:
            reasons.append(f"high predicted demand ({demand_score:.1f}/100, level: {demand_level})")
            drivers.append({"driver": "Demand Pressure", "impact": "High Positive", "score": demand_score, "weight": "+35%"})
        elif demand_score <= 35:
            reasons.append(f"subdued demand forecast ({demand_score:.1f}/100, level: {demand_level})")
            drivers.append({"driver": "Demand Pressure", "impact": "Negative", "score": demand_score, "weight": "-20%"})
        else:
            drivers.append({"driver": "Demand Pressure", "impact": "Neutral", "score": demand_score, "weight": "±0%"})

        # 2. Inventory / Occupancy driver
        if occupancy_rate >= 0.80:
            reasons.append(f"tight inventory ({int(occupancy_rate*100)}% capacity utilized, only {inventory_remaining} remaining)")
            drivers.append({"driver": "Inventory Scarcity", "impact": "High Positive", "score": round(occupancy_rate*100, 1), "weight": "+25%"})
        elif occupancy_rate <= 0.30:
            reasons.append(f"excess capacity ({inventory_remaining} units unsold, {int(occupancy_rate*100)}% utilized)")
            drivers.append({"driver": "Inventory Surplus", "impact": "Discount Stimulus", "score": round(occupancy_rate*100, 1), "weight": "-25%"})
        else:
            drivers.append({"driver": "Inventory Balance", "impact": "Balanced", "score": round(occupancy_rate*100, 1), "weight": "Normal"})

        # 3. Competitor Benchmarking
        comp_diff_pct = round(((competitor_price - current_price) / max(current_price, 1)) * 100.0, 1)
        if comp_diff_pct > 3.0:
            reasons.append(f"competitor pricing is {comp_diff_pct:+.1f}% higher (₹{competitor_price:,.0f}) creating capture opportunity")
            drivers.append({"driver": "Competitor Benchmarking", "impact": "Positive", "score": competitor_price, "weight": f"{comp_diff_pct:+.1f}%"})
        elif comp_diff_pct < -3.0:
            reasons.append(f"competitor undercutting by {abs(comp_diff_pct):.1f}% (₹{competitor_price:,.0f}) requiring competitive alignment")
            drivers.append({"driver": "Competitor Benchmarking", "impact": "Negative", "score": competitor_price, "weight": f"{comp_diff_pct:+.1f}%"})
        else:
            drivers.append({"driver": "Competitor Benchmarking", "impact": "Parity", "score": competitor_price, "weight": "Parity"})

        # 4. Special Event driver
        if special_event and special_event != "Normal Day" and event_multiplier > 1.05:
            reasons.append(f"special event '{special_event}' surge ({event_multiplier:.2f}x multiplier)")
            drivers.append({"driver": f"Special Event ({special_event})", "impact": "High Positive", "score": event_multiplier, "weight": f"+{int((event_multiplier-1.0)*100)}%"})

        # 5. Customer Behaviour & Price Sensitivity driver
        if price_sensitivity is not None:
            if price_sensitivity <= 0.45:
                reasons.append(f"customer segment '{customer_segment}' exhibits low price sensitivity ({price_sensitivity})")
                drivers.append({"driver": "Customer Behaviour", "impact": "Inelastic Demand", "score": price_sensitivity, "weight": "Low Sensitivity"})
            elif price_sensitivity >= 1.3:
                reasons.append(f"customer segment '{customer_segment}' has high price sensitivity ({price_sensitivity})")
                drivers.append({"driver": "Customer Behaviour", "impact": "Elastic Demand", "score": price_sensitivity, "weight": "High Sensitivity"})

        # 6. Booking velocity
        if booking_velocity >= 5.0:
            reasons.append(f"accelerating booking velocity ({booking_velocity:.1f} orders/day)")
            drivers.append({"driver": "Velocity Momentum", "impact": "Positive", "score": booking_velocity, "weight": "+10%"})
        elif booking_velocity <= 1.0:
            reasons.append(f"sluggish sales velocity ({booking_velocity:.1f} orders/day)")
            drivers.append({"driver": "Velocity Drag", "impact": "Negative", "score": booking_velocity, "weight": "-8%"})

        # 7. Temporal / Seasonality
        if days_remaining <= 3:
            reasons.append(f"imminent expiry/departure ({days_remaining} days remaining)")
            drivers.append({"driver": "Urgency / Lead Time", "impact": "High Urgency", "score": days_remaining, "weight": "Urgent"})
        if is_weekend and special_event not in ["Weekend", "Concert", "Festival"]:
            reasons.append("weekend/holiday surge premium")
        if season in ["Peak", "Holiday", "Festive Sale", "Festival Surge", "Winter Peak"]:
            reasons.append(f"peak seasonal period ({season})")

        # Combine into cohesive natural language
        if abs(pct_change) < 0.5:
            summary = f"Recommended price maintained at ₹{final_price:,.0f}. Market conditions and competitor benchmark are in equilibrium."
        else:
            reason_text = ", ".join(reasons) if reasons else "market elasticity calibration"
            summary = f"Recommended price {direction} by {abs(pct_change):.1f}% (₹{current_price:,.0f} → ₹{final_price:,.0f}). Primary drivers: {reason_text}."

        if is_capped and cap_reason:
            summary += f" [Note: {cap_reason}]"

        return {
            "summary": summary,
            "direction": direction,
            "pct_change": pct_change,
            "reasons_list": reasons,
            "drivers": drivers,
            "guardrail_applied": is_capped,
            "guardrail_note": cap_reason if is_capped else "Operating within normal safety bounds"
        }


# Global instance
explainability_engine = ExplainabilityEngine()
