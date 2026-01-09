# Decision Foresight Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     PORTFOLIO SENTINEL SYSTEM                        │
│                 VC Portfolio Risk Intelligence Platform              │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         DATA LAYER (Phase 1-4)                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  15 Startups (45-60 days operational history each)                  │
│  ├─ Post-Hype Collapse (3): Lumina, Quantum, Strata                │
│  ├─ Silent Failure (3): Nexus, Beacon, Frontier                    │
│  ├─ Zombie (2): Atlas, WaveGrid                                    │
│  ├─ False Recovery (2): Aurora, Nova                               │
│  ├─ True Turnaround (2): Helix, Pioneer                            │
│  └─ Consistent Winner (3): Verde, Cipher, TerraSense              │
│                                                                      │
│  Metrics per startup (daily):                                       │
│  • commit_count, tasks_completed, tasks_missed                     │
│  • morale_score, response_time_hours, burn_rate_k                  │
│  • market_sentiment_score                                          │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   FEATURE ENGINEERING (Phase 1)                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  backend/feature_engineering.py                                     │
│  ├─ Rolling averages (7-day commit velocity)                       │
│  ├─ Task miss rate computation                                     │
│  ├─ Morale trend (linear regression slope)                         │
│  ├─ Response time normalization (z-scores)                         │
│  ├─ Spend dynamics (% change)                                      │
│  └─ Execution health score (composite)                             │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      RISK MODEL (Phase 1)                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  backend/risk_model.py                                              │
│  ├─ Isolation Forest (anomaly detection)                           │
│  ├─ Component scoring (execution 35%, team 25%,                    │
│  │                       anomaly 25%, spend 15%)                    │
│  ├─ Daily risk scores (0-100 scale)                                │
│  └─ Trend analysis (7-day slope)                                   │
│                                                                      │
│  Output: risk_score, severity (low/medium/high), trend (up/down)   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  REASONING LAYER (Phase 3)                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  backend/reasoning/                                                 │
│  ├─ Azure OpenAI (GPT-4, temp=0.3)                                 │
│  ├─ Investor-grade explanations:                                   │
│  │   • Why this risk matters                                       │
│  │   • What typically happens next                                 │
│  │   • Recommended investor action                                 │
│  └─ Deterministic caching (hash-based)                             │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                                  │
              ┌───────────────────┴───────────────────┐
              ▼                                       ▼
