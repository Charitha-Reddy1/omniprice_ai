"""
System Monitoring, Telemetry, Alerting, and Human Override Decision Log Service.
Tracks latency, health statuses, alert rules, and audit trails of approved/overridden pricing.
"""

import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from typing import Dict, Any, List


class MonitoringService:
    """Central monitoring, telemetry, alerting, and decision persistence."""

    def __init__(self):
        self.start_time = time.time()
        self.decision_count = 0
        self.overrides_count = 0
        self.failed_requests_count = 0
        self.latency_history: List[float] = []
        self.recent_decisions: List[Dict[str, Any]] = []
        self.active_alerts: List[Dict[str, Any]] = []
        self.audit_log: List[Dict[str, Any]] = []

    def record_decision(self, decision: Dict[str, Any]):
        """Record a completed pricing calculation in telemetry and check alert rules."""
        self.decision_count += 1
        total_lat = decision.get("telemetry", {}).get("total_decision_latency_ms", 5.0)
        self.latency_history.append(total_lat)
        if len(self.latency_history) > 100:
            self.latency_history.pop(0)

        # Store recent decision
        self.recent_decisions.insert(0, decision)
        if len(self.recent_decisions) > 50:
            self.recent_decisions.pop()

        # Run alert evaluations
        self._evaluate_alerts(decision)

    def _evaluate_alerts(self, decision: Dict[str, Any]):
        """Evaluate real-time alert rules."""
        domain = decision.get("domain", "general")
        item_name = decision.get("item_name", "Item")
        demand_score = decision.get("demand_score", 50)
        occupancy = decision.get("occupancy_rate", 0.5)
        inventory = decision.get("inventory_remaining", 10)
        confidence = decision.get("confidence_score", 0.9)
        is_capped = decision.get("guardrail_status", {}).get("is_capped", False)

        now_utc = datetime.now(timezone.utc)
        now_ist = now_utc.astimezone(ZoneInfo("Asia/Kolkata"))
        now_str = now_ist.strftime("%I:%M:%S %p IST")

        # Low Inventory Alert
        if occupancy >= 0.85 or inventory <= 3:
            self._add_alert("WARNING", f"Low Inventory Alert: {item_name} has only {inventory} units remaining ({int(occupancy*100)}% capacity).", now_str)

        # Demand Spike Alert
        if demand_score >= 85:
            self._add_alert("INFO", f"Demand Spike Detected: {item_name} demand score surged to {demand_score:.1f}/100.", now_str)

        # Low Confidence Alert
        if confidence < 0.72:
            self._add_alert("WARNING", f"Model Confidence Low: {item_name} prediction confidence at {int(confidence*100)}%.", now_str)

        # Guardrail Safety Cap Alert
        if is_capped:
            reason = decision.get("guardrail_status", {}).get("cap_reason", "Safety limit")
            self._add_alert("INFO", f"Price Guardrail Enforced for {item_name}: {reason}", now_str)

    def _add_alert(self, level: str, message: str, timestamp: str):
        # Avoid duplicate consecutive alerts
        for existing in self.active_alerts[:5]:
            if existing["message"] == message:
                return
        self.active_alerts.insert(0, {
            "level": level,
            "message": message,
            "timestamp": timestamp
        })
        if len(self.active_alerts) > 15:
            self.active_alerts.pop()

    def record_override(
        self,
        domain: str,
        item_id: str,
        item_name: str,
        current_price: float,
        recommended_price: float,
        final_price: float,
        action: str,  # 'ACCEPT', 'REJECT', 'OVERRIDE'
        reason: str = "Manager confirmation",
        manager_id: str = "Pricing_Admin"
    ) -> Dict[str, Any]:
        """Record a human manager's review, approval, or override."""
        self.overrides_count += 1
        now_utc = datetime.now(timezone.utc)
        now_ist = now_utc.astimezone(ZoneInfo("Asia/Kolkata"))
        record = {
            "id": f"AUDIT-{len(self.audit_log)+1:04d}",
            "timestamp": now_utc.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "timestamp_ist": now_ist.strftime("%I:%M:%S %p"),
            "domain": domain,
            "item_id": item_id,
            "item_name": item_name,
            "current_price": current_price,
            "recommended_price": recommended_price,
            "final_price": final_price,
            "action": action.upper(),
            "reason": reason,
            "manager_id": manager_id
        }
        self.audit_log.insert(0, record)
        if len(self.audit_log) > 100:
            self.audit_log.pop()
        return record

    def get_system_health(self) -> Dict[str, Any]:
        """Calculates system health and key telemetry metrics."""
        uptime_sec = round(time.time() - self.start_time, 1)
        avg_latency = round(sum(self.latency_history) / max(len(self.latency_history), 1), 2)
        
        has_errors = self.failed_requests_count > 0
        has_warnings = any(a["level"] == "WARNING" for a in self.active_alerts[:5])

        if has_errors:
            status = "✕ Error"
            status_class = "error"
        elif has_warnings:
            status = "⚠ Warning"
            status_class = "warning"
        else:
            status = "● System Healthy"
            status_class = "healthy"

        return {
            "status": status,
            "status_class": status_class,
            "uptime_seconds": uptime_sec,
            "total_decisions": self.decision_count,
            "total_human_overrides": self.overrides_count,
            "failed_requests": self.failed_requests_count,
            "avg_latency_ms": avg_latency,
            "active_alerts": self.active_alerts[:6],
            "audit_log": self.audit_log[:10],
            "data_freshness": "Real-time stream (< 1s)",
            "data_source_mode": "SIMULATED REAL-TIME DATA"
        }


# Global monitoring instance
monitoring_service = MonitoringService()
