"""FastAPI routes exposing risk intelligence data.

Deterministic, demo-safe endpoints that wrap the existing risk intelligence
pipeline. Data is precomputed at startup from sample CSVs to avoid per-request
variance and to keep responses fast and reproducible.
"""

from typing import Dict, List, Tuple, Optional

import pandas as pd
from fastapi import APIRouter, HTTPException, Query
import numpy as np

from hardening import (
    RequestValidator,
    AuditMetadata,
    FailureMode,
    run_hardening_checks,
    run_system_readiness,
    READINESS_STATUS,
    READINESS_DETAILS,
)

from feature_engineering import engineer_features
from risk_model import compute_risk_score, get_risk_trend, get_risk_components
from portfolio_utils import (
    label_risk_severity,
    extract_top_signals,
)
from reasoning import get_investor_reasoning
from intelligence import (
    compute_historical_snapshots,
    compute_causality_markers,
    compute_intervention_scenarios,
    compute_foresight_intelligence,
    compute_portfolio_intelligence,
    enrich_startup_with_memory,
    generate_portfolio_memory_summary,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# Data Preparation (deterministic, computed once at startup)
# ---------------------------------------------------------------------------

def _compute_startup_payload(
    startup_id: str,
    name: str,
    sector: str,
    df: pd.DataFrame,
    archetype: str = 'unknown',
    include_intelligence: bool = False,
) -> Dict:
    df_features = engineer_features(df)
    risk_score, df_with_risk = compute_risk_score(df_features)

    components_raw = get_risk_components(df_with_risk)
    components = {
        'execution': components_raw.get('execution_risk', 0),
        'team_health': components_raw.get('team_health_risk', 0),
        'anomaly': components_raw.get('anomaly_risk', 0),
        'spend': components_raw.get('spend_risk', 0),
    }

    # Last 7 days of risk scores for sparkline and trend
    risk_history = df_with_risk['daily_risk_score'].tail(7).round(1).tolist()
    if not risk_history:
        risk_history = [float(risk_score)]

    # Trend direction derived from slope
    trend_info = get_risk_trend(df_with_risk, window=min(7, len(df_with_risk)))
    slope = trend_info.get('trend_slope', 0)
    if slope > 1:
        trend = 'up'
    elif slope < -1:
        trend = 'down'
    else:
        trend = 'stable'

    trend_delta = round(risk_history[-1] - risk_history[0], 1) if len(risk_history) > 1 else 0.0

    # Severity and drivers
    severity = label_risk_severity(risk_score).lower()
    top_signals = extract_top_signals(df_with_risk, top_n=3)
    risk_drivers = [
        {
            'label': signal['signal_name'],
            'detail': signal['description'],
        }
        for signal in top_signals
    ]

    # Reasoning layer: deterministic, cached
    snapshot = {
        'startup_id': startup_id,
        'name': name,
        'sector': sector,
        'risk_score': risk_score,
        'severity': severity,
        'trend': trend,
        'trend_delta': trend_delta,
        'risk_drivers': risk_drivers,
        'components': components,
    }
    reasoning = get_investor_reasoning(snapshot)
    ai_insight = {
        'whyItMatters': reasoning.get('why_this_matters', ''),
        'whatHappensNext': reasoning.get('what_typically_happens_next', ''),
        'recommendedAction': reasoning.get('recommended_investor_action', ''),
    }

    requires_partner_attention = severity == 'high'

    payload = {
        'id': startup_id,
        'name': name,
        'sector': sector,
        'riskScore': round(float(risk_score), 1),
        'severity': severity,
        'trend': trend,
        'trendDelta': trend_delta,
        'riskHistory': risk_history,
        'riskDrivers': risk_drivers,
        'aiInsight': ai_insight,
        'requiresPartnerAttention': requires_partner_attention,
    }

    # Optionally include intelligence layer (time snapshots, scenarios, causality)
    if include_intelligence:
        snapshots = compute_historical_snapshots(df, startup_id, name)
        causality = compute_causality_markers(snapshots, severity)
        scenarios = compute_intervention_scenarios(df, risk_score, severity, archetype)

        # Compute decision foresight for each intervention scenario
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
                    'foresight': foresight_signals,
        }
        
        # Enrich with investor memory layer for no_intervention scenario
        # (Memory enrichment applies to default scenario; all scenarios share same pattern memory)
        payload = enrich_startup_with_memory(payload, archetype, scenario='no_intervention')

    return payload


