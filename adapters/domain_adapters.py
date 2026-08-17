"""
Domain Adapters for Hotel, Product, Flight, and Travel Package domains.
Normalizes domain data into the Common Pricing Engine schema and adds domain-specific metadata.
"""

from typing import Dict, Any
from adapters.base_adapter import BaseDomainAdapter


class HotelAdapter(BaseDomainAdapter):
    """Adapter for Hotel Room bookings."""

    def __init__(self):
        super().__init__(domain_name="hotel", currency_symbol="₹")

    def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        total_rooms = int(raw_data.get("total_rooms", raw_data.get("total_capacity", 50)))
        avail_rooms = int(raw_data.get("available_rooms", raw_data.get("inventory_remaining", 10)))
        occ = float(raw_data.get("occupancy_rate", (total_rooms - avail_rooms) / max(total_rooms, 1)))

        return {
            "domain": "hotel",
            "item_id": str(raw_data.get("item_id", "HTL-01")),
            "item_name": str(raw_data.get("hotel_name", raw_data.get("item_name", "Taj Mahal Palace"))),
            "sub_type": str(raw_data.get("room_type", raw_data.get("sub_type", "Deluxe Sea View Room"))),
            "base_price": float(raw_data.get("base_price", 5000)),
            "current_price": float(raw_data.get("current_price", 5000)),
            "competitor_price": float(raw_data.get("competitor_price", 5200)),
            "inventory_remaining": avail_rooms,
            "total_capacity": total_rooms,
            "inventory_ratio": round(float(avail_rooms / max(total_rooms, 1)), 3),
            "occupancy_rate": occ,
            "days_remaining": int(raw_data.get("days_until_checkin", raw_data.get("days_remaining", 3))),
            "is_weekend": int(raw_data.get("is_weekend", 1)),
            "season": str(raw_data.get("season", "Peak")),
            "season_multiplier": float(raw_data.get("season_multiplier", 1.25)),
            "special_event": str(raw_data.get("special_event", "Normal Day")),
            "event_multiplier": float(raw_data.get("event_multiplier", 1.0)),
            "customer_segment": str(raw_data.get("customer_segment", "Leisure")),
            "price_sensitivity": float(raw_data.get("price_sensitivity", 0.9)),
            "purchase_frequency": float(raw_data.get("purchase_frequency", 2.5)),
            "conversion_rate": float(raw_data.get("conversion_rate", 0.35)),
            "booking_velocity": float(raw_data.get("booking_velocity", 3.5))
        }

    def format_display(self, result: Dict[str, Any]) -> Dict[str, Any]:
        res = result.copy()
        res["domain_label"] = "Hotel Room"
        res["inventory_label"] = f"{res['inventory_remaining']} rooms left ({int(res['occupancy_rate']*100)}% booked)"
        res["unit_label"] = "per night"
        res["lead_time_label"] = f"{res['days_remaining']} days to check-in"
        return res


class ProductAdapter(BaseDomainAdapter):
    """Adapter for Retail Products."""

    def __init__(self):
        super().__init__(domain_name="product", currency_symbol="₹")

    def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        total_stock = int(raw_data.get("max_stock", raw_data.get("total_capacity", 100)))
        stock_remaining = int(raw_data.get("inventory", raw_data.get("inventory_remaining", 15)))
        occ = float(raw_data.get("occupancy_rate", 1.0 - (stock_remaining / max(total_stock, 1))))

        return {
            "domain": "product",
            "item_id": str(raw_data.get("item_id", "PRD-01")),
            "item_name": str(raw_data.get("product_name", raw_data.get("item_name", "Sony WH-1000XM5 Headphones"))),
            "sub_type": str(raw_data.get("category", raw_data.get("sub_type", "Electronics"))),
            "base_price": float(raw_data.get("base_price", 2500)),
            "current_price": float(raw_data.get("current_price", 2500)),
            "competitor_price": float(raw_data.get("competitor_price", 2650)),
            "inventory_remaining": stock_remaining,
            "total_capacity": total_stock,
            "inventory_ratio": round(float(stock_remaining / max(total_stock, 1)), 3),
            "occupancy_rate": occ,
            "days_remaining": int(raw_data.get("days_to_restock", raw_data.get("days_remaining", 14))),
            "is_weekend": int(raw_data.get("is_promo", raw_data.get("is_weekend", 0))),
            "season": str(raw_data.get("season", "Festive Sale")),
            "season_multiplier": float(raw_data.get("season_multiplier", 1.2)),
            "special_event": str(raw_data.get("special_event", "Normal Day")),
            "event_multiplier": float(raw_data.get("event_multiplier", 1.0)),
            "customer_segment": str(raw_data.get("customer_segment", "Prime Member")),
            "price_sensitivity": float(raw_data.get("price_sensitivity", 0.7)),
            "purchase_frequency": float(raw_data.get("purchase_frequency", 4.0)),
            "conversion_rate": float(raw_data.get("conversion_rate", 0.40)),
            "booking_velocity": float(raw_data.get("sales_velocity", raw_data.get("booking_velocity", 4.0)))
        }

    def format_display(self, result: Dict[str, Any]) -> Dict[str, Any]:
        res = result.copy()
        res["domain_label"] = "Retail Product"
        res["inventory_label"] = f"{res['inventory_remaining']} items in stock"
        res["unit_label"] = "per unit"
        res["lead_time_label"] = f"Restock in {res['days_remaining']} days"
        return res


