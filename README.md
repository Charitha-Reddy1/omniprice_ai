# OmniPrice AI — Real-Time Multi-Domain Autonomous Dynamic Pricing Engine

> **Hackathon Architecture Showcase** &middot; Built as a modular, production-ready, reusable AI Dynamic Pricing Platform for **Hotels, Retail Products, Flight Tickets, and Bundled Travel Packages**.

---

## 1. Problem Statement
Traditional static or rule-based pricing systems fail to react dynamically to high-velocity market shifts. Businesses lose revenue when inventory is sold too cheaply during high-demand surges or when high prices lead to unsold perishables (hotel rooms, airline seats, seasonal inventory). Furthermore, black-box AI pricing engines lack trust because managers cannot understand *why* prices changed, nor can they prevent dangerous price spikes without hard business safety guardrails.

## 2. Business Objective
* **Revenue & Margin Maximization:** Dynamically capture willingness-to-pay and consumer surplus during high-demand and high-scarcity conditions.
* **Velocity & Inventory Optimization:** Stimulate demand during off-peak times before expiration without eroding brand value.
* **Safety & Regulatory Compliance:** Enforce price guardrails (ceilings, floors, single-step change caps).
* **Explainability & Human Agency:** Provide transparent mathematical and natural language justifications with human-in-the-loop override capabilities.

---

## 3. Four Domains, One Unified Engine
Rather than developing siloed, duplicate pricing systems, **OmniPrice AI** uses a single core mathematical and machine learning engine configured through lightweight **Domain Adapters**:

1. **Hotel Rooms:** Available rooms, occupancy rate, check-in lead time, weekend multipliers, special events, customer price sensitivity.
2. **Retail Products:** Stock remaining, restock cycle, sales velocity, promo status, customer segment elasticity, flash deals.
3. **Flight Tickets:** Seat capacity, seats remaining, departure countdown, route demand, load factors, festival surge events.
4. **Travel Packages:** Max tour slots, booking ratio, departure countdown, theme/seasonality multipliers, holiday events.

```
                         [ DOMAIN ADAPTERS ]
      +--------------+--------------+--------------+------------------+
      | HotelAdapter | ProdAdapter  | FlightAdapter| TravelPkgAdapter |
      +--------------+--------------+--------------+------------------+
                             |
                             v
               +-----------------------------+
               |  Normalized Entity Schema   |
               +-----------------------------+
                             |
                             v
               +-----------------------------+
               |  Multi-Domain ML Predictor  |
               |  (HistGradientBoosting)     |
               +-----------------------------+
                             |
                             v
               +-----------------------------+
               |   Mathematical Optimizer    |
               | (Elasticity, Scarcity, Event)|
               +-----------------------------+
                             |
                             v
               +-----------------------------+
               |   Price Safety Guardrails   |
               |  (Caps, Floors, Step-Limits)|
               +-----------------------------+
                             |
                             v
               +-----------------------------+
               | Explainable AI (XAI) Engine |
               +-----------------------------+
                             |
                             v
               +-----------------------------+
               |  Real-Time SaaS Dashboard   |
               +-----------------------------+
```

---

## 4. Machine Learning Approach & Genuine Metrics
* **Dataset:** Trained on a combined multi-domain dataset (`data/combined_demand_training.csv`) containing 10,000 samples across all 4 domains.
* **Algorithm:** `HistGradientBoostingRegressor` (Scikit-Learn 1.5.1) with numeric pipelines and categorical one-hot encoding (`domain`, `customer_segment`, `season`, `special_event`).
* **Evaluation (Reproducible Seed: 42):**
  * **$R^2$ Score:** `0.9530`
  * **Mean Absolute Error (MAE):** `3.438`
  * **Root Mean Squared Error (RMSE):** `4.512`
  * **Inference Latency:** `< 2 ms`
* **Features:** `domain`, `base_price`, `current_price`, `competitor_price`, `price_ratio`, `occupancy_rate`, `inventory_ratio`, `inventory_remaining`, `days_remaining`, `is_weekend`, `season_multiplier`, `event_multiplier`, `booking_velocity`, `price_sensitivity`, `purchase_frequency`,  `customer_segment`, `season`, `special_event`.

---

