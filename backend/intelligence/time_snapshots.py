"""Time-aware intelligence: precomputed historical snapshots.

Enables viewing how risk evolved over time without live recomputation.
All snapshots are deterministic and cached at startup.
"""

from typing import Dict, List, Any
import pandas as pd

from feature_engineering import engineer_features
from risk_model import compute_risk_score
from portfolio_utils import label_risk_severity, extract_top_signals


def compute_historical_snapshots(df: pd.DataFrame, startup_id: str, name: str) -> List[Dict[str, Any]]:
    """Precompute risk snapshots at key historical windows.
    
    Returns list of snapshots from oldest to newest, each containing:
    - days_ago: how many days back from present
    - risk_score: score at that point
    - severity: LOW/MEDIUM/HIGH
    - top_driver: dominant signal
    - date: timestamp of snapshot
    """
    if len(df) < 7:
        # Insufficient data for meaningful snapshots
        return []
    
    snapshots = []
    windows = []
    
    # Define snapshot windows (days back from end)
    total_days = len(df)
    if total_days >= 60:
        windows = [60, 45, 30, 14, 7, 0]  # 6 snapshots
    elif total_days >= 45:
        windows = [45, 30, 14, 7, 0]  # 5 snapshots
    elif total_days >= 30:
        windows = [30, 14, 7, 0]  # 4 snapshots
    else:
        windows = [14, 7, 0]  # 3 snapshots minimum
    
    # Filter to valid windows
    windows = [w for w in windows if w < total_days]
    if 0 not in windows:
        windows.append(0)
    
    for days_ago in sorted(windows, reverse=True):
        # Slice data up to that point
        end_idx = len(df) - days_ago
        df_slice = df.iloc[:end_idx].copy()
        
        if len(df_slice) < 7:
            continue
        
        # Compute risk at that point in time
        df_features = engineer_features(df_slice)
        risk_score, df_with_risk = compute_risk_score(df_features)
        severity = label_risk_severity(risk_score).lower()
        
        # Extract top driver
        top_signals = extract_top_signals(df_with_risk, top_n=1)
        top_driver = top_signals[0]['signal_name'] if top_signals else 'Unknown'
        
        # Get the date of this snapshot
        snapshot_date = df_slice.iloc[-1]['date']
        
        snapshots.append({
            'days_ago': days_ago,
            'date': str(snapshot_date),
            'risk_score': round(float(risk_score), 1),
            'severity': severity,
            'top_driver': top_driver,
        })
    
    return snapshots


def compute_causality_markers(snapshots: List[Dict[str, Any]], current_severity: str) -> Dict[str, Any]:
    """Extract causality metadata from snapshot history.
    
    Returns markers like:
    - first_risk_detected_days_ago: when risk exceeded 40
    - days_before_high_risk: lead time to severe state
    - trajectory: improving/stable/deteriorating
    """
    if not snapshots:
        return {}
    
    # Find first elevated risk (>40)
    first_risk_day = None
    for snap in snapshots:
        if snap['risk_score'] > 40:
            first_risk_day = snap['days_ago']
    
    # Find when risk became high (>60)
    high_risk_day = None
    for snap in snapshots:
        if snap['risk_score'] > 60:
            high_risk_day = snap['days_ago']
    
    # Calculate lead time
    lead_time = None
    if current_severity == 'high' and first_risk_day is not None:
        lead_time = first_risk_day  # Days of warning before current high state
    
    # Determine trajectory
    if len(snapshots) >= 3:
        early_risk = snapshots[0]['risk_score']
        mid_risk = snapshots[len(snapshots) // 2]['risk_score']
        late_risk = snapshots[-1]['risk_score']
        
        if late_risk < early_risk - 10:
            trajectory = 'improving'
        elif late_risk > early_risk + 10:
            trajectory = 'deteriorating'
        else:
            trajectory = 'stable'
    else:
        trajectory = 'insufficient_history'
    
    return {
        'first_risk_detected_days_ago': first_risk_day,
        'high_risk_reached_days_ago': high_risk_day,
        'lead_time_days': lead_time,
        'trajectory': trajectory,
        'snapshot_count': len(snapshots),
    }
