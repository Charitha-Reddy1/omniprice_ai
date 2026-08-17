"""
Deterministic Real-Time Market Simulator.
Simulates live dynamic market events (bookings, competitor price adjustments, demand surges, cancellations, special events)
with a deterministic random seed for repeatable judge demonstrations across multiple real-world entities per domain.
"""

import copy
import random
from typing import Dict, Any, List


DEFAULT_SEEDED_ENTITIES = {
    "hotel": {
        "HTL-01": {
            "item_id": "HTL-01",
            "item_name": "Taj Mahal Palace",
            "sub_type": "Deluxe Sea View Room",
            "base_price": 5000.0,
            "current_price": 5200.0,
            "competitor_price": 5400.0,
            "inventory_remaining": 12,
            "total_capacity": 50,
            "inventory_ratio": 0.24,
            "occupancy_rate": 0.76,
            "days_remaining": 3,
            "is_weekend": 1,
            "season": "Peak",
            "season_multiplier": 1.25,
            "special_event": "Normal Day",
            "event_multiplier": 1.0,
            "customer_segment": "Leisure",
            "price_sensitivity": 0.85,
            "purchase_frequency": 2.5,
            "conversion_rate": 0.38,
            "booking_velocity": 4.2
        },
        "HTL-02": {
            "item_id": "HTL-02",
            "item_name": "The Oberoi Mumbai",
            "sub_type": "Executive Suite",
            "base_price": 3800.0,
            "current_price": 4100.0,
            "competitor_price": 4250.0,
            "inventory_remaining": 8,
            "total_capacity": 40,
            "inventory_ratio": 0.20,
            "occupancy_rate": 0.80,
            "days_remaining": 2,
            "is_weekend": 0,
            "season": "Regular",
            "season_multiplier": 1.10,
            "special_event": "Normal Day",
            "event_multiplier": 1.0,
            "customer_segment": "Business",
            "price_sensitivity": 0.40,
            "purchase_frequency": 5.0,
            "conversion_rate": 0.45,
            "booking_velocity": 5.5
        },
        "HTL-03": {
            "item_id": "HTL-03",
            "item_name": "ITC Grand Chola",
            "sub_type": "Tower Room",
            "base_price": 4200.0,
            "current_price": 4400.0,
            "competitor_price": 4600.0,
            "inventory_remaining": 15,
            "total_capacity": 60,
            "inventory_ratio": 0.25,
            "occupancy_rate": 0.75,
            "days_remaining": 1,
            "is_weekend": 0,
            "season": "Regular",
            "season_multiplier": 1.05,
            "special_event": "Normal Day",
            "event_multiplier": 1.0,
            "customer_segment": "Corporate Traveler",
            "price_sensitivity": 0.35,
            "purchase_frequency": 6.0,
            "conversion_rate": 0.50,
            "booking_velocity": 6.8
        },
        "HTL-04": {
            "item_id": "HTL-04",
            "item_name": "Hyatt Regency Hyderabad",
            "sub_type": "Regency Suite",
            "base_price": 8500.0,
            "current_price": 9200.0,
            "competitor_price": 9500.0,
            "inventory_remaining": 5,
            "total_capacity": 20,
            "inventory_ratio": 0.25,
            "occupancy_rate": 0.75,
            "days_remaining": 6,
            "is_weekend": 1,
            "season": "Peak",
            "season_multiplier": 1.30,
            "special_event": "Weekend",
            "event_multiplier": 1.15,
            "customer_segment": "Leisure",
            "price_sensitivity": 0.90,
            "purchase_frequency": 1.8,
            "conversion_rate": 0.32,
            "booking_velocity": 3.1
        },
        "HTL-05": {
            "item_id": "HTL-05",
            "item_name": "Hyderabad Marriott Hotel & Convention Centre",
            "sub_type": "Executive Room",
            "base_price": 12500.0,
            "current_price": 13200.0,
            "competitor_price": 13800.0,
            "inventory_remaining": 3,
            "total_capacity": 10,
            "inventory_ratio": 0.30,
            "occupancy_rate": 0.70,
            "days_remaining": 4,
            "is_weekend": 1,
            "season": "Peak",
            "season_multiplier": 1.35,
            "special_event": "Normal Day",
            "event_multiplier": 1.0,
            "customer_segment": "Luxury",
            "price_sensitivity": 0.20,
            "purchase_frequency": 1.2,
            "conversion_rate": 0.28,
            "booking_velocity": 2.1
        },
        "HTL-06": {
            "item_id": "HTL-06",
            "item_name": "Taj Krishna Hyderabad",
            "sub_type": "Club Room",
            "base_price": 6200.0,
            "current_price": 6500.0,
            "competitor_price": 6800.0,
            "inventory_remaining": 9,
            "total_capacity": 35,
            "inventory_ratio": 0.257,
            "occupancy_rate": 0.743,
            "days_remaining": 5,
            "is_weekend": 0,
            "season": "Holiday",
            "season_multiplier": 1.20,
            "special_event": "Normal Day",
            "event_multiplier": 1.0,
            "customer_segment": "Honeymooners",
            "price_sensitivity": 0.30,
            "purchase_frequency": 1.5,
            "conversion_rate": 0.35,
            "booking_velocity": 3.5
        },
        "HTL-07": {
            "item_id": "HTL-07",
            "item_name": "The Leela Palace Bengaluru",
            "sub_type": "Royal Premier Room",
            "base_price": 3200.0,
            "current_price": 3400.0,
            "competitor_price": 3500.0,
            "inventory_remaining": 18,
            "total_capacity": 80,
            "inventory_ratio": 0.225,
            "occupancy_rate": 0.775,
            "days_remaining": 7,
            "is_weekend": 0,
            "season": "Regular",
            "season_multiplier": 1.0,
            "special_event": "Normal Day",
            "event_multiplier": 1.0,
            "customer_segment": "Budget",
            "price_sensitivity": 1.60,
            "purchase_frequency": 3.0,
            "conversion_rate": 0.30,
            "booking_velocity": 4.0
        },
        "HTL-08": {
            "item_id": "HTL-08",
            "item_name": "ITC Kohenur Hyderabad",
            "sub_type": "Lake View Suite",
            "base_price": 7000.0,
            "current_price": 7400.0,
            "competitor_price": 7600.0,
            "inventory_remaining": 7,
            "total_capacity": 25,
            "inventory_ratio": 0.28,
            "occupancy_rate": 0.72,
            "days_remaining": 8,
            "is_weekend": 1,
            "season": "Holiday",
            "season_multiplier": 1.25,
            "special_event": "Normal Day",
            "event_multiplier": 1.0,
            "customer_segment": "Family Group",
            "price_sensitivity": 0.90,
            "purchase_frequency": 2.0,
            "conversion_rate": 0.36,
            "booking_velocity": 3.2
        }
    },
    "product": {
        "PRD-01": {
            "item_id": "PRD-01",
            "item_name": "Sony WH-1000XM5 Headphones",
            "sub_type": "Electronics",
            "base_price": 4500.0,
            "current_price": 4650.0,
            "competitor_price": 4899.0,
            "inventory_remaining": 14,
            "total_capacity": 150,
            "inventory_ratio": 0.093,
            "occupancy_rate": 0.907,
            "days_remaining": 10,
            "is_weekend": 0,
            "season": "Festive Sale",
            "season_multiplier": 1.35,
            "special_event": "Normal Day",
            "event_multiplier": 1.0,
            "customer_segment": "Prime Member",
            "price_sensitivity": 0.68,
            "purchase_frequency": 4.5,
            "conversion_rate": 0.42,
            "booking_velocity": 6.5
        },
        "PRD-02": {
            "item_id": "PRD-02",
            "item_name": "Apple MacBook Pro 16-inch",
            "sub_type": "Computers",
            "base_price": 65000.0,
            "current_price": 68000.0,
            "competitor_price": 71000.0,
            "inventory_remaining": 8,
            "total_capacity": 50,
            "inventory_ratio": 0.16,
            "occupancy_rate": 0.84,
            "days_remaining": 14,
            "is_weekend": 0,
            "season": "Regular",
            "season_multiplier": 1.10,
            "special_event": "Normal Day",
            "event_multiplier": 1.0,
            "customer_segment": "Corporate Traveler",
            "price_sensitivity": 0.40,
            "purchase_frequency": 1.2,
            "conversion_rate": 0.35,
            "booking_velocity": 3.0
        },
        "PRD-03": {
            "item_id": "PRD-03",
            "item_name": "Apple iPhone 15 Pro",
            "sub_type": "Mobiles",
            "base_price": 42000.0,
            "current_price": 43500.0,
            "competitor_price": 45000.0,
            "inventory_remaining": 22,
            "total_capacity": 100,
            "inventory_ratio": 0.22,
            "occupancy_rate": 0.78,
            "days_remaining": 12,
            "is_weekend": 1,
            "season": "Festive Sale",
            "season_multiplier": 1.25,
            "special_event": "Normal Day",
            "event_multiplier": 1.0,
            "customer_segment": "Loyal Customer",
            "price_sensitivity": 0.55,
            "purchase_frequency": 2.2,
            "conversion_rate": 0.40,
            "booking_velocity": 5.2
        },
        "PRD-04": {
            "item_id": "PRD-04",
            "item_name": "Samsung Galaxy Watch 6",
            "sub_type": "Wearables",
            "base_price": 12000.0,
            "current_price": 12800.0,
            "competitor_price": 13500.0,
            "inventory_remaining": 16,
            "total_capacity": 80,
            "inventory_ratio": 0.20,
            "occupancy_rate": 0.80,
            "days_remaining": 9,
            "is_weekend": 0,
            "season": "Regular",
            "season_multiplier": 1.05,
            "special_event": "Normal Day",
            "event_multiplier": 1.0,
            "customer_segment": "Prime Member",
            "price_sensitivity": 0.60,
            "purchase_frequency": 3.0,
            "conversion_rate": 0.38,
            "booking_velocity": 4.1
        },
        "PRD-05": {
            "item_id": "PRD-05",
            "item_name": "Canon EOS R6 Camera",
            "sub_type": "Photography",
            "base_price": 38000.0,
            "current_price": 39500.0,
            "competitor_price": 41000.0,
            "inventory_remaining": 6,
            "total_capacity": 30,
            "inventory_ratio": 0.20,
            "occupancy_rate": 0.80,
            "days_remaining": 15,
            "is_weekend": 1,
            "season": "Holiday",
            "season_multiplier": 1.15,
            "special_event": "Normal Day",
            "event_multiplier": 1.0,
            "customer_segment": "Leisure",
            "price_sensitivity": 0.70,
            "purchase_frequency": 1.5,
            "conversion_rate": 0.30,
            "booking_velocity": 2.5
        },
        "PRD-06": {
            "item_id": "PRD-06",
            "item_name": "Nike Air Max Running Shoes",
            "sub_type": "Footwear",
            "base_price": 3500.0,
            "current_price": 3700.0,
            "competitor_price": 3900.0,
            "inventory_remaining": 30,
            "total_capacity": 120,
            "inventory_ratio": 0.25,
            "occupancy_rate": 0.75,
            "days_remaining": 20,
            "is_weekend": 0,
            "season": "Regular",
            "season_multiplier": 1.0,
            "special_event": "Normal Day",
            "event_multiplier": 1.0,
            "customer_segment": "Standard",
            "price_sensitivity": 1.10,
            "purchase_frequency": 2.8,
            "conversion_rate": 0.35,
            "booking_velocity": 4.8
        },
        "PRD-07": {
            "item_id": "PRD-07",
            "item_name": "Sony PlayStation 5 Console",
            "sub_type": "Gaming",
            "base_price": 48000.0,
            "current_price": 49900.0,
            "competitor_price": 52000.0,
            "inventory_remaining": 7,
            "total_capacity": 40,
            "inventory_ratio": 0.175,
            "occupancy_rate": 0.825,
            "days_remaining": 8,
            "is_weekend": 1,
            "season": "Festive Sale",
            "season_multiplier": 1.30,
            "special_event": "Major Event",
            "event_multiplier": 1.20,
            "customer_segment": "Prime Member",
            "price_sensitivity": 0.50,
            "purchase_frequency": 1.6,
            "conversion_rate": 0.42,
            "booking_velocity": 5.8
        },
        "PRD-08": {
            "item_id": "PRD-08",
            "item_name": "Samsung Galaxy Tab S9",
            "sub_type": "Computers",
            "base_price": 28000.0,
            "current_price": 29500.0,
            "competitor_price": 31000.0,
            "inventory_remaining": 12,
            "total_capacity": 60,
            "inventory_ratio": 0.20,
            "occupancy_rate": 0.80,
            "days_remaining": 11,
            "is_weekend": 0,
            "season": "Regular",
            "season_multiplier": 1.05,
            "special_event": "Normal Day",
            "event_multiplier": 1.0,
            "customer_segment": "Standard",
            "price_sensitivity": 0.80,
            "purchase_frequency": 2.0,
            "conversion_rate": 0.36,
            "booking_velocity": 3.8
        }
    },
    "flight": {
        "FLT-01": {
            "item_id": "FLT-01",
            "item_name": "IndiGo — Delhi → Mumbai",
            "sub_type": "DEL → BOM",
            "base_price": 5500.0,
            "current_price": 6100.0,
            "competitor_price": 6450.0,
            "inventory_remaining": 18,
            "total_capacity": 180,
            "inventory_ratio": 0.10,
            "occupancy_rate": 0.90,
            "days_remaining": 2,
            "is_weekend": 1,
            "season": "Festival Surge",
            "season_multiplier": 1.40,
            "special_event": "Normal Day",
            "event_multiplier": 1.0,
            "customer_segment": "Corporate Traveler",
            "price_sensitivity": 0.25,
            "purchase_frequency": 6.2,
            "conversion_rate": 0.48,
            "booking_velocity": 7.8
        },
        "FLT-02": {
            "item_id": "FLT-02",
            "item_name": "Air India — Hyderabad → Delhi",
            "sub_type": "HYD → DEL",
            "base_price": 4800.0,
            "current_price": 5200.0,
            "competitor_price": 5400.0,
            "inventory_remaining": 24,
            "total_capacity": 180,
            "inventory_ratio": 0.133,
            "occupancy_rate": 0.867,
            "days_remaining": 4,
            "is_weekend": 0,
            "season": "Regular",
            "season_multiplier": 1.10,
            "special_event": "Normal Day",
            "event_multiplier": 1.0,
            "customer_segment": "Business",
            "price_sensitivity": 0.35,
            "purchase_frequency": 5.5,
            "conversion_rate": 0.45,
            "booking_velocity": 6.0
        },
        "FLT-03": {
            "item_id": "FLT-03",
            "item_name": "Akasa Air — Hyderabad → Bengaluru",
            "sub_type": "HYD → BLR",
            "base_price": 3200.0,
            "current_price": 3500.0,
            "competitor_price": 3700.0,
            "inventory_remaining": 30,
            "total_capacity": 150,
            "inventory_ratio": 0.20,
            "occupancy_rate": 0.80,
            "days_remaining": 5,
            "is_weekend": 0,
            "season": "Regular",
            "season_multiplier": 1.0,
            "special_event": "Normal Day",
            "event_multiplier": 1.0,
            "customer_segment": "Standard",
            "price_sensitivity": 0.80,
            "purchase_frequency": 3.2,
            "conversion_rate": 0.40,
            "booking_velocity": 5.0
        },
        "FLT-04": {
            "item_id": "FLT-04",
            "item_name": "IndiGo — Bengaluru → Chennai",
            "sub_type": "BLR → MAA",
            "base_price": 2800.0,
            "current_price": 3100.0,
            "competitor_price": 3300.0,
            "inventory_remaining": 35,
            "total_capacity": 150,
            "inventory_ratio": 0.233,
            "occupancy_rate": 0.767,
            "days_remaining": 6,
            "is_weekend": 0,
            "season": "Regular",
            "season_multiplier": 1.0,
            "special_event": "Normal Day",
            "event_multiplier": 1.0,
            "customer_segment": "Budget",
            "price_sensitivity": 1.40,
            "purchase_frequency": 2.5,
            "conversion_rate": 0.32,
            "booking_velocity": 4.2
        },
        "FLT-05": {
            "item_id": "FLT-05",
            "item_name": "Air India — Mumbai → Hyderabad",
            "sub_type": "BOM → HYD",
            "base_price": 4500.0,
            "current_price": 4800.0,
            "competitor_price": 5100.0,
            "inventory_remaining": 15,
            "total_capacity": 180,
            "inventory_ratio": 0.083,
            "occupancy_rate": 0.917,
            "days_remaining": 1,
            "is_weekend": 1,
            "season": "Festival Surge",
            "season_multiplier": 1.35,
            "special_event": "Major Event",
            "event_multiplier": 1.25,
            "customer_segment": "Corporate Traveler",
            "price_sensitivity": 0.30,
            "purchase_frequency": 5.8,
            "conversion_rate": 0.50,
            "booking_velocity": 8.1
        },
        "FLT-06": {
            "item_id": "FLT-06",
            "item_name": "Air India Express — Delhi → Bengaluru",
            "sub_type": "DEL → BLR",
            "base_price": 5800.0,
            "current_price": 6300.0,
            "competitor_price": 6600.0,
            "inventory_remaining": 20,
            "total_capacity": 180,
            "inventory_ratio": 0.111,
            "occupancy_rate": 0.889,
            "days_remaining": 3,
            "is_weekend": 0,
            "season": "Regular",
            "season_multiplier": 1.15,
            "special_event": "Normal Day",
            "event_multiplier": 1.0,
            "customer_segment": "Business",
            "price_sensitivity": 0.38,
            "purchase_frequency": 4.8,
            "conversion_rate": 0.44,
            "booking_velocity": 6.5
        },
        "FLT-07": {
            "item_id": "FLT-07",
            "item_name": "IndiGo — Chennai → Delhi",
            "sub_type": "MAA → DEL",
            "base_price": 5200.0,
            "current_price": 5700.0,
            "competitor_price": 6000.0,
            "inventory_remaining": 22,
            "total_capacity": 180,
            "inventory_ratio": 0.122,
            "occupancy_rate": 0.878,
            "days_remaining": 3,
            "is_weekend": 1,
            "season": "Holiday",
            "season_multiplier": 1.20,
            "special_event": "Normal Day",
            "event_multiplier": 1.0,
            "customer_segment": "Leisure Flyer",
            "price_sensitivity": 0.85,
            "purchase_frequency": 2.2,
            "conversion_rate": 0.36,
            "booking_velocity": 5.1
        },
        "FLT-08": {
            "item_id": "FLT-08",
            "item_name": "Air India Express — Hyderabad → Goa",
            "sub_type": "HYD → GOI",
            "base_price": 3900.0,
            "current_price": 4300.0,
            "competitor_price": 4600.0,
            "inventory_remaining": 12,
            "total_capacity": 150,
            "inventory_ratio": 0.08,
            "occupancy_rate": 0.92,
            "days_remaining": 2,
            "is_weekend": 1,
            "season": "Festival Surge",
            "season_multiplier": 1.30,
            "special_event": "Festival",
            "event_multiplier": 1.30,
            "customer_segment": "Leisure Flyer",
            "price_sensitivity": 0.75,
            "purchase_frequency": 2.0,
            "conversion_rate": 0.40,
            "booking_velocity": 7.0
        }
    },
    "travel_package": {
        "PKG-01": {
            "item_id": "PKG-01",
            "item_name": "Goa Coastal Escape 4D3N",
            "sub_type": "Coastal Holiday",
            "base_price": 16500.0,
            "current_price": 17200.0,
            "competitor_price": 18500.0,
            "inventory_remaining": 6,
            "total_capacity": 25,
            "inventory_ratio": 0.24,
            "occupancy_rate": 0.76,
            "days_remaining": 5,
            "is_weekend": 1,
            "season": "Winter Peak",
            "season_multiplier": 1.35,
            "special_event": "Normal Day",
            "event_multiplier": 1.0,
            "customer_segment": "Honeymooners",
            "price_sensitivity": 0.32,
            "purchase_frequency": 1.5,
            "conversion_rate": 0.36,
            "booking_velocity": 3.4
        },
        "PKG-02": {
            "item_id": "PKG-02",
            "item_name": "Dubai City & Desert Experience 5D4N",
            "sub_type": "International Tour",
            "base_price": 45000.0,
            "current_price": 48000.0,
            "competitor_price": 51000.0,
            "inventory_remaining": 4,
            "total_capacity": 20,
            "inventory_ratio": 0.20,
            "occupancy_rate": 0.80,
            "days_remaining": 10,
            "is_weekend": 0,
            "season": "Peak",
            "season_multiplier": 1.30,
            "special_event": "Normal Day",
            "event_multiplier": 1.0,
            "customer_segment": "Luxury",
            "price_sensitivity": 0.25,
            "purchase_frequency": 1.2,
            "conversion_rate": 0.30,
            "booking_velocity": 2.8
        },
        "PKG-03": {
            "item_id": "PKG-03",
            "item_name": "Bali Island Explorer 6D5N",
            "sub_type": "Tropical Island",
            "base_price": 38000.0,
            "current_price": 41000.0,
            "competitor_price": 43500.0,
            "inventory_remaining": 5,
            "total_capacity": 20,
            "inventory_ratio": 0.25,
            "occupancy_rate": 0.75,
            "days_remaining": 12,
            "is_weekend": 1,
            "season": "Peak",
            "season_multiplier": 1.25,
            "special_event": "Normal Day",
            "event_multiplier": 1.0,
            "customer_segment": "Honeymooners",
            "price_sensitivity": 0.30,
            "purchase_frequency": 1.4,
            "conversion_rate": 0.32,
            "booking_velocity": 3.0
        },
        "PKG-04": {
            "item_id": "PKG-04",
            "item_name": "Kashmir Valley Retreat 5D4N",
            "sub_type": "Mountain Sanctuary",
            "base_price": 28000.0,
            "current_price": 30000.0,
            "competitor_price": 32000.0,
            "inventory_remaining": 7,
            "total_capacity": 30,
            "inventory_ratio": 0.233,
            "occupancy_rate": 0.767,
            "days_remaining": 8,
            "is_weekend": 0,
            "season": "Winter Peak",
            "season_multiplier": 1.30,
            "special_event": "Normal Day",
            "event_multiplier": 1.0,
            "customer_segment": "Family Group",
            "price_sensitivity": 0.85,
            "purchase_frequency": 1.8,
            "conversion_rate": 0.34,
            "booking_velocity": 3.2
        },
        "PKG-05": {
            "item_id": "PKG-05",
            "item_name": "Kerala Backwaters Journey 4D3N",
            "sub_type": "Backwater Cruise",
            "base_price": 22000.0,
            "current_price": 23500.0,
            "competitor_price": 25000.0,
            "inventory_remaining": 8,
            "total_capacity": 30,
            "inventory_ratio": 0.267,
            "occupancy_rate": 0.733,
            "days_remaining": 7,
            "is_weekend": 1,
            "season": "Holiday",
            "season_multiplier": 1.20,
            "special_event": "Normal Day",
            "event_multiplier": 1.0,
            "customer_segment": "Leisure",
            "price_sensitivity": 0.80,
            "purchase_frequency": 2.0,
            "conversion_rate": 0.35,
            "booking_velocity": 3.6
        },
        "PKG-06": {
            "item_id": "PKG-06",
            "item_name": "Rajasthan Heritage Circuit 6D5N",
            "sub_type": "Cultural Circuit",
            "base_price": 32000.0,
            "current_price": 34500.0,
            "competitor_price": 36500.0,
            "inventory_remaining": 6,
            "total_capacity": 25,
            "inventory_ratio": 0.24,
            "occupancy_rate": 0.76,
            "days_remaining": 9,
            "is_weekend": 0,
            "season": "Winter Peak",
            "season_multiplier": 1.30,
            "special_event": "Normal Day",
            "event_multiplier": 1.0,
            "customer_segment": "Cultural Traveler",
            "price_sensitivity": 0.70,
            "purchase_frequency": 1.5,
            "conversion_rate": 0.33,
            "booking_velocity": 2.9
        },
        "PKG-07": {
            "item_id": "PKG-07",
            "item_name": "Singapore City Discovery 4D3N",
            "sub_type": "City Break",
            "base_price": 42000.0,
            "current_price": 44500.0,
            "competitor_price": 47000.0,
            "inventory_remaining": 5,
            "total_capacity": 20,
            "inventory_ratio": 0.25,
            "occupancy_rate": 0.75,
            "days_remaining": 11,
            "is_weekend": 1,
            "season": "Regular",
            "season_multiplier": 1.15,
            "special_event": "Normal Day",
            "event_multiplier": 1.0,
            "customer_segment": "Family Group",
            "price_sensitivity": 0.75,
            "purchase_frequency": 1.6,
            "conversion_rate": 0.35,
            "booking_velocity": 3.3
        },
        "PKG-08": {
            "item_id": "PKG-08",
            "item_name": "Maldives Island Escape 5D4N",
            "sub_type": "Luxury Resort",
            "base_price": 85000.0,
            "current_price": 91000.0,
            "competitor_price": 96000.0,
            "inventory_remaining": 2,
            "total_capacity": 10,
            "inventory_ratio": 0.20,
            "occupancy_rate": 0.80,
            "days_remaining": 14,
            "is_weekend": 1,
            "season": "Peak",
            "season_multiplier": 1.40,
            "special_event": "Normal Day",
            "event_multiplier": 1.0,
            "customer_segment": "Luxury",
            "price_sensitivity": 0.18,
            "purchase_frequency": 1.1,
            "conversion_rate": 0.25,
            "booking_velocity": 2.0
        }
    }
}