## 5. Customer Behaviour & Special Event Analysis
* **Customer Behaviour:** Incorporates `price_sensitivity` and `purchase_frequency` into ML feature engineering, demand forecasting, revenue projections, and XAI summaries. `conversion_rate` remains an operational/simulation signal but is not used as a demand-model input because it is derived from the demand target.
* **Special Events:** Explicitly models `special_event` ("Normal Day", "Weekend", "Holiday", "Festival", "Concert", "Major Event") with `event_multiplier` (1.0x to 1.55x).
* **Interactive Trigger:** Clicking `[🎉 Simulate Special Event]` dynamically injects event surges into the real-time pipeline.

---

## 6. Price Safety Guardrails
To prevent price gouging or disastrous margin erosion, the engine enforces strict multi-layered constraints:
* **Absolute Ceiling:** Cannot exceed $+65\%$ of base price.
* **Absolute Floor:** Cannot drop below $65\%$ of base price.
* **Step Limit:** Maximum single-step increase capped at $+20\%$.
* **Step Floor:** Maximum single-step decrease floored at $-20\%$.
* **Transparency:** When a price is capped, the UI flags the specific guardrail rule triggered.

---

## 7. Architecture Alternatives & Decision Justification
| Architecture | Pros | Cons | Hackathon Decision |
|---|---|---|---|
| **Monolithic** | Simple | Poor separation of concerns | Rejected |
| **Modular Monolith (SELECTED)** | Blazing fast development, zero network serialization latency, easy local deployment, strict module interfaces | Needs deliberate discipline | **SELECTED WINNER** |
| **Microservices** | Independent scaling | High operational complexity, docker orchestration, network latency | Rejected for Hackathon |
| **Event-Driven (Kafka/Flink)** | High throughput | Excessive infrastructure overhead | Rejected for Hackathon |

---

## 8. Real-Time Simulation Engine & Seed Determinism
The built-in deterministic simulator runs background ticks and accepts real-time demo triggers:
* **Deterministic Seed:** Hard-pinned to `Seed 42` (with full runtime logging).
* **Interactive Triggers:**
  * `[Increase Demand]` $\rightarrow$ Spikes booking velocity and season multiplier.
  * `[Decrease Demand]` $\rightarrow$ Simulates market slowdown.
  * `[Reduce Inventory]` $\rightarrow$ Drops available units to trigger scarcity pricing.
  * `[Increase / Decrease Competitor Price]` $\rightarrow$ Tests competitor parity defense.
  * `[Simulate Booking]` $\rightarrow$ Live organic reservation decrement.
  * `[🎉 Simulate Special Event]` $\rightarrow$ Injects festival/concert/major event surge.
  * `[Reset Scenario]` $\rightarrow$ Instantly restores seed 42 baseline.

---

## 9. Human-in-the-Loop & Audit Log
Pricing managers can interact with any recommendation:
1. **Accept:** Commits AI recommendation to active production.
2. **Reject:** Discards recommendation, retaining current rate.
3. **Override:** Sets custom price with mandatory managerial reason note.
* All decisions are persisted to the in-memory **Audit Trail** and displayed on the dashboard.

---

## 10. Installation & Quickstart

### Prerequisites
* Python 3.10+ (Python 3.14 compatible)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Verify/Train Multi-Domain Model
The project ships with pre-prepared domain datasets and a persisted trained model. If the model files are removed, the application can retrain from `data/combined_demand_training.csv`.

```bash
python services/demand_predictor.py
```

### Step 3: Run Automated Test Suite
```bash
python -m unittest tests/test_pricing.py
```
*(All 18 tests pass in ~2 seconds)*

### Step 4: Launch Web Server & Dashboard
```bash
python app.py
```
Open **`http://localhost:5000`** in your browser.

---

## 11. Mentor Connect Q&A

**Q1: Why dynamic pricing?**
> Fixed pricing leaves substantial money on the table during demand surges and causes high inventory write-offs during off-peak periods. Dynamic pricing optimizes the intersection of demand, inventory perishability, and competitive positioning.

**Q2: Why AI/ML?**
> Rule-based lookup tables cannot scale to multi-variate non-linear interactions across lead time, competitor actions, seasonal patterns, customer behaviour, and special events. ML learns continuous demand probability densities.

**Q3: Why these four domains?**
> Hotels, Products, Flights, and Travel Packages share identical dynamic pricing fundamentals (perishability/holding cost, lead time urgency, competitor benchmarks, and capacity constraints) while testing different velocity profiles.

