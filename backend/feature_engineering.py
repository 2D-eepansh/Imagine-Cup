"""
Feature Engineering for Portfolio Risk Intelligence

This module transforms raw startup operational data into time-series signals 
that indicate execution velocity, team health, and operational sustainability.

Core philosophy: Early warning signals precede catastrophic failure.
VCs need leading indicators, not lagging metrics.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform raw startup operational data into investor-grade risk signals.
    
    This function creates time-based features that capture:
    - Execution momentum (commit velocity, task completion)
    - Team health (morale trends, responsiveness)
    - Operational efficiency (spend dynamics)
    
    Args:
        df: DataFrame with columns:
            - date (datetime or convertible)
            - commit_count (int)
            - tasks_completed (int)
            - tasks_missed (int)
            - avg_response_time_hours (float)
            - founder_morale_score (float, 0-10 scale)
            - compute_spend_usd (float)
    
    Returns:
        DataFrame with original columns plus engineered features:
            - commit_rolling_7d: 7-day average commit velocity
            - task_miss_rate: Proportion of tasks missed (0-1)
            - morale_change: Day-over-day morale delta
            - morale_trend_7d: 7-day morale trend (positive/negative)
            - response_delay_normalized: Z-scored response time
            - spend_change_pct: Percentage change in compute spend
            - spend_acceleration: Second derivative of spend (spending velocity)
            - execution_health: Composite metric (0-1, higher is better)
    
    Design rationale:
        - Rolling windows smooth noise while preserving trend
        - Miss rate is a direct execution quality signal
        - Morale tracking detects team cohesion breakdown
        - Spend patterns reveal burn rate instability
    """
    
    # Create a working copy to avoid mutation
    df = df.copy()
    
    # Ensure date column is datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Sort by date to ensure temporal coherence
    df = df.sort_values('date').reset_index(drop=True)
    
    # ============================================================
    # EXECUTION VELOCITY SIGNALS
    # ============================================================
    
    # Rolling 7-day commit average - detects slowdown in development
    # Sudden drops indicate team capacity issues or blocked progress
    df['commit_rolling_7d'] = df['commit_count'].rolling(
        window=7, 
        min_periods=1
    ).mean()
    
    # Commit acceleration - is velocity increasing or decreasing?
    df['commit_velocity_change'] = df['commit_rolling_7d'].diff()
    
    # ============================================================
    # TASK EXECUTION QUALITY
    # ============================================================
    
    # Task miss rate - core execution discipline metric
    # High miss rate = poor planning or overcapacity
    df['total_tasks'] = df['tasks_completed'] + df['tasks_missed']
    df['task_miss_rate'] = np.where(
        df['total_tasks'] > 0,
        df['tasks_missed'] / df['total_tasks'],
        0.0
    )
    
    # Rolling 7-day miss rate - persistent vs. temporary issues
    df['task_miss_rate_7d'] = df['task_miss_rate'].rolling(
        window=7,
        min_periods=1
    ).mean()
    
    # ============================================================
    # TEAM HEALTH SIGNALS (MORALE)
    # ============================================================
    
    # Day-over-day morale change - early warning for team issues
    # Persistent decline is a red flag for founder conflict or burnout
    df['morale_change'] = df['founder_morale_score'].diff()
    
    # 7-day morale trend using linear regression slope
    # Captures sustained decline vs. daily noise
    df['morale_trend_7d'] = df['founder_morale_score'].rolling(
        window=7,
        min_periods=3
    ).apply(_calculate_trend_slope, raw=False)
    
    # Morale volatility - excessive swings indicate instability
    df['morale_volatility_7d'] = df['founder_morale_score'].rolling(
        window=7,
        min_periods=3
    ).std()
    
    # ============================================================
    # RESPONSIVENESS SIGNALS
    # ============================================================
    
    # Normalize response time using z-score
    # Detects when team is becoming unresponsive relative to baseline
    mean_response = df['avg_response_time_hours'].mean()
    std_response = df['avg_response_time_hours'].std()
    
    if std_response > 0:
        df['response_delay_normalized'] = (
            df['avg_response_time_hours'] - mean_response
        ) / std_response
    else:
        df['response_delay_normalized'] = 0.0
    
    # ============================================================
    # SPEND DYNAMICS (BURN RATE SIGNALS)
    # ============================================================
    
    # Percentage change in daily compute spend
    # Sudden spikes may indicate inefficiency or loss of cost control
    df['spend_change_pct'] = df['compute_spend_usd'].pct_change() * 100
    
    # Replace infinities with 0 (occurs when previous spend is 0)
    df['spend_change_pct'] = df['spend_change_pct'].replace([np.inf, -np.inf], 0)
    
    # Spend acceleration - second derivative
    # Detects if burn rate is accelerating (red flag)
    df['spend_acceleration'] = df['spend_change_pct'].diff()
    
    # Rolling 7-day average spend - baseline burn rate
    df['spend_rolling_7d'] = df['compute_spend_usd'].rolling(
        window=7,
        min_periods=1
    ).mean()
    
    # ============================================================
    # COMPOSITE EXECUTION HEALTH METRIC
    # ============================================================
    
    # Combines multiple signals into single execution health score (0-1)
    # Higher = healthier execution
    
    # Normalize commit velocity (0-1 scale relative to max)
    max_commits = df['commit_rolling_7d'].max()
    commit_score = df['commit_rolling_7d'] / max_commits if max_commits > 0 else 0
    
    # Invert miss rate (1 = no misses, 0 = all missed)
    task_score = 1 - df['task_miss_rate_7d']
    
    # Normalize morale (assuming 0-10 scale)
    morale_score = df['founder_morale_score'] / 10.0
    
    # Weighted composite (execution > morale > tasks)
    df['execution_health'] = (
        0.40 * commit_score +
        0.35 * task_score +
        0.25 * morale_score
    )
    
    # ============================================================
    # CLEAN UP AND FINALIZE
    # ============================================================
    
    # Fill NaN values that result from rolling windows and diff operations
    # Use forward fill for early window periods
    df = df.fillna(method='bfill').fillna(0)
    
    # Drop intermediate calculation columns
    df = df.drop(columns=['total_tasks'], errors='ignore')
    
    return df