DEFAULT_SEEDED_STATE = {
    "hotel": DEFAULT_SEEDED_ENTITIES["hotel"]["HTL-01"],
    "product": DEFAULT_SEEDED_ENTITIES["product"]["PRD-01"],
    "flight": DEFAULT_SEEDED_ENTITIES["flight"]["FLT-01"],
    "travel_package": DEFAULT_SEEDED_ENTITIES["travel_package"]["PKG-01"]
}


class MarketSimulator:
    """Simulates deterministic live market changes across all domains and entities."""

    def __init__(self, initial_seed: int = 42):
        self.seed = initial_seed
        self.rng = random.Random(self.seed)
        self.tick_count = 0
        self.entities_state: Dict[str, Dict[str, Dict[str, Any]]] = copy.deepcopy(DEFAULT_SEEDED_ENTITIES)
        self.active_entity: Dict[str, str] = {
            "hotel": "HTL-01",
            "product": "PRD-01",
            "flight": "FLT-01",
            "travel_package": "PKG-01"
        }
        self.data_source_mode = "SIMULATED REAL-TIME DATA"

    @property
    def current_state(self) -> Dict[str, Dict[str, Any]]:
        """Backward compatibility dictionary accessor for active entities across 4 domains."""
        return {
            dom: self.entities_state[dom][self.active_entity[dom]]
            for dom in ["hotel", "product", "flight", "travel_package"]
        }

    def reset_to_seed(self, seed: int = 42):
        """Reset simulation to clean initial state with specified seed."""
        self.seed = seed
        self.rng = random.Random(self.seed)
        self.tick_count = 0
        self.entities_state = copy.deepcopy(DEFAULT_SEEDED_ENTITIES)
        self.active_entity = {
            "hotel": "HTL-01",
            "product": "PRD-01",
            "flight": "FLT-01",
            "travel_package": "PKG-01"
        }
        return {
            "status": "reset",
            "seed": self.seed,
            "tick_count": self.tick_count,
            "state": self.current_state
        }

    def get_state(self, domain: str = "hotel", item_id: str = None) -> Dict[str, Any]:
        dom = domain.lower()
        if dom not in self.entities_state:
            dom = "hotel"
        if item_id and item_id in self.entities_state[dom]:
            self.active_entity[dom] = item_id
            return self.entities_state[dom][item_id]
        active_id = self.active_entity.get(dom, list(self.entities_state[dom].keys())[0])
        return self.entities_state[dom][active_id]

    def get_entities(self, domain: str = "hotel") -> List[Dict[str, Any]]:
        dom = domain.lower()
        if dom not in self.entities_state:
            dom = "hotel"
        return [
            {
                "item_id": item_id,
                "item_name": item["item_name"],
                "sub_type": item["sub_type"],
                "current_price": item["current_price"],
                "base_price": item["base_price"],
                "is_active": (item_id == self.active_entity.get(dom))
            }
            for item_id, item in self.entities_state[dom].items()
        ]

    def apply_action(self, domain: str, action: str, amount: float = None, item_id: str = None) -> Dict[str, Any]:
        """
        Applies a discrete demo button trigger to a domain's selected entity.
        """
        dom = domain.lower()
        if dom not in self.entities_state:
            dom = "hotel"
            
        if item_id and item_id in self.entities_state[dom]:
            self.active_entity[dom] = item_id
            
        active_id = self.active_entity.get(dom, list(self.entities_state[dom].keys())[0])
        item = self.entities_state[dom][active_id]

        if action == "increase_demand":
            item["booking_velocity"] = round(min(15.0, item["booking_velocity"] + 2.5), 2)
            item["season_multiplier"] = round(min(1.8, item["season_multiplier"] + 0.15), 2)
            action_desc = f"Demand Surge injected for {item['item_name']} (+2.5 velocity, +15% season multiplier)"

        elif action == "decrease_demand":
            item["booking_velocity"] = round(max(0.4, item["booking_velocity"] - 2.0), 2)
            item["season_multiplier"] = round(max(0.75, item["season_multiplier"] - 0.15), 2)
            action_desc = f"Market Demand Softening for {item['item_name']} (-2.0 velocity)"

        elif action == "reduce_inventory":
            drop = int(amount if amount else max(1, int(item["inventory_remaining"] * 0.35)))
            item["inventory_remaining"] = max(1, item["inventory_remaining"] - drop)
            item["occupancy_rate"] = round(1.0 - (item["inventory_remaining"] / item["total_capacity"]), 3)
            item["inventory_ratio"] = round(item["inventory_remaining"] / item["total_capacity"], 3)
            action_desc = f"Inventory for {item['item_name']} reduced by {drop} units (Scarcity: {int(item['occupancy_rate']*100)}%)"

        elif action == "increase_competitor":
            delta = 0.08 if amount is None else amount
            item["competitor_price"] = round(item["competitor_price"] * (1.0 + delta), -1)
            action_desc = f"Competitor price for {item['item_name']} increased to ₹{item['competitor_price']:,.0f} (+{int(delta*100)}%)"

        elif action == "decrease_competitor":
            delta = 0.08 if amount is None else amount
            item["competitor_price"] = round(item["competitor_price"] * (1.0 - delta), -1)
            action_desc = f"Competitor price for {item['item_name']} dropped to ₹{item['competitor_price']:,.0f} (-{int(delta*100)}%)"

        elif action == "simulate_booking":
            booked = min(item["inventory_remaining"], self.rng.randint(1, 3))
            item["inventory_remaining"] = max(1, item["inventory_remaining"] - booked)
            item["occupancy_rate"] = round(1.0 - (item["inventory_remaining"] / item["total_capacity"]), 3)
            item["inventory_ratio"] = round(item["inventory_remaining"] / item["total_capacity"], 3)
            item["booking_velocity"] = round(item["booking_velocity"] + 0.8, 2)
            action_desc = f"New booking for {item['item_name']}: {booked} unit(s) secured!"

        elif action == "simulate_special_event":
            events_options = [
                ("Concert", 1.35),
                ("Major Event", 1.50),
                ("Festival", 1.40),
                ("Holiday", 1.28)
            ]
            evt_name, evt_mult = self.rng.choice(events_options)
            item["special_event"] = evt_name
            item["event_multiplier"] = evt_mult
            item["booking_velocity"] = round(item["booking_velocity"] + 3.0, 2)
            action_desc = f"🎉 Special Event Injected for {item['item_name']}: '{evt_name}' ({evt_mult}x multiplier!)"

        elif action == "reset_domain":
            self.entities_state[dom][active_id] = copy.deepcopy(DEFAULT_SEEDED_ENTITIES[dom][active_id])
            action_desc = f"Reset {item['item_name']} scenario to baseline"

        else:
            action_desc = f"Unrecognized action: {action}"

        return {
            "domain": domain,
            "action": action,
            "description": action_desc,
            "updated_state": item
        }

    def simulate_tick(self) -> Dict[str, Any]:
        """Performs a background tick with subtle, organic market fluctuations across active entities."""
        self.tick_count += 1
        events = []

        for dom in ["hotel", "product", "flight", "travel_package"]:
            active_id = self.active_entity[dom]
            item = self.entities_state[dom][active_id]
            
            # Chance of competitor price nudge (+/- 1.5%)
            if self.rng.random() < 0.35:
                pct = self.rng.choice([-0.015, -0.01, 0.01, 0.02])
                item["competitor_price"] = round(item["competitor_price"] * (1.0 + pct), -1)
                events.append(f"[{item['item_name']}] Competitor price updated to ₹{item['competitor_price']:,.0f}")

            # Chance of minor booking
            if self.rng.random() < 0.25 and item["inventory_remaining"] > 2:
                item["inventory_remaining"] -= 1
                item["occupancy_rate"] = round(1.0 - (item["inventory_remaining"] / item["total_capacity"]), 3)
                item["inventory_ratio"] = round(item["inventory_remaining"] / item["total_capacity"], 3)
                item["booking_velocity"] = round(min(14.0, item["booking_velocity"] + 0.3), 2)
                events.append(f"[{item['item_name']}] Organic booking recorded. {item['inventory_remaining']} left.")

            # Slight velocity drift
            drift = self.rng.uniform(-0.15, 0.15)
            item["booking_velocity"] = round(max(0.5, min(14.0, item["booking_velocity"] + drift)), 2)

        return {
            "tick": self.tick_count,
            "seed": self.seed,
            "events": events,
            "states": self.current_state
        }


# Global simulator instance
simulator = MarketSimulator(initial_seed=42)