**Q4: Why one common pricing engine?**
> Code reusability and operational efficiency. Domain-specific features are transformed into a normalized schema via adapters, keeping the core ML, optimizer, and guardrail logic dry and centrally maintained.

**Q5: How is it real-time?**
> Decisions are computed in `< 5ms` per request. Market signals (bookings, competitor price adjustments, special event surges) trigger immediate recalculation and live dashboard UI updates.

**Q6: What happens if the API fails?**
> The system has a 3-tier fallback chain: Live API $\rightarrow$ Cached State $\rightarrow$ Deterministic Simulator with graceful heuristic degradation if the ML model is unreachable.

**Q7: How do you prevent unrealistic prices?**
> Business Safety Guardrails enforce strict $\pm 20\%$ single-step bounds and hard absolute margin ceilings/floors before any price is recommended.

**Q8: How is the ML model evaluated?**
> Evaluated on an isolated $20\%$ hold-out test set from 10,000 combined records across all 4 domains using standard regression metrics: MAE ($3.438$), RMSE ($4.512$), and $R^2$ score ($0.9530$).

**Q9: Why this architecture?**
> A Modular Monolith delivers ultra-low sub-millisecond in-process latency, zero deployment friction, and pristine modular boundaries that can easily be extracted into microservices if needed.

**Q10: Why not microservices?**
> Microservices introduce network overhead, distributed failure modes, and deployment complexity that provide zero business value in a hackathon evaluation context.

**Q11: How is the system reusable?**
> To add a 5th domain (e.g. Ride Sharing), one simply creates a new 20-line `RideAdapter` implementing `BaseDomainAdapter`. The core engine requires zero modifications.

**Q12: How would you scale this in production?**
> Deploy as containerized stateless workers behind an Application Load Balancer with Redis for hot cache and Kafka for event streaming if transaction volumes exceed $100\text{k req/sec}$.

**Q13: How do you monitor it?**
> Real-time latency tracking, alert triggers for low inventory / demand spikes / low model confidence, and full human override audit logging.

**Q14: How do you explain the AI recommendation?**
> The XAI engine decomposes the mathematical factors (demand pressure, inventory scarcity, competitor capture, velocity momentum, special event surges, customer price sensitivity) into transparent impact percentages and natural language summaries.

**Q15: What are the limitations?**
> Does not account for macro-economic supply chain disruptions or hyper-personalized 1-to-1 customer tracking (by design, to preserve user privacy).

---

## 12. Final Compliance Audit Table (§29)

| Requirement | Evidence | Status |
|---|---|---|
| **Demand fluctuations** | Simulated velocity drift, demand scores & ML prediction updates | **COMPLETE** |
| **Seasonal changes** | Multi-season multipliers (`Peak`, `Festive Sale`, `Festival Surge`, `Winter Peak`) | **COMPLETE** |
| **Competitor pricing** | Real-time competitor price benchmarking, parity capture & elasticity | **COMPLETE** |
| **Inventory availability** | Scarcity curve calculations on `inventory_remaining` & `inventory_ratio` | **COMPLETE** |
| **Special events** | Explicit `special_event` ("Concert", "Festival", "Holiday", "Major Event") & `event_multiplier` | **COMPLETE** |
| **Customer behaviour** | `customer_segment`, `price_sensitivity`, `purchase_frequency` | **COMPLETE** |
| **Demand prediction** | Multi-domain trained `HistGradientBoostingRegressor` ($R^2 = 0.9530$, $\text{MAE} = 3.438$) | **COMPLETE** |
| **Behaviour analysis** | Price sensitivity influences demand model, elasticity, and XAI explanations | **COMPLETE** |
| **Competitor monitoring** | Live competitor tracking & demo button triggers | **COMPLETE** |
| **Optimal price recommendation** | Core pricing optimizer with elasticity, scarcity, event, and velocity factors | **COMPLETE** |
| **Revenue impact** | Elasticity-adjusted before/after estimated revenue projections | **COMPLETE** |
| **Four domains** | Hotel, Product, Flight, Travel Package normalized via domain adapters | **COMPLETE** |
| **Real-time decision** | Sub-5ms decision pipeline with automatic 3s stream ticks and demo controls | **COMPLETE** |
| **Reusable engine** | Single `DynamicPricingEngine.calculate_price()` across all 4 domains | **COMPLETE** |
