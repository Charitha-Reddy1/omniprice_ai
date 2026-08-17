"""
Price Guardrails Service.
Enforces business safety constraints, preventing unrealistic swings, price gouging, or margin erosion.
"""

from typing import Dict, Any, Tuple


class PriceGuardrails:
    """Enforces safety bounds and policy limits on suggested prices."""

    def __init__(
        self,
        min_price_ratio: float = 0.65,      # Cannot drop below 65% of base price
        max_price_ratio: float = 1.65,      # Cannot exceed 165% of base price
        max_increase_pct: float = 0.20,     # Max single change +20%
        max_decrease_pct: float = 0.20,     # Max single change -20%
    ):
        self.min_price_ratio = min_price_ratio
        self.max_price_ratio = max_price_ratio
        self.max_increase_pct = max_increase_pct
        self.max_decrease_pct = max_decrease_pct

    def apply_guardrails(
        self,
        raw_recommended_price: float,
        current_price: float,
        base_price: float,
        custom_min: float = None,
        custom_max: float = None
    ) -> Dict[str, Any]:
        """
        Clamps the price within safe bounds and logs which constraint (if any) was triggered.
        """
        # Step 1: Base absolute bounds
        abs_min = custom_min if custom_min is not None else (base_price * self.min_price_ratio)
        abs_max = custom_max if custom_max is not None else (base_price * self.max_price_ratio)

        # Step 2: Step-change bounds relative to current price
        step_min = current_price * (1.0 - self.max_decrease_pct)
        step_max = current_price * (1.0 + self.max_increase_pct)

        effective_min = max(abs_min, step_min)
        effective_max = min(abs_max, step_max)

        final_price = raw_recommended_price
        is_capped = False
        cap_reason = None
        cap_type = "NONE"

        if raw_recommended_price > effective_max:
            final_price = effective_max
            is_capped = True
            if effective_max == step_max:
                cap_reason = f"Capped by +{int(self.max_increase_pct*100)}% maximum single-step increase safety limit"
                cap_type = "MAX_INCREASE_STEP"
            else:
                cap_reason = f"Capped by maximum business price ceiling (₹{abs_max:,.0f})"
                cap_type = "MAX_CEILING"

        elif raw_recommended_price < effective_min:
            final_price = effective_min
            is_capped = True
            if effective_min == step_min:
                cap_reason = f"Protected by -{int(self.max_decrease_pct*100)}% maximum single-step decrease floor"
                cap_type = "MAX_DECREASE_STEP"
            else:
                cap_reason = f"Protected by minimum margin floor (₹{abs_min:,.0f})"
                cap_type = "MIN_FLOOR"

        # Round sensibly to nearest 10 or 50
        if final_price > 5000:
            final_price = round(final_price, -1)
        else:
            final_price = round(final_price)

        return {
            "final_price": float(final_price),
            "raw_price": float(raw_recommended_price),
            "is_capped": is_capped,
            "cap_reason": cap_reason,
            "cap_type": cap_type,
            "effective_bounds": {
                "min": round(float(effective_min), 2),
                "max": round(float(effective_max), 2),
                "abs_min": round(float(abs_min), 2),
                "abs_max": round(float(abs_max), 2)
            }
        }


# Global guardrails instance
price_guardrails = PriceGuardrails()
