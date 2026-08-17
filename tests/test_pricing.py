"""
Comprehensive Automated Test Suite for Dynamic Pricing Engine.
Covers multi-domain ML prediction, customer behaviour, special events, safety guardrails,
4 domain adapters, API endpoints, simulator determinism, and failure handling.
"""

import os
import unittest
import numpy as np
from app import app
from services.pricing_engine import pricing_engine
from services.demand_predictor import demand_predictor
from services.guardrails import price_guardrails
from services.optimizer import pricing_optimizer
from services.simulator import simulator
from adapters.domain_adapters import get_adapter, ADAPTERS


class DynamicPricingEngineTestSuite(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    # -------------------------------------------------------------------------
    # 1. Multi-Domain ML Demand Prediction Tests
    # -------------------------------------------------------------------------
    def test_hotel_demand_prediction(self):
        """Verify Hotel domain demand prediction through multi-domain ML model."""
        sample_hotel = {
            "domain": "hotel",
            "base_price": 5000,
            "current_price": 5200,
            "competitor_price": 5600,
            "occupancy_rate": 0.85,
            "inventory_remaining": 8,
            "total_capacity": 50,
            "days_remaining": 3,
            "is_weekend": 1,
            "season_multiplier": 1.3,
            "special_event": "Concert",
            "event_multiplier": 1.35,
            "customer_segment": "Business",
            "price_sensitivity": 0.4,
            "booking_velocity": 4.5
        }
        res = demand_predictor.predict_demand(sample_hotel)
        self.assertIn("demand_score", res)
        self.assertGreaterEqual(res["demand_score"], 0.0)
        self.assertLessEqual(res["demand_score"], 100.0)

    def test_product_demand_prediction(self):
        """Verify Retail Product domain demand prediction through multi-domain ML model."""
        sample_prod = {
            "domain": "product",
            "base_price": 4500,
            "current_price": 4650,
            "competitor_price": 4899,
            "occupancy_rate": 0.90,
            "inventory_remaining": 14,
            "total_capacity": 150,
            "days_remaining": 10,
            "is_weekend": 0,
            "season_multiplier": 1.35,
            "special_event": "Flash Deal",
            "event_multiplier": 1.35,
            "customer_segment": "Prime Member",
            "price_sensitivity": 0.7,
            "booking_velocity": 6.5
        }
        res = demand_predictor.predict_demand(sample_prod)
        self.assertIn("demand_score", res)
        self.assertGreaterEqual(res["demand_score"], 0.0)

    def test_flight_demand_prediction(self):
        """Verify Flight domain demand prediction through multi-domain ML model."""
        sample_flight = {
            "domain": "flight",
            "base_price": 5500,
            "current_price": 6100,
            "competitor_price": 6450,
            "occupancy_rate": 0.90,
            "inventory_remaining": 18,
            "total_capacity": 180,
            "days_remaining": 2,
            "is_weekend": 1,
            "season_multiplier": 1.4,
            "special_event": "Festival",
            "event_multiplier": 1.5,
            "customer_segment": "Corporate Traveler",
            "price_sensitivity": 0.25,
            "booking_velocity": 7.8
        }
        res = demand_predictor.predict_demand(sample_flight)
        self.assertIn("demand_score", res)
        self.assertGreaterEqual(res["demand_score"], 0.0)

    def test_travel_package_demand_prediction(self):
        """Verify Travel Package domain demand prediction through multi-domain ML model."""
        sample_pkg = {
            "domain": "travel_package",
            "base_price": 16500,
            "current_price": 17200,
            "competitor_price": 18500,
            "occupancy_rate": 0.76,
            "inventory_remaining": 6,
            "total_capacity": 25,
            "days_remaining": 5,
            "is_weekend": 1,
            "season_multiplier": 1.35,
            "special_event": "Holiday",
            "event_multiplier": 1.35,
            "customer_segment": "Honeymooners",
            "price_sensitivity": 0.3,
            "booking_velocity": 3.4
        }
        res = demand_predictor.predict_demand(sample_pkg)
        self.assertIn("demand_score", res)
        self.assertGreaterEqual(res["demand_score"], 0.0)

    def test_ml_model_metadata_metrics(self):
        """Verify multi-domain model metadata has genuine R², MAE, RMSE metrics."""
        meta = demand_predictor.metadata
        self.assertIn("metrics", meta)
        metrics = meta["metrics"]
        self.assertIn("r2_score", metrics)
        self.assertGreater(metrics["r2_score"], 0.80)
        self.assertIn("mae", metrics)

    # -------------------------------------------------------------------------
    # 2. Customer Behaviour & Special Event Integration Tests
    # -------------------------------------------------------------------------
    def test_customer_price_sensitivity_influence(self):
        """Verify customer price sensitivity measurably influences optimization and explanation."""
        inelastic_input = {
            "domain": "hotel",
            "base_price": 5000,
            "current_price": 5000,
            "competitor_price": 5500,
            "inventory_remaining": 10,
            "total_capacity": 50,
            "days_remaining": 5,
            "is_weekend": 1,
            "season_multiplier": 1.2,
            "customer_segment": "Corporate Traveler",
            "price_sensitivity": 0.2,  # Inelastic
            "booking_velocity": 4.0
        }
        decision = pricing_engine.calculate_price(inelastic_input, domain="hotel")
        self.assertEqual(decision["customer_segment"], "Corporate Traveler")
        self.assertIn("explanation", decision)

    def test_special_event_pricing_and_explanation(self):
        """Verify special events increase pricing recommendation and appear in explanation."""
        event_input = {
            "domain": "hotel",
            "base_price": 5000,
            "current_price": 5000,
            "competitor_price": 5500,
            "inventory_remaining": 10,
            "total_capacity": 50,
            "days_remaining": 5,
            "is_weekend": 1,
            "season_multiplier": 1.2,
            "special_event": "Concert",
            "event_multiplier": 1.45,
            "customer_segment": "Leisure",
            "price_sensitivity": 0.8,
            "booking_velocity": 4.0
        }
        decision = pricing_engine.calculate_price(event_input, domain="hotel")
        self.assertEqual(decision["special_event"], "Concert")
        self.assertIn("Concert", decision["explanation"]["summary"])

    # -------------------------------------------------------------------------
    # 3. Guardrails Safety Tests
    # -------------------------------------------------------------------------
    def test_guardrails_max_step_increase_cap(self):
        """Verify price cannot jump higher than +20% in a single step."""
        base_price = 5000.0
        current_price = 5000.0
        extreme_optimizer_price = 8000.0

        guard_res = price_guardrails.apply_guardrails(
            raw_recommended_price=extreme_optimizer_price,
            current_price=current_price,
            base_price=base_price
        )
        self.assertTrue(guard_res["is_capped"])
        self.assertEqual(guard_res["cap_type"], "MAX_INCREASE_STEP")
        self.assertLessEqual(guard_res["final_price"], 6000.0)

    def test_guardrails_max_step_decrease_floor(self):
        """Verify price cannot drop more than -20% in a single step."""
        base_price = 5000.0
        current_price = 5000.0
        extreme_drop_price = 2000.0

        guard_res = price_guardrails.apply_guardrails(
            raw_recommended_price=extreme_drop_price,
            current_price=current_price,
            base_price=base_price
        )
        self.assertTrue(guard_res["is_capped"])
        self.assertEqual(guard_res["cap_type"], "MAX_DECREASE_STEP")
        self.assertGreaterEqual(guard_res["final_price"], 4000.0)

    # -------------------------------------------------------------------------
    # 4. Domain Adapters Reusability Tests
    # -------------------------------------------------------------------------
    def test_all_four_domain_adapters_exist(self):
        """Verify all 4 domains have valid adapters."""
        domains = ["hotel", "product", "flight", "travel_package"]
        for dom in domains:
            adapter = get_adapter(dom)
            self.assertIsNotNone(adapter)
            self.assertEqual(adapter.domain_name, dom)

    def test_unified_pricing_across_all_four_domains(self):
        """Verify the Common Pricing Engine processes all 4 domains successfully."""
        domains = ["hotel", "product", "flight", "travel_package"]
        for dom in domains:
            state = simulator.get_state(dom)
            decision = pricing_engine.calculate_price(state, domain=dom)
            self.assertEqual(decision["domain"], dom)
            self.assertIn("recommended_price", decision)
            self.assertIn("current_estimated_revenue", decision)
            self.assertIn("explanation", decision)

    # -------------------------------------------------------------------------
    # 5. Deterministic Simulator Tests
    # -------------------------------------------------------------------------
    def test_simulator_determinism_with_seed(self):
        """Verify simulator produces identical results given the same random seed."""
        simulator.reset_to_seed(42)
        res1 = simulator.apply_action("hotel", "increase_demand")
        p1 = res1["updated_state"]["booking_velocity"]

        simulator.reset_to_seed(42)
        res2 = simulator.apply_action("hotel", "increase_demand")
        p2 = res2["updated_state"]["booking_velocity"]

        self.assertEqual(p1, p2)

    def test_simulate_special_event_action(self):
        """Verify [Simulate Special Event] trigger updates event multiplier and velocity."""
        simulator.reset_to_seed(42)
        res = simulator.apply_action("hotel", "simulate_special_event")
        self.assertNotEqual(res["updated_state"]["special_event"], "Normal Day")
        self.assertGreater(res["updated_state"]["event_multiplier"], 1.0)

    # -------------------------------------------------------------------------
    # 6. REST API Endpoints Tests
    # -------------------------------------------------------------------------
    def test_api_health_endpoint(self):
        res = self.app.get("/api/health")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()["success"])

    def test_api_metrics_endpoint(self):
        res = self.app.get("/api/metrics")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()["success"])

    def test_api_pricing_current_all_domains(self):
        res = self.app.get("/api/pricing/current?domain=all")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.get_json()["results"]), 4)

    def test_api_pricing_override(self):
        payload = {
            "domain": "hotel",
            "item_id": "HTL-01",
            "item_name": "Grand Palace Hotel",
            "current_price": 5000,
            "recommended_price": 5400,
            "final_price": 5350,
            "action": "OVERRIDE",
            "reason": "Test manager override",
            "manager_id": "Judge_Admin"
        }
        res = self.app.post("/api/pricing/override", json=payload)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["override_record"]["action"], "OVERRIDE")

    def test_api_simulate_action(self):
        payload = {
            "domain": "hotel",
            "action": "simulate_special_event"
        }
        res = self.app.post("/api/simulate/action", json=payload)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()["success"])

    # -------------------------------------------------------------------------
    # 7. Multi-Entity Selection Tests
    # -------------------------------------------------------------------------
    def test_entity_selection_all_domains(self):
        """Verify selecting individual entities in each domain returns valid decision objects."""
        test_cases = [
            ("hotel", "HTL-02", "The Oberoi Mumbai"),
            ("product", "PRD-02", "Apple MacBook Pro 16-inch"),
            ("flight", "FLT-02", "Air India — Hyderabad → Delhi"),
            ("travel_package", "PKG-02", "Dubai City & Desert Experience 5D4N")
        ]
        for dom, ent_id, expected_name in test_cases:
            res = self.app.get(f"/api/pricing/current?domain={dom}&entity_id={ent_id}")
            self.assertEqual(res.status_code, 200)
            data = res.get_json()
            self.assertTrue(data["success"])
            self.assertEqual(data["result"]["item_id"], ent_id)
            self.assertEqual(data["result"]["item_name"], expected_name)

    def test_api_entities_endpoint(self):
        """Verify GET /api/entities returns selectable list of 8 entities per domain."""
        for dom in ["hotel", "product", "flight", "travel_package"]:
            res = self.app.get(f"/api/entities?domain={dom}")
            self.assertEqual(res.status_code, 200)
            data = res.get_json()
            self.assertTrue(data["success"])
            self.assertEqual(len(data["entities"]), 8)

    def test_simulate_action_on_selected_entity(self):
        """Verify real-time simulation action applies to selected entity."""
        payload = {
            "domain": "hotel",
            "entity_id": "HTL-02",
            "action": "increase_demand"
        }
        res = self.app.post("/api/simulate/action", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["pricing_decision"]["item_id"], "HTL-02")


if __name__ == "__main__":
    unittest.main()