┌──────────────────────────────┐    ┌──────────────────────────────┐
│   TIME SNAPSHOTS (Phase 5)   │    │   SCENARIOS (Phase 5)        │
├──────────────────────────────┤    ├──────────────────────────────┤
│                              │    │                              │
│  backend/intelligence/       │    │  backend/intelligence/       │
│  time_snapshots.py           │    │  scenarios.py                │
│                              │    │                              │
│  Historical risk at:         │    │  Three trajectories:         │
│  • 60 days ago               │    │  • no_intervention           │
│  • 45 days ago               │    │  • early_intervention        │
│  • 30 days ago               │    │  • delayed_intervention      │
│  • 14 days ago               │    │                              │
│  • 7 days ago                │    │  Each with adjusted:         │
│  • Today (0 days ago)        │    │  • morale, velocity          │
│                              │    │  • task completion           │
│  + Causality markers:        │    │  • recomputed risk           │
│  • First risk detected       │    │                              │
│  • Lead time to high risk    │    │                              │
│  • Trajectory type           │    │                              │
│                              │    │                              │
└──────────────────────────────┘    └──────────────────────────────┘
              │                                       │
              └───────────────────┬───────────────────┘
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                 DECISION FORESIGHT (Phase 6) ✨ NEW                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  backend/intelligence/foresight.py                                  │
│                                                                      │
│  Inputs:                                                            │
│  ├─ Current risk snapshot (risk_score, severity, trend)            │
│  ├─ Historical snapshots (for velocity & confidence)               │
│  ├─ Causality markers (trajectory, first detection)                │
│  ├─ Startup archetype (post_hype_collapse, silent_failure, etc.)   │
│  └─ Intervention scenario (no/early/delayed)                       │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ 1. DECISION WINDOW                                           │  │
│  │    compute_decision_window()                                 │  │
│  │                                                              │  │
│  │    Logic:                                                    │  │
│  │    • Calculate risk velocity from snapshots                 │  │
│  │    • Map (severity, velocity, archetype) → time range       │  │
│  │                                                              │  │
│  │    Output:                                                   │  │
│  │    {                                                         │  │
│  │      days_min: 7,                                           │  │
│  │      days_max: 14,                                          │  │
│  │      description: "Risk likely to escalate within ~7–14     │  │
│  │                    days if conditions persist"              │  │
│  │    }                                                         │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ 2. URGENCY CLASSIFICATION                                    │  │
│  │    compute_decision_urgency()                                │  │
│  │                                                              │  │
│  │    Logic (independent of risk score alone):                 │  │
│  │    • CRITICAL: high severity + collapse/failure archetype   │  │
│  │    • HIGH: high severity OR (medium + bad archetype)        │  │
│  │    • MEDIUM: medium severity OR deteriorating + velocity>2  │  │
│  │    • LOW: standard monitoring sufficient                    │  │
│  │                                                              │  │
│  │    Output: "HIGH"                                           │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ 3. CONFIDENCE FRAMING                                        │  │
│  │    compute_confidence_framing()                              │  │
│  │                                                              │  │
│  │    Criteria:                                                 │  │
│  │    • Snapshot count (5+ = high confidence)                  │  │
│  │    • Trajectory clarity (clear = higher confidence)         │  │
│  │    • Archetype known (known = higher confidence)            │  │
│  │                                                              │  │
│  │    Output:                                                   │  │
│  │    {                                                         │  │
│  │      level: "High",                                         │  │
│  │      rationale: "Pattern repeated historically across       │  │
│  │                  comparable portfolio companies"            │  │
│  │    }                                                         │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ 4. REVERSIBILITY MARKER                                      │  │
│  │    compute_reversibility_marker()                            │  │
│  │                                                              │  │
│  │    Markers (honest, unbiased):                              │  │
│  │    • DIMINISHED: late intervention, limited impact          │  │
│  │    • VIABLE: early intervention likely effective            │  │
│  │    • NARROWING: window closing, urgency increasing          │  │
│  │    • OPTIMAL: best intervention point                       │  │
│  │    • CONSTRAINED: possible but costly                       │  │
│  │    • ACCELERATIVE: support compounds momentum               │  │
│  │    • PREVENTIVE: primarily preventive                       │  │
│  │                                                              │  │
│  │    Output:                                                   │  │
│  │    {                                                         │  │
│  │      marker: "VIABLE",                                      │  │
│  │      description: "Intervention still likely to materially  │  │
│  │                    alter outcome",                          │  │
│  │      explanation: "Operational reset achievable with        │  │
│  │                    focused advisory support..."             │  │
│  │    }                                                         │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ 5. ORCHESTRATION                                             │  │
│  │    compute_foresight_intelligence()                          │  │
│  │                                                              │  │
│  │    Combines all signals into single payload:                │  │
│  │    {                                                         │  │
│  │      decisionWindow: {...},                                 │  │
│  │      urgency: "HIGH",                                       │  │
│  │      confidence: {...},                                     │  │
│  │      reversibility: {...},                                  │  │
│  │      velocityIndicator: "Accelerating decline"             │  │
│  │    }                                                         │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      API RESPONSE (Phase 2-6)                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  GET /api/startups/{id}?include_intelligence=true                   │
│                                                                      │
│  {                                                                   │
│    "id": "1",                                                        │
│    "name": "Lumina Health",                                         │
│    "riskScore": 72.4,                                               │
│    "severity": "high",                                              │
│    "aiInsight": {                                                   │
│      "whyItMatters": "...",         ← Azure OpenAI reasoning        │
│      "whatHappensNext": "...",                                      │
│      "recommendedAction": "..."                                     │
│    },                                                               │
│    "intelligence": {                                                │
│      "timeSnapshots": [...],        ← Historical risk evolution     │
│      "causalityMarkers": {...},     ← When risk first detected      │
│      "interventionScenarios": {...},← No/early/delayed outcomes     │
│      "foresight": {                 ← ✨ NEW: Decision signals      │
│        "no_intervention": {                                         │
│          "decisionWindow": {...},   ← Time available                │
│          "urgency": "HIGH",         ← Priority level                │
│          "confidence": {...},       ← Signal reliability            │
│          "reversibility": {...},    ← Intervention viability        │
│          "velocityIndicator": "..." ← Trajectory description        │
│        },                                                           │
│        "early_intervention": {...}, ← Same signals, better outlook  │
│        "delayed_intervention": {...}← Same signals, worse outlook   │
│      }                                                              │
│    }                                                                │
│  }                                                                   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  DECISION USE CASES                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. INVESTMENT COMMITTEE BRIEFING                                   │
│     ┌────────────────────────────────────────────────────────┐     │
│     │ Lumina Health (Healthcare)                             │     │
│     │ Risk: 72.4 (High) | Urgency: HIGH | Window: 7-14 days │     │
│     │                                                        │     │
│     │ Decision: VIABLE reversibility with early intervention│     │
│     │ Action: Deploy advisory team this week                │     │
│     │ Confidence: High (60-day consistent trajectory)       │     │
│     └────────────────────────────────────────────────────────┘     │
│                                                                      │
│  2. PORTFOLIO TRIAGE                                                │
│     ┌────────────────────────────────────────────────────────┐     │
│     │ Sort by urgency:                                       │     │
│     │ 1. CRITICAL (Strata AI) → Immediate action            │     │
│     │ 2. HIGH (Lumina, Quantum) → This week                 │     │
│     │ 3. MEDIUM (Nexus, Beacon) → Next 2 weeks             │     │
│     │ 4. LOW (Verde, Cipher) → Standard monitoring          │     │
│     └────────────────────────────────────────────────────────┘     │
│                                                                      │
│  3. SCENARIO COMPARISON                                             │
│     ┌────────────────────────────────────────────────────────┐     │
│     │              No Interv  │  Early Interv │ Delayed      │     │
│     │ Urgency      HIGH       │  MEDIUM ↓    │ CRITICAL ↑  │     │
│     │ Window       7-14 days  │  14-21 ↑     │ 0-7 ↓       │     │
│     │ Reversibility NARROWING │  VIABLE ↑    │ DIMINISHED ↓│     │
│     │                                                        │     │
│     │ Conclusion: Early intervention materially improves     │     │
│     │             outlook and extends decision window        │     │
│     └────────────────────────────────────────────────────────┘     │
│                                                                      │
│  4. RESOURCE ALLOCATION                                             │
│     ┌────────────────────────────────────────────────────────┐     │
│     │ Focus intervention on:                                 │     │
│     │ • Reversibility: OPTIMAL or VIABLE                     │     │
│     │ • Urgency: MEDIUM or HIGH                              │     │
│     │ • Confidence: High                                     │     │
│     │                                                        │     │
│     │ Result: Aurora, Helix, Pioneer (intervention-ready)   │     │
│     └────────────────────────────────────────────────────────┘     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                        KEY DESIGN PRINCIPLES                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ✓ NO PREDICTION: Bounded estimates, not point forecasts           │
│  ✓ NO PROBABILITIES: Descriptive confidence, not numeric scores    │
│  ✓ DETERMINISTIC: Seeded computation, fully reproducible           │
│  ✓ CACHED: Precomputed at startup, zero per-request overhead       │
│  ✓ HONEST: "DIMINISHED" reversibility when intervention won't work │
│  ✓ DECISION-GRADE: Language suitable for investment memos          │
│  ✓ SCENARIO-AWARE: Compare no/early/delayed intervention           │
│  ✓ ARCHETYPE-INFORMED: Calibrated by realistic failure patterns    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         PHASE TIMELINE                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Phase 1: Core Risk Intelligence (feature eng, risk model, utils)  │
│  Phase 2: Full-Stack Separation (frontend/backend, REST API)       │
│  Phase 3: Azure OpenAI Reasoning (investor-grade explanations)     │
│  Phase 4: Portfolio Expansion (15 startups, realistic archetypes)  │
│  Phase 5: Time & Scenario Intelligence (snapshots, causality)      │
│  Phase 6: Decision Foresight ✨ (urgency, windows, reversibility)  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## File Structure