def _build_cache() -> Tuple[List[Dict], Dict[str, Dict], Dict[str, Dict]]:
    # Deterministic synthetic portfolio spanning archetypes
    rng = np.random.default_rng(42)

    archetypes = [
        ('1', 'Lumina Health', 'Healthcare', 'post_hype_collapse'),
        ('2', 'Quantum Logistics', 'Supply Chain', 'post_hype_collapse'),
        ('3', 'Nexus Fintech', 'Financial Services', 'silent_failure'),
        ('4', 'Verde Climate', 'CleanTech', 'consistent_winner'),
        ('5', 'Atlas Robotics', 'Industrial', 'zombie'),
        ('6', 'Cipher Security', 'Cybersecurity', 'consistent_winner'),
        ('7', 'Aurora Mobility', 'Transportation', 'false_recovery'),
        ('8', 'Helix Bio', 'Biotech', 'true_turnaround'),
        ('9', 'Beacon Retail', 'E-commerce', 'silent_failure'),
        ('10', 'Strata AI', 'Enterprise SaaS', 'post_hype_collapse'),
        ('11', 'WaveGrid', 'Energy', 'zombie'),
        ('12', 'Nova Payments', 'Fintech', 'false_recovery'),
        ('13', 'Pioneer Ops', 'DevTools', 'true_turnaround'),
        ('14', 'TerraSense', 'AgTech', 'consistent_winner'),
        ('15', 'Frontier Labs', 'Defense Tech', 'silent_failure'),
    ]

    startups: List[Dict] = []
    lookup: Dict[str, Dict] = {}
    extended_cache: Dict[str, Dict] = {}  # Store df + archetype for intelligence queries

    for idx, (sid, name, sector, archetype) in enumerate(archetypes):
        days = int(rng.integers(45, 61))
        df = _generate_archetype_series(archetype, days, seed=1000 + idx)
        payload = _compute_startup_payload(sid, name, sector, df, archetype=archetype)
        startups.append(payload)
        lookup[sid] = payload
        extended_cache[sid] = {'df': df, 'archetype': archetype, 'name': name, 'sector': sector}

    return startups, lookup, extended_cache


# ---------------------------------------------------------------------------
# Synthetic data generator (deterministic, seeded)
# ---------------------------------------------------------------------------

