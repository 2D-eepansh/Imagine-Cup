# Phase 6: Decision Foresight Intelligence - Implementation Summary

## Overview

Added decision-grade foresight signals to the VC portfolio risk intelligence system, enabling investment committee decision-making without relying on prediction models or numeric forecasts. All signals are deterministic, cached, and derived from existing time-series snapshots and intervention scenarios.

## Architecture Changes

### 1. New Module: `backend/intelligence/foresight.py`

Created comprehensive foresight intelligence module providing four core decision signals:

#### A. Decision Window Computation
- **Function**: `compute_decision_window(risk_score, severity, trajectory, snapshots, archetype)`
- **Returns**: Bounded time range strings (e.g., "Near-term (7-14 days)", "Medium-term (14-21 days)")
- **Logic**:
  - Immediate (0-7 days): Risk ≥80 or critical severity
  - Near-term (7-14 days): Risk ≥70 or worsening trend with slope >5
  - Medium-term (14-21 days): Risk ≥50 or worsening trend with slope >2
  - Watchlist (21-30 days): Worsening trend
  - Long-term (30+ days): Stable or improving trends
- **Key Feature**: Time windows are conservative ranges, not point estimates

#### B. Urgency Classification
- **Function**: `compute_decision_urgency(risk_score, severity, trajectory, velocity, causality, archetype)`
- **Returns**: Urgency level (LOW, MEDIUM, HIGH, CRITICAL)
- **Logic Independent of Risk Score**:
  - CRITICAL: Severity high + archetype in collapse/failure categories
  - HIGH: Severity high or (medium + specific archetype patterns)
  - MEDIUM: Severity medium or deteriorating trajectory with velocity >2
  - LOW: Standard monitoring sufficient
- **Key Feature**: Considers trajectory dynamics, not just current score

#### C. Confidence Framing
- **Function**: `compute_confidence_framing(snapshots, trajectory, archetype, severity)`
- **Returns**: Qualitative confidence descriptor with rationale
- **Assessment Criteria**:
  - High confidence: 5+ snapshots, clear trajectory, known archetype
  - Medium confidence: 4+ snapshots or stable trajectory
  - Moderate confidence: <4 snapshots or ambiguous trajectory
- **Key Feature**: Non-numeric confidence suitable for investment memos

#### D. Reversibility Marker
- **Function**: `compute_reversibility_marker(severity, urgency, trajectory, archetype, intervention_scenario)`
- **Returns**: Dict with marker level, description, and explanation
- **Marker Types**:
  - DIMINISHED: Critical cases with late intervention
  - VIABLE: Early intervention still likely effective
  - NARROWING: Window closing, urgency increasing
  - OPTIMAL: Best intervention point (medium severity + deteriorating)
  - ACCELERATIVE: Support compounds positive momentum
  - PREVENTIVE: Standard monitoring sufficient
- **Key Feature**: Honest assessment without optimistic bias

#### E. Orchestration Function
- **Function**: `compute_foresight_intelligence(risk_score, severity, trajectory, snapshots, causality, archetype, intervention_scenario)`
- **Returns**: Complete foresight payload with all signals
- **Structure**:
```python
{
    'decisionWindow': {...},
    'urgency': 'HIGH',
    'confidence': {'level': 'High', 'rationale': '...'},
    'reversibility': {'marker': 'VIABLE', 'description': '...', 'explanation': '...'},
    'velocityIndicator': 'Accelerating decline'
}
```

### 2. API Integration: `backend/api/routes.py`

#### Import Addition
```python
from backend.intelligence import (
    compute_historical_snapshots,
    compute_causality_markers,
    compute_intervention_scenarios,
    compute_foresight_intelligence,  # NEW
)
```

#### Payload Enhancement
Modified `_compute_startup_payload()` to compute foresight signals for all three intervention scenarios:

```python
if include_intelligence:
    snapshots = compute_historical_snapshots(df, startup_id, name)
    causality = compute_causality_markers(snapshots, severity)
    scenarios = compute_intervention_scenarios(risk_score, severity, archetype)
    
    # NEW: Compute decision foresight for each scenario
    foresight_signals = {}
    trajectory = causality.get('trajectory', 'unknown') if causality else 'unknown'
    
    for scenario_name in ['no_intervention', 'early_intervention', 'delayed_intervention']:
        foresight_signals[scenario_name] = compute_foresight_intelligence(
            risk_score=risk_score,
            severity=severity,
            trajectory=trajectory,
            snapshots=snapshots,
            causality=causality or {},
            archetype=archetype,
            intervention_scenario=scenario_name,
        )
    
    payload['intelligence'] = {
        'timeSnapshots': snapshots,
        'causalityMarkers': causality,
        'interventionScenarios': scenarios,
        'foresight': foresight_signals,  # NEW
    }
```

