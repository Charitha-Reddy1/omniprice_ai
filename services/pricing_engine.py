"""
Core Common Dynamic Pricing Engine.
Orchestrates the end-to-end pricing pipeline across all 4 domains without logic duplication.
Pipeline: Validation -> Adapter -> Demand ML -> Competition -> Inventory -> Optimizer -> Guardrails -> XAI -> Display
"""

import time
from typing import Dict, Any
from services.demand_predictor import demand_predictor
from services.optimizer import pricing_optimizer
from services.guardrails import price_guardrails
from services.explanation import explainability_engine
from adapters.domain_adapters import get_adapter


class DynamicPricingEngine:
    """Unified, domain-agnostic dynamic pricing engine."""

    def __init__(self):
        self.demand_predictor = demand_predictor
        self.optimizer = pricing_optimizer
        self.guardrails = price_guardrails
        self.explainer = explainability_engine

    def calculate_price(
        self,
        domain_data: Dict[str, Any],
        domain: str = "hotel",
        custom_guardrails: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """
        Calculates optimal price for ANY domain (Hotel, Product, Flight, Travel Package).
        """
        overall_start = time.perf_counter()

        # Step 1: Normalize through domain adapter
        adapter = get_adapter(domain)
        norm = adapter.normalize(domain_data)

        # Step 2: Demand Prediction via trained ML pipeline
        demand_res = self.demand_predictor.predict_demand(norm)
        demand_score = demand_res["demand_score"]
        demand_level = demand_res["demand_level"]
        confidence_score = demand_res["confidence_score"]
        ml_latency_ms = demand_res["prediction_latency_ms"]

        # Step 3: Mathematical Optimization (Elasticity, Scarcity, Competitor, Urgency, Event, Behaviour)
        opt_res = self.optimizer.optimize_price(
            base_price=norm["base_price"],
            current_price=norm["current_price"],
            competitor_price=norm["competitor_price"],
            demand_score=demand_score,
            inventory_remaining=norm["inventory_remaining"],
            total_capacity=norm["total_capacity"],
            days_remaining=norm["days_remaining"],
            booking_velocity=norm["booking_velocity"],
            season_multiplier=norm["season_multiplier"],
            customer_segment=norm["customer_segment"],
            event_multiplier=norm.get("event_multiplier", 1.0),
            special_event=norm.get("special_event", "Normal Day"),
            price_sensitivity=norm.get("price_sensitivity", None),
            conversion_rate=norm.get("conversion_rate", None)
        )

        raw_rec_price = opt_res["raw_recommended_price"]

        # Step 4: Apply Price Safety Guardrails (Business constraints)
        c_min = custom_guardrails.get("min_price") if custom_guardrails else None
        c_max = custom_guardrails.get("max_price") if custom_guardrails else None
        
        guard_res = self.guardrails.apply_guardrails(
            raw_recommended_price=raw_rec_price,
            current_price=norm["current_price"],
            base_price=norm["base_price"],
            custom_min=c_min,
            custom_max=c_max
        )

        final_recommended_price = guard_res["final_price"]
        is_capped = guard_res["is_capped"]
        cap_reason = guard_res["cap_reason"]

        # Step 5: Recalculate transparent revenue impact with guardrail-constrained final price
        price_diff = final_recommended_price - norm["current_price"]
        pct_change = round((price_diff / max(norm["current_price"], 1)) * 100.0, 2)
        
        elasticity = opt_res["factors"]["elasticity"]
        expected_demand_current = opt_res["expected_demand_units_current"]
        expected_demand_rec = min(
            norm["inventory_remaining"],
            max(0.1, expected_demand_current * (1.0 + (elasticity * (pct_change / 100.0))))
        )
        
        est_curr_rev = round(norm["current_price"] * expected_demand_current, 2)
        est_rec_rev = round(final_recommended_price * expected_demand_rec, 2)
        est_rev_delta = round(est_rec_rev - est_curr_rev, 2)
        est_rev_delta_pct = round((est_rev_delta / max(est_curr_rev, 1)) * 100.0, 2)

        # Step 6: Generate Explainable AI reasoning
        explanation = self.explainer.generate_explanation(
            current_price=norm["current_price"],
            final_price=final_recommended_price,
            demand_score=demand_score,
            demand_level=demand_level,
            occupancy_rate=norm["occupancy_rate"],
            inventory_remaining=norm["inventory_remaining"],
            competitor_price=norm["competitor_price"],
            booking_velocity=norm["booking_velocity"],
            days_remaining=norm["days_remaining"],
            is_weekend=norm["is_weekend"],
            season=norm["season"],
            customer_segment=norm["customer_segment"],
            is_capped=is_capped,
            cap_reason=cap_reason,
            factors=opt_res["factors"],
            special_event=norm.get("special_event", "Normal Day"),
            event_multiplier=norm.get("event_multiplier", 1.0),
            price_sensitivity=norm.get("price_sensitivity", None)
        )

        total_latency_ms = round((time.perf_counter() - overall_start) * 1000, 2)

        # Step 7: Assemble complete decision object
        decision = {
            "domain": norm["domain"],
            "item_id": norm["item_id"],
            "item_name": norm["item_name"],
            "sub_type": norm["sub_type"],
            "base_price": norm["base_price"],
            "current_price": norm["current_price"],
            "competitor_price": norm["competitor_price"],
            "recommended_price": final_recommended_price,
            "raw_optimizer_price": raw_rec_price,
            "price_difference": round(price_diff, 2),
            "price_change_pct": pct_change,
            
            # Demand & Confidence
            "demand_score": demand_score,
            "demand_level": demand_level,
            "confidence_score": confidence_score,
            
            # Inventory & Velocity
            "inventory_remaining": norm["inventory_remaining"],
            "total_capacity": norm["total_capacity"],
            "occupancy_rate": round(norm["occupancy_rate"], 3),
            "days_remaining": norm["days_remaining"],
            "booking_velocity": norm["booking_velocity"],
            "customer_segment": norm["customer_segment"],
            "price_sensitivity": norm.get("price_sensitivity", 0.9),
            "purchase_frequency": norm.get("purchase_frequency", 2.5),
            "conversion_rate": norm.get("conversion_rate", 0.35),
            "season": norm["season"],
            "special_event": norm.get("special_event", "Normal Day"),
            "event_multiplier": norm.get("event_multiplier", 1.0),
            "is_weekend": norm["is_weekend"],
            "season": norm["season"],
            "is_weekend": norm["is_weekend"],
            
            # Revenue Impact
            "expected_demand_units_current": round(expected_demand_current, 2),
            "expected_demand_units_recommended": round(expected_demand_rec, 2),
            "current_estimated_revenue": est_curr_rev,
            "recommended_estimated_revenue": est_rec_rev,
            "estimated_revenue_delta": est_rev_delta,
            "estimated_revenue_impact_pct": est_rev_delta_pct,
            
            # Guardrails
            "guardrail_status": {
                "is_capped": is_capped,
                "cap_reason": cap_reason,
                "cap_type": guard_res["cap_type"],
                "bounds": guard_res["effective_bounds"]
            },
            
            # Explainability
            "explanation": explanation,
            
            # Telemetry & Performance
            "telemetry": {
                "ml_prediction_ms": ml_latency_ms,
                "optimization_ms": opt_res["calc_latency_ms"],
                "total_decision_latency_ms": total_latency_ms,
                "model_status": "Loaded" if self.demand_predictor.is_loaded else "Fallback"
            },
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        }

        # Step 8: Apply domain presentation formatting
        return adapter.format_display(decision)


# Global Engine Instance
pricing_engine = DynamicPricingEngine()
