/**
 * OmniPrice AI — Real-Time Autonomous Dynamic Pricing Engine
 * Client-side Controller: Polling, Demo Triggers, Live Chart Updates, Tweening & XAI
 */

document.addEventListener("DOMContentLoaded", () => {
  // State variables
  let currentDomain = "hotel";
  let isAutoTickEnabled = true;
  let tickCountdownSec = 3;
  let timerInterval = null;
  let currentDecisionData = null;
  let allDecisionsCache = {};

  // Chart Instances
  let priceChartInstance = null;
  let elasticityChartInstance = null;
  let profitChartInstance = null;
  const historyTimestamps = [];
  const historyOurPrices = [];
  const historyCompPrices = [];

  const demandHistoryTimestamps = [];
  const historyObservedDemand = [];
  const historyPredictedDemand = [];

  // DOM Elements
  const domainButtons = document.querySelectorAll(".domain-btn");
  const singleDomainView = document.getElementById("singleDomainView");
  const allDomainsView = document.getElementById("allDomainsView");
  const allDomainsTableBody = document.getElementById("allDomainsTableBody");
  
  const tickCountdownEl = document.getElementById("tickCountdown");
  const btnToggleAutoTick = document.getElementById("btnToggleAutoTick");
  const eventTickerText = document.getElementById("eventTickerText");
  const currentSeedValue = document.getElementById("currentSeedValue");
  const dataSourceText = document.getElementById("dataSourceText");
  
  // KPI Elements
  const kpiRecPrice = document.getElementById("kpiRecPrice");
  const kpiCurrentPrice = document.getElementById("kpiCurrentPrice");
  const priceDeltaTag = document.getElementById("priceDeltaTag");
  const guardrailStatusBadge = document.getElementById("guardrailStatusBadge");
  const kpiEstRevenue = document.getElementById("kpiEstRevenue");
  const kpiRevDeltaTag = document.getElementById("kpiRevDeltaTag");
  const kpiRevDiff = document.getElementById("kpiRevDiff");
  const kpiDemandScore = document.getElementById("kpiDemandScore");
  const kpiDemandLevelTag = document.getElementById("kpiDemandLevelTag");
  const demandProgressBar = document.getElementById("demandProgressBar");
  const kpiInventoryRemaining = document.getElementById("kpiInventoryRemaining");
  const kpiTotalCapacity = document.getElementById("kpiTotalCapacity");
  const kpiOccRateTag = document.getElementById("kpiOccRateTag");
  const inventoryProgressBar = document.getElementById("inventoryProgressBar");
  const kpiLatency = document.getElementById("kpiLatency");
  const kpiConfidence = document.getElementById("kpiConfidence");
  
  // Entity Detail Elements
  const entityTitle = document.getElementById("entityTitle");
  const entitySubType = document.getElementById("entitySubType");
  const metricCurrentPrice = document.getElementById("metricCurrentPrice");
  const metricBasePrice = document.getElementById("metricBasePrice");
  const metricCompPrice = document.getElementById("metricCompPrice");
  const metricCompDiff = document.getElementById("metricCompDiff");
  const metricVelocity = document.getElementById("metricVelocity");
  const metricSeason = document.getElementById("metricSeason");
  const metricLeadDays = document.getElementById("metricLeadDays");
  const calloutRecPrice = document.getElementById("calloutRecPrice");
  const calloutPctBadge = document.getElementById("calloutPctBadge");
  const calloutGuardrailNote = document.getElementById("calloutGuardrailNote");
  
  // XAI Elements
  const xaiSummaryText = document.getElementById("xaiSummaryText");
  const xaiDriversList = document.getElementById("xaiDriversList");
  
  // Modal Elements
  const overrideModal = document.getElementById("overrideModal");
  const btnOpenOverrideModal = document.getElementById("btnOpenOverrideModal");
  const btnCloseModal = document.getElementById("btnCloseModal");
  const btnCancelModal = document.getElementById("btnCancelModal");
  const overrideForm = document.getElementById("overrideForm");
  const overrideActionSelect = document.getElementById("overrideActionSelect");
  const customPriceGroup = document.getElementById("customPriceGroup");
  const customPriceInput = document.getElementById("customPriceInput");
  const overrideReasonInput = document.getElementById("overrideReasonInput");
  const modalDomainLabel = document.getElementById("modalDomainLabel");
  const modalItemName = document.getElementById("modalItemName");
  const modalCurrentPrice = document.getElementById("modalCurrentPrice");
  const modalRecPrice = document.getElementById("modalRecPrice");
  
  // Quick action buttons
  const btnQuickAccept = document.getElementById("btnQuickAccept");
  const btnQuickReject = document.getElementById("btnQuickReject");
  
  // Alerts & Audit
  const alertsList = document.getElementById("alertsList");
  const auditTableBody = document.getElementById("auditTableBody");

  // Initialize Charts
  initCharts();

  // Respect a landing-page domain selection such as /dashboard?domain=flight.
  const requestedDomain = new URLSearchParams(window.location.search).get("domain");
  const allowedDomains = ["hotel", "product", "flight", "travel_package", "all"];
  if (requestedDomain && allowedDomains.includes(requestedDomain)) {
    currentDomain = requestedDomain;
    const requestedButton = document.querySelector(`.domain-btn[data-domain="${requestedDomain}"]`);
    if (requestedButton) {
      domainButtons.forEach(b => b.classList.remove("active"));
      requestedButton.classList.add("active");
    }
  }

  // Load initial data
  if (currentDomain === "all") {
    singleDomainView.style.display = "none";
    allDomainsView.style.display = "block";
    if (entitySelectorContainer) entitySelectorContainer.style.display = "none";
    fetchAllDomainsData();
  } else {
    singleDomainView.style.display = "block";
    allDomainsView.style.display = "none";
    if (entitySelectorContainer) entitySelectorContainer.style.display = "flex";
    fetchPricingData(currentDomain);
  }
  fetchHealthAndTelemetry();
  startTimerLoop();

  // ==========================================================================
  // Event Listeners: Domain & Entity Selectors
  // ==========================================================================
  domainButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      domainButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      currentDomain = btn.dataset.domain;

      if (currentDomain === "all") {
        singleDomainView.style.display = "none";
        allDomainsView.style.display = "block";
        if (entitySelectorContainer) entitySelectorContainer.style.display = "none";
        fetchAllDomainsData();
      } else {
        allDomainsView.style.display = "none";
        singleDomainView.style.display = "block";
        if (entitySelectorContainer) entitySelectorContainer.style.display = "flex";
        selectedEntityId = null;
        fetchPricingData(currentDomain);
      }
    });
  });

  if (entitySelect) {
    entitySelect.addEventListener("change", (e) => {
      selectedEntityId = e.target.value;
      if (currentDomain !== "all") {
        fetchPricingData(currentDomain, selectedEntityId);
      }
    });
  }

  // ==========================================================================
  // Demo Trigger Action Buttons
  // ==========================================================================
  document.getElementById("btnIncreaseDemand").addEventListener("click", () => triggerAction("increase_demand"));
  document.getElementById("btnDecreaseDemand").addEventListener("click", () => triggerAction("decrease_demand"));
  document.getElementById("btnReduceInventory").addEventListener("click", () => triggerAction("reduce_inventory"));
  document.getElementById("btnIncreaseComp").addEventListener("click", () => triggerAction("increase_competitor"));
  document.getElementById("btnDecreaseComp").addEventListener("click", () => triggerAction("decrease_competitor"));
  document.getElementById("btnSimulateBooking").addEventListener("click", () => triggerAction("simulate_booking"));
  document.getElementById("btnSimulateEvent").addEventListener("click", () => triggerAction("simulate_special_event"));
  
  document.getElementById("btnResetScenario").addEventListener("click", async () => {
    try {
      const res = await fetch("/api/simulate/reset", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ seed: 42 })
      });
      const data = await res.json();
      flashTicker("Scenario successfully reset to baseline seed 42.");
      if (currentDomain === "all") {
        fetchAllDomainsData();
      } else {
        fetchPricingData(currentDomain, selectedEntityId);
      }
    } catch (e) {
      console.error(e);
    }
  });

  btnToggleAutoTick.addEventListener("click", () => {
    isAutoTickEnabled = !isAutoTickEnabled;
    btnToggleAutoTick.textContent = isAutoTickEnabled ? "⏸ Pause Stream" : "▶ Resume Stream";
    btnToggleAutoTick.style.color = isAutoTickEnabled ? "var(--text-secondary)" : "var(--accent-amber)";
  });

  // ==========================================================================
  // API Fetch & Actions
  // ==========================================================================
  async function triggerAction(actionName) {
    const targetDomain = currentDomain === "all" ? "hotel" : currentDomain;
    const bodyPayload = { domain: targetDomain, action: actionName };
    if (currentDomain !== "all" && selectedEntityId) {
      bodyPayload.entity_id = selectedEntityId;
    }
    try {
      const res = await fetch("/api/simulate/action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(bodyPayload)
      });
      const data = await res.json();
      if (data.success) {
        flashTicker(data.action_result.description);
        if (currentDomain === "all") {
          fetchAllDomainsData();
        } else {
          renderDecision(data.pricing_decision);
        }
        fetchHealthAndTelemetry();
      }
    } catch (err) {
      console.error("Action trigger failed", err);
    }
  }

  function updateEntityDropdown(entities) {
    if (!entitySelect || !entities) return;
    entitySelect.innerHTML = "";
    entities.forEach(ent => {
      const opt = document.createElement("option");
      opt.value = ent.item_id;
      opt.textContent = `${ent.item_name} (${ent.sub_type})`;
      if (ent.item_id === selectedEntityId) {
        opt.selected = true;
      }
      entitySelect.appendChild(opt);
    });
  }

  async function fetchPricingData(domain, entityId = null) {
    try {
      let url = `/api/pricing/current?domain=${domain}`;
      if (entityId) {
        url += `&entity_id=${entityId}`;
      }
      const res = await fetch(url);
      const data = await res.json();
      if (data.success && data.result) {
        currentDecisionData = data.result;
        selectedEntityId = data.result.item_id;
        renderDecision(data.result);
        if (data.entities) {
          updateEntityDropdown(data.entities);
        }
      }
    } catch (err) {
      console.error("Failed to fetch current pricing", err);
    }
  }

  async function fetchAllDomainsData() {
    try {
      const res = await fetch("/api/pricing/current?domain=all");
      const data = await res.json();
      if (data.success && data.results) {
        allDecisionsCache = data.results;
        renderAllDomainsTable(data.results);
      }
    } catch (err) {
      console.error("Failed to fetch all domains", err);
    }
  }

  async function performTick() {
    try {
      const res = await fetch("/api/simulate/tick", { method: "POST" });
      const data = await res.json();
      if (data.success) {
        if (data.tick_data.events && data.tick_data.events.length > 0) {
          flashTicker(data.tick_data.events.join(" | "));
        }
        if (currentDomain === "all") {
          renderAllDomainsTable(data.decisions);
        } else if (data.decisions[currentDomain]) {
          renderDecision(data.decisions[currentDomain]);
        }
        fetchHealthAndTelemetry();
      }
    } catch (err) {
      console.error("Tick error", err);
    }
  }

  async function fetchHealthAndTelemetry() {
    try {
      const res = await fetch("/api/health");
      const data = await res.json();
      if (data.success && data.health) {
        renderHealthAndAlerts(data.health);
      }
    } catch (err) {
      console.error("Health fetch error", err);
    }
  }

  // ==========================================================================
  // Render Engine & Animated Updates
  // ==========================================================================
  function renderDecision(d) {
    currentDecisionData = d;

    // Trigger visual flash
    flashUpdatedCard(kpiRecPrice);
    flashUpdatedCard(calloutRecPrice);

    // KPI Values
    kpiRecPrice.textContent = `₹${d.recommended_price.toLocaleString("en-IN")}`;
    kpiCurrentPrice.textContent = `Current: ₹${d.current_price.toLocaleString("en-IN")}`;
    
    const pct = d.price_change_pct;
    priceDeltaTag.textContent = `${pct >= 0 ? "+" : ""}${pct.toFixed(1)}%`;
    priceDeltaTag.className = `kpi-tag ${pct > 0 ? "tag-success" : (pct < 0 ? "tag-amber" : "")}`;

    // Guardrail Badge
    if (d.guardrail_status.is_capped) {
      guardrailStatusBadge.textContent = `⚠ ${d.guardrail_status.cap_reason}`;
      guardrailStatusBadge.className = "guardrail-indicator capped";
      calloutGuardrailNote.textContent = d.guardrail_status.cap_reason;
    } else {
      guardrailStatusBadge.textContent = "✓ Safety Bounds Active";
      guardrailStatusBadge.className = "guardrail-indicator";
      const b = d.guardrail_status.bounds;
      calloutGuardrailNote.textContent = `Safely within bounds (₹${b.min.toLocaleString("en-IN")} – ₹${b.max.toLocaleString("en-IN")})`;
    }

    // Est. Revenue
    kpiEstRevenue.textContent = `₹${Math.round(d.recommended_estimated_revenue).toLocaleString("en-IN")}`;
    const revPct = d.estimated_revenue_impact_pct;
    kpiRevDeltaTag.textContent = `${revPct >= 0 ? "+" : ""}${revPct.toFixed(1)}%`;
    kpiRevDiff.textContent = `${d.estimated_revenue_delta >= 0 ? "+₹" : "-₹"}${Math.abs(Math.round(d.estimated_revenue_delta)).toLocaleString("en-IN")} projected`;

    // Demand
    kpiDemandScore.textContent = d.demand_score.toFixed(1);
    kpiDemandLevelTag.textContent = d.demand_level;
    demandProgressBar.style.width = `${Math.min(100, Math.max(5, d.demand_score))}%`;

    // Inventory & Capacity
    kpiInventoryRemaining.textContent = d.inventory_remaining;
    kpiTotalCapacity.textContent = `of ${d.total_capacity} total`;
    kpiOccRateTag.textContent = `${Math.round(d.occupancy_rate * 100)}% Booked`;
    inventoryProgressBar.style.width = `${Math.round(d.occupancy_rate * 100)}%`;

    // Domain-Specific Terminology Update
    const domName = (d.domain || currentDomain).toLowerCase();
    const kpiTitleScarcity = document.getElementById("kpiTitleScarcity");
    const quadLabelComp = document.getElementById("quadLabelComp");
    const quadLabelVelocity = document.getElementById("quadLabelVelocity");

    if (domName === "hotel" || domName === "hotels") {
      if (kpiTitleScarcity) kpiTitleScarcity.textContent = "Rooms & Occupancy";
      if (quadLabelComp) quadLabelComp.textContent = "Competitor Room Rate";
      if (quadLabelVelocity) quadLabelVelocity.textContent = "Booking Velocity & Conv.";
      kpiOccRateTag.textContent = `${Math.round(d.occupancy_rate * 100)}% Booked`;
      kpiTotalCapacity.textContent = `of ${d.total_capacity} rooms`;
      metricSeason.textContent = `${d.season} (${d.days_remaining}d check-in)`;
    } else if (domName === "product" || domName === "products") {
      if (kpiTitleScarcity) kpiTitleScarcity.textContent = "Stock & Inventory";
      if (quadLabelComp) quadLabelComp.textContent = "Competitor Price";
      if (quadLabelVelocity) quadLabelVelocity.textContent = "Sales Velocity & Conv.";
      kpiOccRateTag.textContent = `${d.inventory_remaining} in Stock`;
      kpiTotalCapacity.textContent = `of ${d.total_capacity} max stock`;
      metricSeason.textContent = `${d.season} (${d.days_remaining}d restock)`;
    } else if (domName === "flight" || domName === "flights") {
      if (kpiTitleScarcity) kpiTitleScarcity.textContent = "Seats & Load Factor";
      if (quadLabelComp) quadLabelComp.textContent = "Competitor Fare";
      if (quadLabelVelocity) quadLabelVelocity.textContent = "Booking Velocity & Conv.";
      kpiOccRateTag.textContent = `${Math.round(d.occupancy_rate * 100)}% Load Factor`;
      kpiTotalCapacity.textContent = `of ${d.total_capacity} seats`;
      metricSeason.textContent = `${d.season} (${d.days_remaining}d departure)`;
    } else if (domName === "travel_package" || domName === "travel_packages") {
      if (kpiTitleScarcity) kpiTitleScarcity.textContent = "Slots & Capacity";
      if (quadLabelComp) quadLabelComp.textContent = "Competitor Package Price";
      if (quadLabelVelocity) quadLabelVelocity.textContent = "Booking Velocity & Conv.";
      kpiOccRateTag.textContent = `${Math.round(d.occupancy_rate * 100)}% Slots Filled`;
      kpiTotalCapacity.textContent = `of ${d.total_capacity} slots`;
      metricSeason.textContent = `${d.season} (${d.days_remaining}d travel)`;
    }

    // Latency
    kpiLatency.innerHTML = `${d.telemetry.total_decision_latency_ms}<small>ms</small>`;
    kpiConfidence.textContent = `Conf: ${Math.round(d.confidence_score * 100)}%`;

    // Hero Entity Snapshot
    entityTitle.textContent = d.item_name;
    entitySubType.textContent = d.sub_type;
    metricCurrentPrice.textContent = `₹${d.current_price.toLocaleString("en-IN")}`;
    metricBasePrice.textContent = `Base: ₹${d.base_price.toLocaleString("en-IN")}`;
    metricCompPrice.textContent = `₹${d.competitor_price.toLocaleString("en-IN")}`;
    
    const compDiffPct = (((d.competitor_price - d.current_price) / d.current_price) * 100).toFixed(1);
    metricCompDiff.textContent = `${compDiffPct >= 0 ? "+" : ""}${compDiffPct}% vs ours`;
    
    metricVelocity.textContent = `${d.booking_velocity} /day`;
    const metricConversionEl = document.getElementById("metricConversion");
    if (metricConversionEl) metricConversionEl.textContent = `Conv. Rate: ${Math.round((d.conversion_rate || 0.35)*100)}% (Sens: ${d.price_sensitivity || 0.9})`;
    
    const metricEventEl = document.getElementById("metricEvent");
    if (metricEventEl) metricEventEl.textContent = d.special_event && d.special_event !== "Normal Day" ? `🎉 ${d.special_event}` : "Normal Day";
    
    metricSeason.textContent = `${d.season} (${d.days_remaining}d lead)`;

    calloutRecPrice.textContent = `₹${d.recommended_price.toLocaleString("en-IN")}`;
    calloutPctBadge.textContent = `${pct >= 0 ? "+" : ""}${pct.toFixed(1)}% Recommendation`;

    // XAI Explanation Header Banner
    const directionWord = pct > 0 ? "increased" : (pct < 0 ? "reduced" : "held steady");
    const signStr = pct >= 0 ? "+" : "";
    if (xaiSummaryText) {
      xaiSummaryText.innerHTML = `<strong>Recommended price ${directionWord} by ${signStr}${pct.toFixed(1)}%</strong> &mdash; ₹${d.current_price.toLocaleString("en-IN")} &rarr; ₹${d.recommended_price.toLocaleString("en-IN")}`;
    }

    renderBusinessReasons(d);
    updateCustomerLikelihood(d);

    // Update Chart
    updatePriceChart(d);
    updateElasticityChart(d);
    updateProfitCurveChart(d);
  }

  function updateCustomerLikelihood(d) {
    const likelihoodTitle = document.getElementById("likelihoodTitle");
    const likelihoodPct = document.getElementById("likelihoodPct");
    const likelihoodStatusBadge = document.getElementById("likelihoodStatusBadge");
    const likelihoodStatusText = document.getElementById("likelihoodStatusText");
    const likelihoodProgressFill = document.getElementById("likelihoodProgressFill");

    if (!likelihoodPct) return;

    const domName = (d.domain || currentDomain).toLowerCase();
    
    // Domain-appropriate title and terminology
    const isBookingDomain = domName.includes("hotel") || domName.includes("flight") || domName.includes("package");
    if (domName.includes("flight")) {
      if (likelihoodTitle) likelihoodTitle.textContent = "Passenger Booking Likelihood";
    } else if (isBookingDomain) {
      if (likelihoodTitle) likelihoodTitle.textContent = "Customer Booking Likelihood";
    } else {
      if (likelihoodTitle) likelihoodTitle.textContent = "Customer Buying Likelihood";
    }

    const verb = isBookingDomain ? "book" : "buy";

    // Signals derived from existing scenario data
    const demandScore = d.demand_score !== undefined ? d.demand_score : 50.0;
    const occRate = d.occupancy_rate !== undefined ? d.occupancy_rate : 0.75;
    const velocity = d.booking_velocity !== undefined ? d.booking_velocity : 3.5;
    const currPrice = d.current_price || d.base_price || 5000;
    const compPrice = d.competitor_price || currPrice;

    // Price competitiveness relative to competitor
    const priceDiffRatio = (compPrice - currPrice) / Math.max(currPrice, 1);
    const compFactor = Math.max(-15.0, Math.min(15.0, priceDiffRatio * 40.0));

    // Combined multi-signal score (0 to 100)
    const rawScore = (demandScore * 0.45) 
                   + (occRate * 15.0) 
                   + (Math.min(1.0, velocity / 6.0) * 15.0) 
                   + compFactor 
                   + 10.0;

    const pct = Math.round(Math.max(5, Math.min(98, rawScore)));

    likelihoodPct.textContent = `${pct}%`;
    if (likelihoodProgressFill) {
      likelihoodProgressFill.style.width = `${pct}%`;
      if (pct >= 60) {
        likelihoodProgressFill.style.background = "linear-gradient(90deg, #0ea5e9, #10b981)";
      } else if (pct >= 40) {
        likelihoodProgressFill.style.background = "linear-gradient(90deg, #38bdf8, #f59e0b)";
      } else {
        likelihoodProgressFill.style.background = "linear-gradient(90deg, #f59e0b, #ef4444)";
      }
    }

    let statusLabel = "";
    let badgeModifier = "";
    if (pct >= 80) {
      statusLabel = `Very likely to ${verb}`;
    } else if (pct >= 60) {
      statusLabel = `Likely to ${verb}`;
    } else if (pct >= 40) {
      statusLabel = "Moderate likelihood";
      badgeModifier = "badge-moderate";
    } else if (pct >= 20) {
      statusLabel = `Less likely to ${verb}`;
      badgeModifier = "badge-low";
    } else {
      statusLabel = `Unlikely to ${verb}`;
      badgeModifier = "badge-low";
    }

    if (likelihoodStatusBadge) {
      likelihoodStatusBadge.textContent = statusLabel;
      likelihoodStatusBadge.className = `likelihood-badge ${badgeModifier}`.trim();
    }
    if (likelihoodStatusText) {
      likelihoodStatusText.textContent = statusLabel;
    }
  }

  function renderBusinessReasons(d) {
    if (!xaiDriversList) return;
    xaiDriversList.innerHTML = "";

    const domName = (d.domain || currentDomain).toLowerCase();
    const compDiffPct = (((d.competitor_price - d.current_price) / d.current_price) * 100).toFixed(1);
    
    const items = [];

    // 1. Scarcity / Inventory Item
    if (domName.includes("product")) {
      items.push({
        title: "📦 Stock Availability",
        detail: `Only ${d.inventory_remaining} units in stock (${Math.round(d.occupancy_rate * 100)}% sold)`
      });
    } else if (domName.includes("flight")) {
      items.push({
        title: "📦 Seat Capacity",
        detail: `Only ${d.inventory_remaining} seats remaining (${Math.round(d.occupancy_rate * 100)}% load factor)`
      });
    } else if (domName.includes("package")) {
      items.push({
        title: "📦 Slot Availability",
        detail: `Only ${d.inventory_remaining} slots remaining (${Math.round(d.occupancy_rate * 100)}% filled)`
      });
    } else {
      items.push({
        title: "📦 Low Inventory",
        detail: `Only ${d.inventory_remaining} rooms available (${Math.round(d.occupancy_rate * 100)}% booked)`
      });
    }

    // 2. Velocity Item
    if (domName.includes("product")) {
      items.push({
        title: "📈 Sales Velocity",
        detail: `${d.booking_velocity} sales/day (Conv. Rate: ${Math.round((d.conversion_rate || 0.35)*100)}%)`
      });
    } else {
      items.push({
        title: "📈 Bookings Momentum",
        detail: `${d.booking_velocity} bookings/day (Conv. Rate: ${Math.round((d.conversion_rate || 0.35)*100)}%)`
      });
    }

    // 3. Timing / Urgency Item
    if (domName.includes("product")) {
      items.push({
        title: "⏰ Restock Schedule",
        detail: `Restock expected in ${d.days_remaining} days`
      });
    } else if (domName.includes("flight")) {
      items.push({
        title: "⏰ Departure Proximity",
        detail: `${d.days_remaining} days remaining until departure`
      });
    } else if (domName.includes("package")) {
      items.push({
        title: "⏰ Travel Date Proximity",
        detail: `${d.days_remaining} days remaining until travel date`
      });
    } else {
      items.push({
        title: "⏰ Check-in Proximity",
        detail: `${d.days_remaining} days remaining until check-in`
      });
    }

    // 4. Competitor Benchmarking Item
    const compLabel = domName.includes("flight") ? "Competitor Fare" : (domName.includes("package") ? "Competitor Package Price" : (domName.includes("product") ? "Competitor Price" : "Competitor Room Rate"));
    const compDiffStr = compDiffPct >= 0 ? `+${compDiffPct}% higher vs ours` : `${compDiffPct}% lower vs ours`;
    items.push({
      title: `🏷️ ${compLabel}`,
      detail: `Competitor price is ₹${d.competitor_price.toLocaleString("en-IN")} (${compDiffStr})`
    });

    // 5. Demand Score Item
    items.push({
      title: "📊 Market Demand Level",
      detail: `Demand score is ${d.demand_score.toFixed(1)}/100 (Level: ${d.demand_level})`
    });

    // Render cards
    items.forEach(item => {
      const card = document.createElement("div");
      card.className = "driver-row";
      card.style.display = "flex";
      card.style.justifyContent = "space-between";
      card.style.alignItems = "center";
      card.style.padding = "0.75rem 1rem";
      card.style.marginBottom = "0.5rem";
      card.style.background = "var(--bg-card-alt)";
      card.style.borderRadius = "var(--radius-md)";
      card.style.border = "1px solid var(--border-subtle)";
      
      card.innerHTML = `
        <div style="display: flex; flex-direction: column; gap: 2px;">
          <span style="font-weight: 700; font-size: 0.85rem; color: var(--text-primary);">${item.title}</span>
          <span style="font-size: 0.78rem; color: var(--text-secondary);">${item.detail}</span>
        </div>
      `;
      xaiDriversList.appendChild(card);
    });

    // 6. Dynamic Conclusion Sentence
    const conclusionEl = document.getElementById("xaiConclusionText");
    if (conclusionEl) {
      conclusionEl.innerHTML = generateConclusionText(d, domName);
    }
  }

  function generateConclusionText(d, domName) {
    const pct = d.price_change_pct;
    const reasons = [];

    // Inventory reason
    if (d.occupancy_rate >= 0.75 || d.inventory_remaining <= 5) {
      if (domName.includes("product")) reasons.push("inventory is tight");
      else if (domName.includes("flight")) reasons.push("seats are selling fast");
      else if (domName.includes("package")) reasons.push("slots are nearly filled");
      else reasons.push("inventory is becoming scarce");
    } else if (d.inventory_remaining > 15) {
      reasons.push("inventory remains high");
    }

    // Velocity reason
    if (d.booking_velocity >= 4.0) {
      reasons.push(domName.includes("product") ? "sales velocity is high" : "bookings are accelerating");
    } else if (d.booking_velocity <= 2.0) {
      reasons.push("demand velocity has slowed");
    }

    // Timing reason
    if (d.days_remaining <= 3) {
      if (domName.includes("flight")) reasons.push("departure is imminent");
      else if (domName.includes("product")) reasons.push("restock date is approaching");
      else if (domName.includes("package")) reasons.push("travel date is approaching");
      else reasons.push("check-in date is approaching");
    }

    // Competitor reason
    if (d.competitor_price > d.current_price * 1.03) {
      reasons.push("competitor pricing allows room for revenue expansion");
    } else if (d.competitor_price < d.current_price * 0.97) {
      reasons.push("competitor discounting requires parity adjustment");
    }

    if (reasons.length === 0) {
      reasons.push("market demand indicators remain balanced");
    }

    const reasonsJoined = reasons.slice(0, 3).join(", ");

    if (pct > 0) {
      return `<strong>💡 Conclusion:</strong> Model increased the price by +${pct.toFixed(1)}% because ${reasonsJoined}.`;
    } else if (pct < 0) {
      return `<strong>💡 Conclusion:</strong> Model reduced the price by ${pct.toFixed(1)}% because ${reasonsJoined}.`;
    } else {
      return `<strong>💡 Conclusion:</strong> Model maintained current pricing because ${reasonsJoined}.`;
    }
  }

  function renderAllDomainsTable(decisions) {
    allDomainsTableBody.innerHTML = "";
    const domainKeys = ["hotel", "product", "flight", "travel_package"];
    
    domainKeys.forEach(key => {
      const d = decisions[key];
      if (!d) return;

      const tr = document.createElement("tr");
      const pct = d.price_change_pct;
      const isCapped = d.guardrail_status.is_capped;

      tr.innerHTML = `
        <td><strong style="color: var(--accent-cyan); text-transform: uppercase; font-size: 0.75rem;">${d.domain}</strong></td>
        <td><strong>${d.item_name}</strong></td>
        <td style="color: var(--text-muted);">${d.sub_type}</td>
        <td>₹${d.current_price.toLocaleString("en-IN")}</td>
        <td><strong style="color: #000000; font-size: 0.95rem; font-weight: 800;">₹${d.recommended_price.toLocaleString("en-IN")}</strong></td>
        <td><span class="kpi-tag ${pct >= 0 ? "tag-success" : "tag-amber"}">${pct >= 0 ? "+" : ""}${pct.toFixed(1)}%</span></td>
        <td><span class="kpi-tag tag-cyan">${d.demand_level} (${d.demand_score.toFixed(0)})</span></td>
        <td>${d.inventory_remaining} left (${Math.round(d.occupancy_rate * 100)}%)</td>
        <td>₹${d.competitor_price.toLocaleString("en-IN")}</td>
        <td><span class="seed-pill" style="padding: 2px 6px;">${Math.round(d.confidence_score * 100)}%</span></td>
        <td>${isCapped ? `<span class="kpi-tag tag-amber" title="${d.guardrail_status.cap_reason}">Capped</span>` : `<span style="color: var(--accent-emerald);">Normal</span>`}</td>
        <td>
          <button class="btn-action-primary" style="padding: 4px 8px; font-size: 0.72rem;" onclick="window.quickAcceptDomain('${key}')">✓ Accept</button>
        </td>
      `;
      allDomainsTableBody.appendChild(tr);
    });
  }

  function renderHealthAndAlerts(health) {
    const healthStatusEl = document.getElementById("healthStatusText");
    if (healthStatusEl) healthStatusEl.textContent = health.status;
    
    // Alerts
    alertsList.innerHTML = "";
    if (health.active_alerts && health.active_alerts.length > 0) {
      health.active_alerts.forEach(a => {
        const item = document.createElement("div");
        item.className = `alert-item ${a.level.toLowerCase()}`;
        item.innerHTML = `
          <span>${a.message}</span>
          <span class="alert-time">${a.timestamp}</span>
        `;
        alertsList.appendChild(item);
      });
    } else {
      alertsList.innerHTML = '<div class="empty-alerts">All systems operating within normal safety bounds.</div>';
    }

    // Audit Log
    if (health.audit_log && health.audit_log.length > 0) {
      auditTableBody.innerHTML = "";
      health.audit_log.forEach(log => {
        const row = document.createElement("tr");
        const actionColor = log.action === "ACCEPT" ? "var(--accent-emerald)" : (log.action === "OVERRIDE" ? "var(--accent-cyan)" : "var(--accent-rose)");
        const timeDisplay = log.timestamp_ist || (function() {
          try {
            const raw = log.timestamp.replace(" UTC", "Z").replace(" ", "T");
            return new Date(raw).toLocaleTimeString("en-IN", { timeZone: "Asia/Kolkata", hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true });
          } catch(e) {
            return log.timestamp;
          }
        })();
        row.innerHTML = `
          <td style="font-family: var(--font-mono); color: var(--text-muted);">${log.id}</td>
          <td style="font-family: var(--font-mono);">${timeDisplay}</td>
          <td style="text-transform: capitalize;">${log.domain}</td>
          <td>${log.item_name}</td>
          <td>₹${log.recommended_price.toLocaleString("en-IN")}</td>
          <td><strong>₹${log.final_price.toLocaleString("en-IN")}</strong></td>
          <td><strong style="color: ${actionColor}">${log.action}</strong></td>
          <td style="color: var(--text-muted); font-size: 0.72rem;">${log.reason}</td>
        `;
        auditTableBody.appendChild(row);
      });
    }
  }

  function flashTicker(text) {
    eventTickerText.textContent = text;
    const ticker = document.getElementById("eventTicker");
    ticker.style.transition = "background-color 0.2s ease";
    ticker.style.backgroundColor = "rgba(6, 182, 212, 0.2)";
    setTimeout(() => {
      ticker.style.backgroundColor = "rgba(0, 0, 0, 0.25)";
    }, 600);
  }

  function flashUpdatedCard(el) {
    if (!el) return;
    el.classList.remove("cell-updated");
    void el.offsetWidth; // trigger reflow
    el.classList.add("cell-updated");
  }

  // ==========================================================================
  // Charts Implementation
  // ==========================================================================
  function initCharts() {
    const ctxPrice = document.getElementById("priceTrendChart").getContext("2d");
    priceChartInstance = new Chart(ctxPrice, {
      type: "line",
      data: {
        labels: [],
        datasets: [
          {
            label: "Recommended Price (₹)",
            borderColor: "#06b6d4",
            backgroundColor: "rgba(6, 182, 212, 0.1)",
            borderWidth: 2.5,
            fill: true,
            tension: 0.35,
            data: []
          },
          {
            label: "Competitor Benchmark (₹)",
            borderColor: "#f59e0b",
            borderDash: [5, 5],
            borderWidth: 2,
            fill: false,
            tension: 0.35,
            data: []
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            labels: { color: "#94a3b8", font: { family: "'Plus Jakarta Sans', sans-serif", size: 11 } }
          }
        },
        scales: {
          x: { grid: { color: "#192742" }, ticks: { color: "#64748b", font: { size: 10 } } },
          y: { grid: { color: "#192742" }, ticks: { color: "#64748b", font: { size: 10 } } }
        }
      }
    });

    const ctxElasticity = document.getElementById("elasticityChart").getContext("2d");
    elasticityChartInstance = new Chart(ctxElasticity, {
      type: "line",
      data: {
        labels: [],
        datasets: [
          {
            label: "Observed Demand",
            borderColor: "#3b82f6",
            backgroundColor: "rgba(59, 130, 246, 0.1)",
            borderWidth: 2.5,
            fill: true,
            tension: 0.35,
            data: []
          },
          {
            label: "Predicted Demand",
            borderColor: "#a855f7",
            borderDash: [5, 5],
            borderWidth: 2,
            fill: false,
            tension: 0.35,
            data: []
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            labels: { color: "#94a3b8", font: { family: "'Plus Jakarta Sans', sans-serif", size: 11 } }
          }
        },
        scales: {
          x: { grid: { color: "#192742" }, ticks: { color: "#64748b", font: { size: 10 } } },
          y: { grid: { color: "#192742" }, ticks: { color: "#64748b", font: { size: 10 } }, min: 0, max: 100 }
        }
      }
    });

    const ctxProfit = document.getElementById("profitComparisonChart").getContext("2d");
    
    const profitBarLabelsPlugin = {
      id: "profitBarValueLabels",
      afterDatasetsDraw(chart) {
        const { ctx, data } = chart;
        const meta = chart.getDatasetMeta(0);
        if (!meta || !meta.data) return;
        meta.data.forEach((bar, index) => {
          const val = data.datasets[0].data[index];
          if (val !== undefined && val !== null) {
            ctx.save();
            ctx.font = "bold 13px 'Plus Jakarta Sans', sans-serif";
            ctx.fillStyle = "#000000";
            ctx.textAlign = "center";
            ctx.textBaseline = "bottom";
            const formatted = "₹" + Math.round(val).toLocaleString("en-IN");
            ctx.fillText(formatted, bar.x, bar.y - 6);
            ctx.restore();
          }
        });
      }
    };

    profitChartInstance = new Chart(ctxProfit, {
      type: "bar",
      plugins: [profitBarLabelsPlugin],
      data: {
        labels: ["Current Price", "Recommended Price"],
        datasets: [
          {
            label: "Estimated Profit (₹)",
            data: [0, 0],
            backgroundColor: ["rgba(56, 189, 248, 0.85)", "rgba(16, 185, 129, 0.85)"],
            borderColor: ["#0284c7", "#059669"],
            borderWidth: 1.5,
            borderRadius: 8,
            maxBarThickness: 100
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            callbacks: {
              title: function(items) {
                if (!items.length) return "";
                return items[0].label;
              },
              label: function(context) {
                const val = context.parsed.y;
                const idx = context.dataIndex;
                const prefix = idx === 0 ? "Current Price Profit: " : "Recommended Profit: ";
                return `${prefix}₹${Math.round(val).toLocaleString("en-IN")}`;
              },
              afterLabel: function(context) {
                const idx = context.dataIndex;
                if (idx === 1 && currentDecisionData) {
                  const qCurr = currentDecisionData.expected_demand_units_current || 2.0;
                  const qRec = currentDecisionData.expected_demand_units_recommended || 2.0;
                  const unitCost = (currentDecisionData.base_price || 5000) * 0.45;
                  const currProf = Math.max(0, Math.round((currentDecisionData.current_estimated_revenue || (currentDecisionData.current_price * qCurr)) - (unitCost * qCurr)));
                  const recProf = Math.max(0, Math.round((currentDecisionData.recommended_estimated_revenue || (currentDecisionData.recommended_price * qRec)) - (unitCost * qRec)));
                  const diff = recProf - currProf;
                  if (diff > 0) {
                    return `▲ +₹${diff.toLocaleString("en-IN")} higher estimated profit outcome`;
                  } else if (diff < 0) {
                    return `▼ -₹${Math.abs(diff).toLocaleString("en-IN")} difference`;
                  } else {
                    return "Equal estimated profit outcome";
                  }
                }
                return null;
              }
            }
          }
        },
        scales: {
          x: {
            title: {
              display: true,
              text: "Pricing Option",
              color: "#000000",
              font: { family: "'Plus Jakarta Sans', sans-serif", size: 12, weight: "700" }
            },
            grid: { color: "#e2e8f0" },
            ticks: { color: "#000000", font: { size: 12, weight: "700" } }
          },
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: "Estimated Profit (₹)",
              color: "#000000",
              font: { family: "'Plus Jakarta Sans', sans-serif", size: 12, weight: "700" }
            },
            grid: { color: "#e2e8f0" },
            ticks: {
              color: "#000000",
              font: { size: 11, weight: "600" },
              callback: function(value) {
                return "₹" + Number(value).toLocaleString("en-IN");
              }
            }
          }
        }
      }
    });
  }

  function updatePriceChart(d) {
    const timeLabel = new Date().toLocaleTimeString().split(" ")[0];
    if (historyTimestamps.length > 10) {
      historyTimestamps.shift();
      historyOurPrices.shift();
      historyCompPrices.shift();
    }
    historyTimestamps.push(timeLabel);
    historyOurPrices.push(d.recommended_price);
    historyCompPrices.push(d.competitor_price);

    priceChartInstance.data.labels = historyTimestamps;
    priceChartInstance.data.datasets[0].data = historyOurPrices;
    priceChartInstance.data.datasets[1].data = historyCompPrices;
    priceChartInstance.update("none");
  }

  function updateElasticityChart(d) {
    const timeLabel = new Date().toLocaleTimeString().split(" ")[0];
    if (demandHistoryTimestamps.length > 10) {
      demandHistoryTimestamps.shift();
      historyObservedDemand.shift();
      historyPredictedDemand.shift();
    }

    const observedVal = Math.min(100, Math.round((d.booking_velocity / 12.0) * 100));
    const predictedVal = Math.min(100, Math.round(d.demand_score));

    demandHistoryTimestamps.push(timeLabel);
    historyObservedDemand.push(observedVal);
    historyPredictedDemand.push(predictedVal);

    elasticityChartInstance.data.labels = demandHistoryTimestamps;
    elasticityChartInstance.data.datasets[0].data = historyObservedDemand;
    elasticityChartInstance.data.datasets[1].data = historyPredictedDemand;
    elasticityChartInstance.update("none");
  }

  function updateProfitCurveChart(d) {
    if (!profitChartInstance) return;

    const basePrice = d.base_price || 5000;
    const unitCost = basePrice * 0.45;
    const qCurr = d.expected_demand_units_current || 2.0;
    const qRec = d.expected_demand_units_recommended || 2.0;

    const currRevenue = d.current_estimated_revenue !== undefined ? d.current_estimated_revenue : (d.current_price * qCurr);
    const recRevenue = d.recommended_estimated_revenue !== undefined ? d.recommended_estimated_revenue : (d.recommended_price * qRec);

    const currProfit = Math.max(0, Math.round(currRevenue - (unitCost * qCurr)));
    const recProfit = Math.max(0, Math.round(recRevenue - (unitCost * qRec)));

    const labels = [
      `Current Price (₹${d.current_price.toLocaleString("en-IN")})`,
      `Recommended Price (₹${d.recommended_price.toLocaleString("en-IN")})`
    ];

    profitChartInstance.data.labels = labels;
    profitChartInstance.data.datasets[0].data = [currProfit, recProfit];

    const maxVal = Math.max(currProfit, recProfit, 100);
    profitChartInstance.options.scales.y.suggestedMax = Math.round(maxVal * 1.22);

    profitChartInstance.update("none");
  }

  // ==========================================================================
  // Timer Loop for Auto-ticks
  // ==========================================================================
  function startTimerLoop() {
    timerInterval = setInterval(() => {
      if (isAutoTickEnabled) {
        tickCountdownSec -= 1;
        if (tickCountdownSec <= 0) {
          tickCountdownSec = 3;
          performTick();
        }
        tickCountdownEl.textContent = `${tickCountdownSec}s`;
      }
    }, 1000);
  }

  // ==========================================================================
  // Human Override Modal & Handlers
  // ==========================================================================
  btnOpenOverrideModal.addEventListener("click", () => {
    if (!currentDecisionData) return;
    modalDomainLabel.textContent = currentDecisionData.domain;
    modalItemName.textContent = currentDecisionData.item_name;
    modalCurrentPrice.textContent = `₹${currentDecisionData.current_price.toLocaleString("en-IN")}`;
    modalRecPrice.textContent = `₹${currentDecisionData.recommended_price.toLocaleString("en-IN")}`;
    customPriceInput.value = currentDecisionData.recommended_price;
    overrideModal.classList.add("active");
  });

  const closeModal = () => overrideModal.classList.remove("active");
  btnCloseModal.addEventListener("click", closeModal);
  btnCancelModal.addEventListener("click", closeModal);

  overrideActionSelect.addEventListener("change", (e) => {
    customPriceGroup.style.display = e.target.value === "OVERRIDE" ? "block" : "none";
  });

  overrideForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!currentDecisionData) return;

    const action = overrideActionSelect.value;
    let finalPrice = currentDecisionData.recommended_price;

    if (action === "REJECT") {
      finalPrice = currentDecisionData.current_price;
    } else if (action === "OVERRIDE") {
      finalPrice = parseFloat(customPriceInput.value) || currentDecisionData.recommended_price;
    }

    const payload = {
      domain: currentDecisionData.domain,
      item_id: currentDecisionData.item_id,
      item_name: currentDecisionData.item_name,
      current_price: currentDecisionData.current_price,
      recommended_price: currentDecisionData.recommended_price,
      final_price: finalPrice,
      action: action,
      reason: overrideReasonInput.value || "Manager manual override"
    };

    try {
      const res = await fetch("/api/pricing/override", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data.success) {
        closeModal();
        flashTicker(`Manager action recorded: ${action} for ${currentDecisionData.item_name} at ₹${finalPrice.toLocaleString("en-IN")}`);
        fetchHealthAndTelemetry();
      }
    } catch (err) {
      console.error(err);
    }
  });

  // Quick Accept / Reject from card
  btnQuickAccept.addEventListener("click", async () => {
    if (!currentDecisionData) return;
    await submitQuickDecision("ACCEPT", currentDecisionData.recommended_price, "Fast-approved by pricing manager");
  });

  btnQuickReject.addEventListener("click", async () => {
    if (!currentDecisionData) return;
    await submitQuickDecision("REJECT", currentDecisionData.current_price, "Rejected recommendation; held current price");
  });

  async function submitQuickDecision(action, finalPrice, reason) {
    const payload = {
      domain: currentDecisionData.domain,
      item_id: currentDecisionData.item_id,
      item_name: currentDecisionData.item_name,
      current_price: currentDecisionData.current_price,
      recommended_price: currentDecisionData.recommended_price,
      final_price: finalPrice,
      action: action,
      reason: reason
    };

    try {
      const res = await fetch("/api/pricing/override", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data.success) {
        flashTicker(`Logged ${action}: Final price ₹${finalPrice.toLocaleString("en-IN")}`);
        showDecisionToast(action);
        fetchHealthAndTelemetry();
      }
    } catch (e) {
      console.error(e);
    }
  }

  function showDecisionToast(action) {
    let toast = document.getElementById("quickDecisionToast");
    const container = document.querySelector(".quick-override-buttons");
    if (!container) return;

    if (!toast) {
      toast = document.createElement("div");
      toast.id = "quickDecisionToast";
      toast.style.cssText = `
        position: absolute;
        top: -38px;
        right: 0;
        padding: 5px 12px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 700;
        white-space: nowrap;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.4);
        z-index: 100;
        transition: opacity 0.3s ease, transform 0.3s ease;
      `;
      container.style.position = "relative";
      container.appendChild(toast);
    }

    if (action === "ACCEPT") {
      toast.style.background = "rgba(16, 185, 129, 0.95)";
      toast.style.color = "#0f172a";
      toast.innerHTML = "✓ Price accepted and added to log";
    } else if (action === "REJECT") {
      toast.style.background = "rgba(244, 63, 94, 0.95)";
      toast.style.color = "#ffffff";
      toast.innerHTML = "✕ Price rejected and added to log";
    } else {
      toast.style.background = "rgba(6, 182, 212, 0.95)";
      toast.style.color = "#0f172a";
      toast.innerHTML = "✓ Decision recorded and added to log";
    }

    toast.style.display = "block";
    toast.style.opacity = "1";
    toast.style.transform = "translateY(0)";

    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateY(-4px)";
      setTimeout(() => {
        toast.style.display = "none";
      }, 300);
    }, 1500);
  }

  // Global helper for table accept
  window.quickAcceptDomain = async function(domKey) {
    const d = allDecisionsCache[domKey];
    if (!d) return;
    const payload = {
      domain: d.domain,
      item_id: d.item_id,
      item_name: d.item_name,
      current_price: d.current_price,
      recommended_price: d.recommended_price,
      final_price: d.recommended_price,
      action: "ACCEPT",
      reason: "Approved from multi-domain table matrix"
    };
    try {
      await fetch("/api/pricing/override", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      flashTicker(`Matrix Approved: ${d.item_name} set to ₹${d.recommended_price.toLocaleString("en-IN")}`);
      fetchHealthAndTelemetry();
    } catch (e) {
      console.error(e);
    }
  };
});