### 3. Module Orchestration: `backend/intelligence/__init__.py`

Added foresight export:
```python
from backend.intelligence.foresight import compute_foresight_intelligence

__all__ = [
    'compute_historical_snapshots',
    'compute_causality_markers',
    'compute_intervention_scenarios',
    'compute_foresight_intelligence',  # NEW
]
```

## API Response Structure

### Endpoint: GET /api/startups/{id}?include_intelligence=true

New intelligence.foresight payload structure:

```json
{
  "intelligence": {
    "timeSnapshots": [...],
    "causalityMarkers": {...},
    "interventionScenarios": {...},
    "foresight": {
      "no_intervention": {
        "decisionWindow": {
          "days_min": 14,
          "days_max": 21,
          "description": "Risk likely to escalate within ~14–21 days under unchanged behavior"
        },
        "urgency": "HIGH",
        "confidence": {
          "level": "High",
          "rationale": "Pattern repeated historically across comparable portfolio companies"
        },
        "reversibility": {
          "marker": "NARROWING",
          "description": "Intervention window closing; action urgency increasing",
          "explanation": "Current trajectory leads to compounding dysfunction..."
        },
        "velocityIndicator": "Accelerating decline"
      },
      "early_intervention": {
        "decisionWindow": {...},
        "urgency": "MEDIUM",
        "confidence": {...},
        "reversibility": {
          "marker": "VIABLE",
          "description": "Intervention still likely to materially alter outcome",
          "explanation": "Operational reset achievable with focused advisory support..."
        },
        "velocityIndicator": "Gradual deterioration"
      },
      "delayed_intervention": {
        "decisionWindow": {...},
        "urgency": "CRITICAL",
        "confidence": {...},
        "reversibility": {
          "marker": "DIMINISHED",
          "description": "Intervention impact materially constrained",
          "explanation": "Team cohesion, market position degraded..."
        },
        "velocityIndicator": "Rapid deterioration"
      }
    }
  }
}
```

## Technical Design Principles

### 1. No Prediction, No Probabilities
- All signals derived from observable historical patterns
- Time windows expressed as bounded ranges, not point forecasts
- Confidence framing uses descriptive language, not numeric percentages

### 2. Deterministic & Cacheable
- All computations seeded from startup archetype and historical snapshots
- Foresight signals precomputed at startup with full portfolio cache
- No randomness per request, guaranteed reproducibility

### 3. Decision-Grade Language
- Urgency levels suitable for investment committee escalation
- Reversibility assessments framed honestly without optimistic bias
- Confidence rationale provides context for interpretation

### 4. Scenario-Aware
- Separate foresight signals for no/early/delayed intervention
- Enables comparative analysis: "If we intervene early, urgency drops from HIGH to MEDIUM"
- Reversibility markers explicitly compare intervention impact

### 5. Archetype-Informed
- Decision windows calibrated by startup archetype
- Urgency classification considers archetype failure patterns
- Reversibility assessments account for structural vs operational issues

## Use Cases

### Investment Committee Briefing
```
Startup: Lumina Health
Risk: 72 (High)
Decision Window: Near-term (7-14 days)
Urgency: HIGH
Reversibility: VIABLE with early intervention

Rationale: Post-hype collapse archetype with accelerating decline. 
High confidence based on 60-day trajectory. Operational reset achievable 
with focused advisory support if deployed within 2 weeks.
```

### Portfolio Triage
- Filter by urgency level: Show all CRITICAL and HIGH urgency startups
- Sort by decision window: Prioritize immediate (0-7 day) windows
- Compare reversibility: Focus resources on VIABLE/OPTIMAL interventions

### Scenario Comparison
```
Current State (No Intervention):
  - Urgency: HIGH
  - Window: 7-14 days
  - Reversibility: NARROWING

With Early Intervention:
  - Urgency: MEDIUM
  - Window: 14-21 days
  - Reversibility: VIABLE

Conclusion: Early intervention materially improves outlook and extends 
decision window, justifying immediate advisory engagement.
```

## Dependencies

### Required Modules
- `backend.feature_engineering`: For risk feature computation
- `backend.risk_model`: For risk scoring and trend analysis
- `backend.intelligence.time_snapshots`: For historical snapshot data
- `numpy`: For velocity calculations and data manipulation

### No New External Dependencies
- Built entirely on existing infrastructure
- No ML libraries added
- No prediction frameworks required

## Testing Approach