def _calculate_trend_slope(series: pd.Series) -> float:
    """
    Calculate linear trend slope for a time series window.
    
    Used to detect sustained morale trends (up/down) over rolling windows.
    Positive slope = improving, negative = declining.
    
    Args:
        series: Time series window (pandas Series)
    
    Returns:
        Slope of linear fit (float)
    """
    if len(series) < 2:
        return 0.0
    
    # Create x values (0, 1, 2, ... n-1)
    x = np.arange(len(series))
    y = series.values
    
    # Handle NaN values
    mask = ~np.isnan(y)
    if mask.sum() < 2:
        return 0.0
    
    # Simple linear regression: slope = covariance(x,y) / variance(x)
    try:
        slope = np.polyfit(x[mask], y[mask], 1)[0]
        return slope
    except:
        return 0.0


def get_feature_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Extract summary statistics from engineered features.
    
    Useful for quick health checks and debugging feature distributions.
    
    Args:
        df: DataFrame with engineered features
    
    Returns:
        Dictionary containing summary metrics
    """
    if df.empty:
        return {}
    
    # Get most recent values (investor cares about current state)
    latest = df.iloc[-1]
    
    summary = {
        'latest_date': latest['date'],
        'commit_velocity_7d': round(latest['commit_rolling_7d'], 2),
        'task_miss_rate': round(latest['task_miss_rate'], 3),
        'morale_score': round(latest['founder_morale_score'], 1),
        'morale_trend': round(latest['morale_trend_7d'], 3),
        'execution_health': round(latest['execution_health'], 3),
        'response_time_hours': round(latest['avg_response_time_hours'], 1),
        'daily_spend_usd': round(latest['compute_spend_usd'], 2),
        'spend_change_pct': round(latest['spend_change_pct'], 1)
    }
    
    return summary
