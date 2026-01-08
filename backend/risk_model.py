"""
Risk Scoring Model for Portfolio Intelligence

This module implements anomaly detection and risk quantification for startup portfolios.
It uses Isolation Forest to detect abnormal operational patterns and combines signals
into a unified risk score (0-100 scale).

Core insight: Startups fail gradually, then suddenly.
This model detects the "gradually" phase before capital is lost.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from typing import Tuple, Dict, Any, List


def compute_risk_score(df: pd.DataFrame) -> Tuple[float, pd.DataFrame]:
    """
    Compute portfolio risk score for a startup using anomaly detection and signal weighting.
    
    This is the core intelligence function. It:
    1. Detects operational anomalies using Isolation Forest
    2. Weights signals by investor importance (execution > morale > spend)
    3. Produces a single risk score (0-100) for the most recent day
    
    Risk score interpretation:
        0-30:  Low risk - healthy execution, normal operations
        31-60: Medium risk - warning signals present, monitor closely
        61-100: High risk - intervention required, capital at risk
    
    Args:
        df: DataFrame with engineered features from feature_engineering.py
            Must include:
                - commit_rolling_7d
                - task_miss_rate_7d
                - morale_trend_7d
                - response_delay_normalized
                - spend_change_pct
                - execution_health
    
    Returns:
        Tuple of (risk_score, df_with_anomalies):
            - risk_score: Float between 0-100 (higher = more risk)
            - df_with_anomalies: Original DataFrame with added columns:
                - anomaly_score: Isolation Forest anomaly score (-1 to 1)
                - is_anomaly: Boolean flag for anomaly detection
                - daily_risk: Risk score for each day
    
    Design rationale:
        - Isolation Forest detects multivariate operational abnormalities
        - Weighted combination reflects VC priorities (execution matters most)
        - Recent bias: latest data weighted more heavily
        - Explainable: each component can be traced back to source data
    """
    
    # Validate input
    if df.empty:
        raise ValueError("Input DataFrame is empty")
    
    # Create working copy
    df = df.copy()
    
    # ============================================================
    # STEP 1: ANOMALY DETECTION
    # ============================================================
    
    # Select features for anomaly detection
    # These represent core operational health dimensions
    anomaly_features = [
        'commit_rolling_7d',      # Development velocity
        'task_miss_rate_7d',      # Execution discipline
        'morale_trend_7d',        # Team health trajectory
        'response_delay_normalized',  # Responsiveness
        'spend_change_pct',       # Burn rate stability
    ]
    
    # Ensure all required features exist
    missing_features = [f for f in anomaly_features if f not in df.columns]
    if missing_features:
        raise ValueError(f"Missing required features: {missing_features}")
    
    # Extract feature matrix for anomaly detection
    X = df[anomaly_features].copy()
    
    # Handle any remaining NaN/inf values
    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.fillna(X.mean())
    
    # Initialize Isolation Forest
    # contamination=0.1: assume ~10% of days might be anomalous
    # This is calibrated for early-stage startup volatility
    iso_forest = IsolationForest(
        contamination=0.1,
        random_state=42,
        n_estimators=100,
        max_samples='auto',
        bootstrap=False
    )
    
    # Fit and predict anomalies
    # Returns: 1 for normal, -1 for anomaly
    anomaly_labels = iso_forest.fit_predict(X)
    
    # Get anomaly scores (lower = more anomalous)
    # decision_function returns negative scores for anomalies
    anomaly_scores = iso_forest.decision_function(X)
    
    # Normalize anomaly scores to 0-1 scale (1 = highly anomalous)
    # This makes them interpretable and comparable
    df['anomaly_score'] = _normalize_to_risk(anomaly_scores, invert=True)
    df['is_anomaly'] = anomaly_labels == -1
    
    # ============================================================
    # STEP 2: WEIGHTED SIGNAL COMBINATION
    # ============================================================
    
    # Define risk signal weights (must sum to 1.0)
    # Execution and team health matter more than spend volatility
    weights = {
        'execution': 0.35,      # Commit velocity + task completion
        'team_health': 0.25,    # Morale and responsiveness
        'anomaly': 0.25,        # Statistical abnormality
        'spend': 0.15           # Burn rate dynamics
    }
    
    # EXECUTION RISK COMPONENT
    # Lower execution_health = higher risk
    df['risk_execution'] = 1 - df['execution_health']
    
    # Task miss rate is a direct risk signal
    df['risk_task_quality'] = df['task_miss_rate_7d']
    
    # Combined execution risk (weighted average)
    df['execution_risk_signal'] = (
        0.6 * df['risk_execution'] +
        0.4 * df['risk_task_quality']
    )
    
    # TEAM HEALTH RISK COMPONENT
    # Negative morale trend = increasing risk
    # Normalize morale trend to risk scale (0-1)
    morale_risk = df['morale_trend_7d'].apply(
        lambda x: max(0, -x * 0.5)  # Negative trends become positive risk
    )
    df['team_health_risk_signal'] = np.clip(morale_risk, 0, 1)
    
    # Add responsiveness component (high response time = risk)
    response_risk = df['response_delay_normalized'].apply(
        lambda x: max(0, x) / 3  # Normalize to 0-1 range
    )
    df['team_health_risk_signal'] = (
        0.7 * df['team_health_risk_signal'] +
        0.3 * np.clip(response_risk, 0, 1)
    )
    
    # SPEND RISK COMPONENT
    # High spend volatility or acceleration = risk
    spend_vol = np.abs(df['spend_change_pct']) / 100  # Normalize
    df['spend_risk_signal'] = np.clip(spend_vol, 0, 1)
    
    # ANOMALY RISK COMPONENT
    # Already normalized 0-1 from Isolation Forest
    df['anomaly_risk_signal'] = df['anomaly_score']
    
    # ============================================================
    # STEP 3: COMPOSITE DAILY RISK SCORE
    # ============================================================
    
    # Weighted combination of all risk signals
    df['daily_risk'] = (
        weights['execution'] * df['execution_risk_signal'] +
        weights['team_health'] * df['team_health_risk_signal'] +
        weights['anomaly'] * df['anomaly_risk_signal'] +
        weights['spend'] * df['spend_risk_signal']
    )
    
    # Scale to 0-100 for investor-grade presentation
    df['daily_risk_score'] = df['daily_risk'] * 100
    
    # ============================================================
    # STEP 4: COMPUTE FINAL RISK SCORE (LATEST DAY)
    # ============================================================
    
    # Use exponential weighting to emphasize recent days
    # Recent data is more predictive than old data
    window_size = min(7, len(df))  # Use up to 7 days
    recent_scores = df['daily_risk_score'].tail(window_size).values
    
    # Exponential weights: most recent day gets highest weight
    exp_weights = np.exp(np.linspace(0, 1, window_size))
    exp_weights = exp_weights / exp_weights.sum()
    
    # Weighted average of recent risk scores
    risk_score = np.average(recent_scores, weights=exp_weights)
    
    # Apply trend adjustment: if risk is increasing, add penalty
    if len(recent_scores) >= 3:
        risk_trend = np.polyfit(range(len(recent_scores)), recent_scores, 1)[0]
        if risk_trend > 0:  # Risk is increasing
            risk_score += min(risk_trend * 2, 10)  # Add up to 10 points
    
    # Ensure final score is within bounds
    risk_score = np.clip(risk_score, 0, 100)
    
    return risk_score, df


def _normalize_to_risk(scores: np.ndarray, invert: bool = False) -> np.ndarray:
    """
    Normalize anomaly scores to 0-1 risk scale.
    
    Args:
        scores: Array of anomaly scores from Isolation Forest
        invert: If True, invert so that lower scores become higher risk
    
    Returns:
        Normalized risk scores (0-1 scale)
    """
    if len(scores) == 0:
        return np.array([])
    
    # Min-max normalization
    min_score = scores.min()
    max_score = scores.max()
    
    if max_score - min_score == 0:
        return np.zeros_like(scores)
    
    normalized = (scores - min_score) / (max_score - min_score)
    
    if invert:
        normalized = 1 - normalized
    
    return normalized


def get_risk_components(df: pd.DataFrame) -> Dict[str, float]:
    """
    Extract individual risk component contributions for the most recent day.
    
    This provides explainability: investors can see which signals drove the risk score.
    
    Args:
        df: DataFrame with computed risk signals (output from compute_risk_score)
    
    Returns:
        Dictionary with breakdown of risk components (0-100 scale)
    """
    if df.empty or 'daily_risk_score' not in df.columns:
        return {}
    
    latest = df.iloc[-1]
    
    components = {
        'execution_risk': round(latest.get('execution_risk_signal', 0) * 100, 1),
        'team_health_risk': round(latest.get('team_health_risk_signal', 0) * 100, 1),
        'anomaly_risk': round(latest.get('anomaly_risk_signal', 0) * 100, 1),
        'spend_risk': round(latest.get('spend_risk_signal', 0) * 100, 1),
        'is_anomaly_detected': bool(latest.get('is_anomaly', False))
    }
    
    return components


def get_risk_trend(df: pd.DataFrame, window: int = 7) -> Dict[str, Any]:
    """
    Analyze risk score trajectory over recent window.
    
    Helps investors understand if risk is stable, increasing, or decreasing.
    
    Args:
        df: DataFrame with daily_risk_score column
        window: Number of days to analyze (default: 7)
    
    Returns:
        Dictionary with trend analysis metrics
    """
    if df.empty or 'daily_risk_score' not in df.columns:
        return {}
    
    recent = df['daily_risk_score'].tail(window)
    
    if len(recent) < 2:
        return {'trend': 'insufficient_data'}
    
    # Calculate trend slope
    x = np.arange(len(recent))
    slope = np.polyfit(x, recent.values, 1)[0]
    
    # Classify trend
    if abs(slope) < 1:
        trend_direction = 'stable'
    elif slope > 0:
        trend_direction = 'increasing'
    else:
        trend_direction = 'decreasing'
    
    # Calculate volatility
    volatility = recent.std()
    
    return {
        'trend_direction': trend_direction,
        'trend_slope': round(slope, 2),
        'volatility': round(volatility, 2),
        'risk_range': {
            'min': round(recent.min(), 1),
            'max': round(recent.max(), 1),
            'current': round(recent.iloc[-1], 1)
        }
    }


def identify_critical_signals(df: pd.DataFrame, threshold: float = 0.6) -> List[str]:
    """
    Identify which specific signals are in critical state (high risk).
    
    This enables targeted intervention recommendations.
    
    Args:
        df: DataFrame with risk signals
        threshold: Risk level above which signal is considered critical (0-1 scale)
    
    Returns:
        List of critical signal names
    """
    if df.empty:
        return []
    
    latest = df.iloc[-1]
    critical_signals = []
    
    # Check each risk component
    signal_checks = {
        'execution_velocity': latest.get('risk_execution', 0),
        'task_completion': latest.get('risk_task_quality', 0),
        'team_morale': latest.get('team_health_risk_signal', 0),
        'spend_volatility': latest.get('spend_risk_signal', 0),
        'operational_anomaly': latest.get('anomaly_risk_signal', 0)
    }
    
    for signal_name, risk_level in signal_checks.items():
        if risk_level > threshold:
            critical_signals.append(signal_name)
    
    return critical_signals