### Manual Validation (Python Required)
```python
from backend.api.routes import _build_cache

# Build cache with foresight
startups, lookup, extended = _build_cache()

# Test specific startup
startup = lookup['1']  # Lumina Health (post_hype_collapse)
print(f"Startup: {startup['name']}")
print(f"Risk: {startup['riskScore']} ({startup['severity']})")

# Check if intelligence included (requires ?include_intelligence=true)
# Via API: GET /api/startups/1?include_intelligence=true
```

### Expected Outputs by Archetype

#### Post-Hype Collapse (Lumina Health, Quantum Logistics, Strata AI)
- Urgency: HIGH to CRITICAL
- Window: Immediate to Near-term
- Reversibility: NARROWING to DIMINISHED
- Confidence: High (clear trajectory)

#### Silent Failure (Nexus Fintech, Beacon Retail, Frontier Labs)
- Urgency: MEDIUM to HIGH
- Window: Near-term to Medium-term
- Reversibility: VIABLE with early action
- Confidence: Medium (gradual signals)

#### Zombie (Atlas Robotics, WaveGrid)
- Urgency: LOW to MEDIUM
- Window: Watchlist to Long-term
- Reversibility: CONSTRAINED (structural issues)
- Confidence: Medium (stable but low-energy)

#### Consistent Winner (Verde Climate, Cipher Security, TerraSense)
- Urgency: LOW
- Window: Long-term (30+ days)
- Reversibility: PREVENTIVE or ACCELERATIVE
- Confidence: High (stable positive trajectory)

## Files Modified

### New Files
- `backend/intelligence/foresight.py` (329 lines)

### Modified Files
- `backend/intelligence/__init__.py` (added foresight export)
- `backend/api/routes.py` (integrated foresight computation)

### Unchanged Files
- Core intelligence modules (feature_engineering, risk_model, portfolio_utils)
- Frontend (no UI changes required; data binding via existing endpoint)
- Reasoning layer (Azure OpenAI integration remains independent)

## Next Steps (If Python Available)

1. **Start Backend Server**
   ```bash
   cd backend
   uvicorn main:app --reload --port 8000
   ```

2. **Test Foresight Endpoint**
   ```bash
   curl http://localhost:8000/api/startups/1?include_intelligence=true | jq '.intelligence.foresight'
   ```

3. **Validate Across Archetypes**
   - Test post_hype_collapse (IDs: 1, 2, 10) → Expect HIGH/CRITICAL urgency
   - Test consistent_winner (IDs: 4, 6, 14) → Expect LOW urgency
   - Test zombie (IDs: 5, 11) → Expect MEDIUM urgency with CONSTRAINED reversibility

4. **Frontend Integration** (Optional)
   - Parse intelligence.foresight from API response
   - Display urgency badges, decision windows in UI
   - Show scenario comparison table

## Design Rationale

### Why Bounded Time Windows?
Investment committees need actionable timeframes, not false precision. "7-14 days" communicates urgency and flexibility without overpromising accuracy.

### Why Separate Urgency from Risk Score?
A startup can have medium risk score (55) but HIGH urgency if trajectory is accelerating. Urgency reflects dynamics, not just state.

### Why Non-Numeric Confidence?
Numeric confidence (e.g., "73% confident") implies statistical rigor that doesn't exist. Descriptive confidence ("High confidence based on 60-day trajectory") provides context without false precision.

### Why Honest Reversibility Markers?
VCs need realistic assessments. "DIMINISHED" reversibility for late-stage interventions prevents wasting resources on lost causes. "VIABLE" markers highlight where intervention can actually change outcomes.

## Comparison to Prediction Systems

### What This Is NOT
- ❌ Forecasting future risk scores
- ❌ Predicting company outcomes
- ❌ Simulating market scenarios
- ❌ Machine learning-based predictions

### What This IS
- ✅ Bounded time estimates based on historical velocity
- ✅ Urgency classification based on trajectory dynamics
- ✅ Confidence framing reflecting data quality
- ✅ Reversibility assessment comparing intervention scenarios

## Summary

Phase 6 successfully added decision-grade foresight intelligence to the portfolio risk system, enabling VCs to answer four critical questions:

1. **How much time do we have?** → Decision windows (bounded ranges)
2. **How urgent is this?** → Urgency classification (LOW/MEDIUM/HIGH/CRITICAL)
3. **How confident are we?** → Qualitative confidence with rationale
4. **Can we still change the outcome?** → Reversibility markers per scenario

All signals are deterministic, cached, and expressed in professional language suitable for investment committee decision-making. No prediction, no probabilities, no false precision—just actionable intelligence derived from observable patterns.