def _generate_archetype_series(archetype: str, days: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range(end=pd.Timestamp.today(), periods=days)

    def clip_pos(arr):
        return np.clip(arr, 0.1, None)

    # Base shapes per archetype
    t = np.linspace(0, 1, days)

    if archetype == 'post_hype_collapse':
        # Fast rise then cliff
        commits = 30 + 10 * (1 - t) + 12 * np.exp(-6 * t)
        commits[t > 0.55] *= 0.35
        miss_rate = 0.05 + 0.4 * (t > 0.55) + 0.15 * t
        morale = 8 - 3 * t - 2 * (t > 0.55)
        response = 2.5 + 4 * t
        spend = 200 + 40 * t
        spend[t > 0.55] *= 0.8  # cost cuts after cliff
        market = 0.8 + 0.2 * np.sin(4 * np.pi * t)
    elif archetype == 'silent_failure':
        # Slow, quiet decay
        commits = 18 - 8 * t
        miss_rate = 0.08 + 0.25 * t
        morale = 7 - 2.5 * t
        response = 3 + 2 * t
        spend = 150 + 10 * t
        market = 0.6 + 0.1 * np.cos(2 * np.pi * t)
    elif archetype == 'zombie':
        # Flat, low energy
        commits = 8 + 2 * np.sin(2 * np.pi * t)
        miss_rate = 0.18 + 0.05 * np.sin(4 * np.pi * t)
        morale = 5 - 0.5 * t
        response = 4.5 + 0.5 * t
        spend = 90 + 5 * np.sin(2 * np.pi * t)
        market = 0.4 + 0.05 * np.sin(6 * np.pi * t)
    elif archetype == 'false_recovery':
        # Brief improvement then regression below baseline
        commits = 14 - 3 * t
        commits[(t > 0.3) & (t < 0.55)] += 6  # short-lived bump
        miss_rate = 0.15 + 0.1 * t
        miss_rate[(t > 0.3) & (t < 0.55)] -= 0.08
        morale = 6 - 1.5 * t
        morale[(t > 0.3) & (t < 0.55)] += 1.0
        response = 3.5 + 1.5 * t
        response[(t > 0.3) & (t < 0.55)] -= 0.8
        spend = 130 + 8 * t
        market = 0.55 + 0.12 * np.sin(3 * np.pi * t)
    elif archetype == 'true_turnaround':
        # Early pain then gradual, believable improvement
        commits = 10 - 4 * (1 - np.exp(-3 * t)) + 8 * t
        miss_rate = 0.22 - 0.12 * t
        morale = 5 + 2 * t
        response = 5 - 1.5 * t
        spend = 120 + 5 * t
        market = 0.5 + 0.1 * t
    elif archetype == 'consistent_winner':
        # Stable, resilient under noise
        commits = 22 + 2 * np.sin(2 * np.pi * t)
        miss_rate = 0.05 + 0.02 * np.sin(4 * np.pi * t)
        morale = 8.2 + 0.3 * np.sin(2 * np.pi * t)
        response = 2.4 + 0.3 * np.sin(3 * np.pi * t)
        spend = 210 + 12 * np.sin(2 * np.pi * t)
        market = 0.7 + 0.1 * np.cos(2 * np.pi * t)
    else:
        # Fallback mild decay
        commits = 15 - 5 * t
        miss_rate = 0.1 + 0.1 * t
        morale = 6 - 1.5 * t
        response = 3 + t
        spend = 120 + 5 * t
        market = 0.5 + 0.05 * np.sin(2 * np.pi * t)

    noise = lambda scale: rng.normal(0, scale, size=days)

    commit_count = clip_pos(commits + noise(1.5)).round().astype(int)
    tasks_completed = clip_pos(commit_count * (0.55 + noise(0.03))).round().astype(int)
    tasks_completed = np.minimum(tasks_completed, commit_count)  # cannot exceed commits proxy
    tasks_missed = clip_pos(commit_count * miss_rate + noise(0.5)).round().astype(int)
    tasks_missed = np.minimum(tasks_missed, commit_count + 3)  # allow some overage but bounded
    avg_response_time_hours = clip_pos(response + noise(0.2)).round(2)
    founder_morale_score = np.clip(morale + noise(0.2), 0, 10).round(2)
    compute_spend_usd = clip_pos(spend + noise(5)).round(2)

    # Modeled market context (not used in scoring, but available)
    market_sentiment_index = (market + noise(0.02)).round(3)
    search_interest_index = (market + 0.1 * np.sin(5 * t) + noise(0.02)).round(3)

    df = pd.DataFrame({
        'date': dates,
        'commit_count': commit_count,
        'tasks_completed': tasks_completed,
        'tasks_missed': tasks_missed,
        'avg_response_time_hours': avg_response_time_hours,
        'founder_morale_score': founder_morale_score,
        'compute_spend_usd': compute_spend_usd,
        'market_sentiment_index': market_sentiment_index,
        'search_interest_index': search_interest_index,
    })

    return df


STARTUPS_CACHE, STARTUP_LOOKUP, EXTENDED_CACHE = _build_cache()

# Precompute full intelligence payloads at startup to avoid per-request computation
FULL_INTELLIGENCE_CACHE: Dict[str, Dict] = {}
for startup_id, ext in EXTENDED_CACHE.items():
    FULL_INTELLIGENCE_CACHE[startup_id] = _compute_startup_payload(
        startup_id,
        ext['name'],
        ext['sector'],
        ext['df'],
        archetype=ext['archetype'],
        include_intelligence=True,
    )

# Run hardening checks after cache is built
run_hardening_checks()

# Compute non-UI system readiness
_READINESS = run_system_readiness(STARTUPS_CACHE, STARTUP_LOOKUP, EXTENDED_CACHE, FULL_INTELLIGENCE_CACHE)


# ---------------------------------------------------------------------------
# Routes (with validation and graceful error handling)
# ---------------------------------------------------------------------------

@router.get('/api/startups')
async def list_startups() -> List[Dict]:
    """Return summary portfolio view for all startups (always succeeds with cached data)."""
    AuditMetadata.log_request("/api/startups")
    return STARTUPS_CACHE


@router.get('/api/startups/{startup_id}')
async def get_startup(
    startup_id: str,
    include_intelligence: Optional[bool] = Query(False, description="Include full intelligence layer")
) -> Dict:
    """Return full risk intelligence object for a single startup (validated and safe).
    
    Query params:
    - include_intelligence: if true, adds timeSnapshots, causalityMarkers, interventionScenarios
    """
    try:
        # Validate inputs
        startup_id = RequestValidator.validate_startup_id(startup_id)
        include_intelligence = RequestValidator.validate_include_intelligence(include_intelligence)
        
        AuditMetadata.log_request("/api/startups/{id}", startup_id=startup_id)
        
        if not include_intelligence:
            startup = STARTUP_LOOKUP.get(startup_id)
            if not startup:
                raise HTTPException(status_code=404, detail='Startup not found')
            return startup

        # Serve precomputed intelligence payload from cache
        full_payload = FULL_INTELLIGENCE_CACHE.get(startup_id)
        if not full_payload:
            raise HTTPException(status_code=404, detail='Startup not found')
        return full_payload
    
    except HTTPException:
        raise  # Re-raise 404s
    except Exception as e:
        # Graceful fallback: return base data + safe intelligence
        AuditMetadata.log_request("/api/startups/{id} [FALLBACK]", startup_id=startup_id)
        
        base_data = STARTUP_LOOKUP.get(startup_id, {
            'id': startup_id,
            'name': 'Unknown',
            'riskScore': 0,
            'severity': 'unknown',
        })
        
        if include_intelligence:
            base_data['intelligence'] = FailureMode.safe_intelligence_fallback(
                startup_id,
                base_data.get('name', 'Unknown')
            )
        
        return base_data


@router.get('/api/portfolio/attention')
async def get_portfolio_attention(
    scenario: Optional[str] = Query('no_intervention', description="Intervention scenario")
) -> Dict:
    """Return portfolio-level attention allocation intelligence (validated and safe).
    
    Provides:
    - Attention priority ranking (not just risk scores)
    - Risk concentration by sector/time
    - Cross-startup pattern detection
    - Actionable attention summary for partner meetings
    
    Query params:
    - scenario: no_intervention | early_intervention | delayed_intervention
    """
    try:
        # Validate scenario with safe default
        scenario = RequestValidator.validate_scenario(scenario)
        
        AuditMetadata.log_request("/api/portfolio/attention", scenario=scenario)
        
        # Use precomputed intelligence payloads from cache
        startups_with_intelligence = list(FULL_INTELLIGENCE_CACHE.values())
        
        # Compute portfolio intelligence
        portfolio_intel = compute_portfolio_intelligence(startups_with_intelligence, scenario)
        
        # Add portfolio memory summary
        pattern_distribution = portfolio_intel['cross_startup_patterns']['archetype_distribution']
        detected_patterns = portfolio_intel['cross_startup_patterns']['detected_patterns']
        portfolio_memory = generate_portfolio_memory_summary(pattern_distribution, detected_patterns)
        portfolio_intel['portfolio_memory'] = portfolio_memory
        
        return portfolio_intel
    
    except Exception as e:
        # Graceful fallback for portfolio view
        AuditMetadata.log_request("/api/portfolio/attention [FALLBACK]", scenario=scenario)
        return FailureMode.safe_portfolio_fallback()


# Internal readiness endpoint (non-UI)
@router.get('/api/internal/readiness')
def internal_readiness() -> Dict:
    return {
        'status': READINESS_STATUS,
        'details': READINESS_DETAILS,
    }