class FlightAdapter(BaseDomainAdapter):
    """Adapter for Airline Tickets."""

    def __init__(self):
        super().__init__(domain_name="flight", currency_symbol="₹")

    def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        capacity = int(raw_data.get("seat_capacity", raw_data.get("total_capacity", 180)))
        seats_left = int(raw_data.get("seats_remaining", raw_data.get("inventory_remaining", 24)))
        load_factor = float(raw_data.get("load_factor", raw_data.get("occupancy_rate", (capacity - seats_left) / max(capacity, 1))))

        return {
            "domain": "flight",
            "item_id": str(raw_data.get("item_id", "FLT-01")),
            "item_name": str(raw_data.get("airline_flight", raw_data.get("item_name", "IndiGo — Delhi → Mumbai"))),
            "sub_type": str(raw_data.get("route", raw_data.get("sub_type", "DEL → BOM"))),
            "base_price": float(raw_data.get("base_fare", raw_data.get("base_price", 5500))),
            "current_price": float(raw_data.get("current_price", 5500)),
            "competitor_price": float(raw_data.get("competitor_fare", raw_data.get("competitor_price", 5900))),
            "inventory_remaining": seats_left,
            "total_capacity": capacity,
            "inventory_ratio": round(float(seats_left / max(capacity, 1)), 3),
            "occupancy_rate": load_factor,
            "days_remaining": int(raw_data.get("days_until_departure", raw_data.get("days_remaining", 4))),
            "is_weekend": int(raw_data.get("is_weekend", 1)),
            "season": str(raw_data.get("season", "Festival Surge")),
            "season_multiplier": float(raw_data.get("season_multiplier", 1.35)),
            "special_event": str(raw_data.get("special_event", "Normal Day")),
            "event_multiplier": float(raw_data.get("event_multiplier", 1.0)),
            "customer_segment": str(raw_data.get("customer_segment", "Corporate Traveler")),
            "price_sensitivity": float(raw_data.get("price_sensitivity", 0.25)),
            "purchase_frequency": float(raw_data.get("purchase_frequency", 6.0)),
            "conversion_rate": float(raw_data.get("conversion_rate", 0.45)),
            "booking_velocity": float(raw_data.get("booking_velocity", 6.2))
        }

    def format_display(self, result: Dict[str, Any]) -> Dict[str, Any]:
        res = result.copy()
        res["domain_label"] = "Flight Ticket"
        res["inventory_label"] = f"{res['inventory_remaining']} seats left ({int(res['occupancy_rate']*100)}% load factor)"
        res["unit_label"] = "per seat"
        res["lead_time_label"] = f"{res['days_remaining']} days to departure"
        return res


class TravelPackageAdapter(BaseDomainAdapter):
    """Adapter for Bundled Holiday / Travel Packages."""

    def __init__(self):
        super().__init__(domain_name="travel_package", currency_symbol="₹")

    def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        max_slots = int(raw_data.get("max_slots", raw_data.get("total_capacity", 25)))
        slots_left = int(raw_data.get("slots_remaining", raw_data.get("inventory_remaining", 8)))
        booking_ratio = float(raw_data.get("booking_ratio", raw_data.get("occupancy_rate", (max_slots - slots_left) / max(max_slots, 1))))

        return {
            "domain": "travel_package",
            "item_id": str(raw_data.get("item_id", "PKG-01")),
            "item_name": str(raw_data.get("package_name", raw_data.get("item_name", "Goa Coastal Escape 4D3N"))),
            "sub_type": str(raw_data.get("theme", raw_data.get("sub_type", "Coastal Holiday"))),
            "base_price": float(raw_data.get("base_cost", raw_data.get("base_price", 16500))),
            "current_price": float(raw_data.get("current_price", 16500)),
            "competitor_price": float(raw_data.get("competitor_price", 17900)),
            "inventory_remaining": slots_left,
            "total_capacity": max_slots,
            "inventory_ratio": round(float(slots_left / max(max_slots, 1)), 3),
            "occupancy_rate": booking_ratio,
            "days_remaining": int(raw_data.get("days_until_tour", raw_data.get("days_remaining", 12))),
            "is_weekend": int(raw_data.get("is_holiday", raw_data.get("is_weekend", 1))),
            "season": str(raw_data.get("season", "Winter Peak")),
            "season_multiplier": float(raw_data.get("season_multiplier", 1.3)),
            "special_event": str(raw_data.get("special_event", "Normal Day")),
            "event_multiplier": float(raw_data.get("event_multiplier", 1.0)),
            "customer_segment": str(raw_data.get("customer_segment", "Honeymooners")),
            "price_sensitivity": float(raw_data.get("price_sensitivity", 0.3)),
            "purchase_frequency": float(raw_data.get("purchase_frequency", 1.5)),
            "conversion_rate": float(raw_data.get("conversion_rate", 0.35)),
            "booking_velocity": float(raw_data.get("booking_velocity", 2.8))
        }

    def format_display(self, result: Dict[str, Any]) -> Dict[str, Any]:
        res = result.copy()
        res["domain_label"] = "Travel Package"
        res["inventory_label"] = f"{res['inventory_remaining']} slots left ({int(res['occupancy_rate']*100)}% filled)"
        res["unit_label"] = "per package"
        res["lead_time_label"] = f"{res['days_remaining']} days to departure"
        return res


# Adapter Registry
ADAPTERS = {
    "hotel": HotelAdapter(),
    "hotels": HotelAdapter(),
    "product": ProductAdapter(),
    "products": ProductAdapter(),
    "flight": FlightAdapter(),
    "flights": FlightAdapter(),
    "travel_package": TravelPackageAdapter(),
    "travel_packages": TravelPackageAdapter(),
}


def get_adapter(domain: str) -> BaseDomainAdapter:
    clean_domain = str(domain).lower().strip()
    if clean_domain in ADAPTERS:
        return ADAPTERS[clean_domain]
    raise ValueError(f"Unsupported domain: '{domain}'. Supported: {list(ADAPTERS.keys())}")
