"""FastAPI routes exposing risk intelligence data.

Deterministic, demo-safe endpoints that wrap the existing risk intelligence
pipeline. Data is precomputed at startup from sample CSVs to avoid per-request
variance and to keep responses fast and reproducible.
"""

from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
from fastapi import APIRouter, HTTPException

from backend.feature_engineering import engineer_features
from backend.risk_model import compute_risk_score, get_risk_trend, get_risk_components
from backend.portfolio_utils import (
    label_risk_severity,
    extract_top_signals,
)
from backend.reasoning import get_investor_reasoning

router = APIRouter()


# ---------------------------------------------------------------------------
# Data Preparation (deterministic, computed once at startup)
# ---------------------------------------------------------------------------

def _load_dataset(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Sample data not found at {path}")
    return pd.read_csv(path)


def _compute_startup_payload(startup_id: str, name: str, sector: str, df: pd.DataFrame) -> Dict:
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

    return {
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


def _build_cache() -> Tuple[List[Dict], Dict[str, Dict]]:
    base_path = Path(__file__).resolve().parent.parent
    data_path = base_path / 'sample_data.csv'
    df_full = _load_dataset(data_path)

    # Variant dataset (earlier window) to produce a second deterministic profile
    df_mid = df_full.head(max(20, len(df_full) // 2))

    startups = [
        _compute_startup_payload('1', 'Lumina Health', 'Healthcare', df_full),
        _compute_startup_payload('2', 'Quantum Logistics', 'Supply Chain', df_mid),
    ]

    # Quick lookup map
    lookup = {s['id']: s for s in startups}
    return startups, lookup


STARTUPS_CACHE, STARTUP_LOOKUP = _build_cache()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get('/api/startups')
def list_startups() -> List[Dict]:
    """Return summary portfolio view for all startups."""
    return STARTUPS_CACHE


@router.get('/api/startups/{startup_id}')
def get_startup(startup_id: str) -> Dict:
    """Return full risk intelligence object for a single startup."""
    startup = STARTUP_LOOKUP.get(startup_id)
    if not startup:
        raise HTTPException(status_code=404, detail='Startup not found')
    return startup