```
Imagine-Cup/
├── backend/
│   ├── api/
│   │   ├── routes.py           (✏️ Modified: +17 lines for foresight)
│   │   └── main.py
│   ├── intelligence/
│   │   ├── __init__.py         (✏️ Modified: +1 export)
│   │   ├── foresight.py        (✨ NEW: 329 lines)
│   │   ├── time_snapshots.py
│   │   └── scenarios.py
│   ├── reasoning/
│   │   ├── client.py
│   │   ├── orchestrator.py
│   │   └── prompts.py
│   ├── feature_engineering.py
│   ├── risk_model.py
│   └── portfolio_utils.py
│
├── frontend/
│   └── src/
│       ├── services/
│       │   └── api.ts
│       ├── types/
│       │   └── risk.ts
│       └── pages/
│           └── Index.tsx
│
├── PHASE_6_DELIVERY.md         (✨ NEW: This file)
├── PHASE_6_FORESIGHT_SUMMARY.md (✨ NEW: Technical details)
├── FORESIGHT_API_REFERENCE.md   (✨ NEW: API documentation)
├── FORESIGHT_ARCHITECTURE.md    (✨ NEW: Visual diagrams)
└── README.md
```

## Data Flow

```
Operational Metrics
      │
      ▼
Feature Engineering (7-day rolling, miss rate, morale trend)
      │
      ▼
Risk Model (Isolation Forest + weighted scoring)
      │
      ├─────────────────┬─────────────────┐
      ▼                 ▼                 ▼
Time Snapshots    Azure OpenAI      Intervention Scenarios
(60→0 days)       (Reasoning)       (no/early/delayed)
      │                 │                 │
      └─────────────────┴─────────────────┘
                        │
                        ▼
              Decision Foresight ✨
              (urgency, windows, confidence, reversibility)
                        │
                        ▼
              API Response (JSON)
                        │
                        ▼
              Investment Committee Dashboard
```

## Quick Start

### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 2. Test Foresight
```bash
# Get foresight for Lumina Health (post-hype collapse)
curl http://localhost:8000/api/startups/1?include_intelligence=true | \
  jq '.intelligence.foresight.no_intervention'
```

### 3. Expected Output
```json
{
  "decisionWindow": {
    "days_min": 7,
    "days_max": 14,
    "description": "Risk likely to escalate further within ~7–14 days if conditions persist"
  },
  "urgency": "HIGH",
  "confidence": {
    "level": "High",
    "rationale": "Pattern repeated historically across comparable portfolio companies"
  },
  "reversibility": {
    "marker": "NARROWING",
    "description": "Intervention window closing; action urgency increasing",
    "explanation": "Current trajectory leads to compounding dysfunction. Intervention remains viable but effectiveness declining with each passing week."
  },
  "velocityIndicator": "Accelerating decline"
}
```

---

**Phase 6 Complete** ✅  
All backend integration finished. Frontend UI pending.
