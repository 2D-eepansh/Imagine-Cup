"""
Portfolio Utilities for VC Risk Intelligence

This module provides helper functions to translate raw risk scores into 
investor-grade insights, labels, and structured outputs for AI reasoning.

Purpose: Bridge technical risk signals with business decision-making.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from datetime import datetime


def label_risk_severity(risk_score: float) -> str:
    """
    Convert numerical risk score to categorical severity label.
    
    These thresholds are calibrated for VC decision-making:
    - Low: Normal operations, passive monitoring
    - Medium: Active monitoring, prepare contingency plans
    - High: Immediate intervention required, capital at risk
    
    Args:
        risk_score: Risk score between 0-100
    
    Returns:
        Severity label: "Low", "Medium", or "High"
    """
    if risk_score < 0 or risk_score > 100:
        raise ValueError(f"Risk score must be 0-100, got {risk_score}")
    
    if risk_score <= 30:
        return "Low"
    elif risk_score <= 60:
        return "Medium"
    else:
        return "High"


def get_severity_color(severity: str) -> str:
    """
    Map severity labels to standard color codes for UI rendering.
    
    Args:
        severity: Risk severity label ("Low", "Medium", "High")
    
    Returns:
        Hex color code
    """
    color_map = {
        "Low": "#10B981",      # Green - healthy
        "Medium": "#F59E0B",   # Amber - caution
        "High": "#EF4444"      # Red - critical
    }
    return color_map.get(severity, "#6B7280")  # Gray fallback


def extract_top_signals(df: pd.DataFrame, top_n: int = 5) -> List[Dict[str, Any]]:
    """
    Identify the top contributing risk signals from the most recent day.
    
    This provides explainability: shows investors which specific metrics
    are driving the overall risk score.
    
    Args:
        df: DataFrame with risk signal columns (from risk_model.py)
        top_n: Number of top signals to return
    
    Returns:
        List of dictionaries, each containing:
            - signal_name: Human-readable signal name
            - risk_level: Numerical risk contribution (0-100)
            - severity: Categorical label
            - description: Investor-friendly explanation
    """
    if df.empty:
        return []
    
    latest = df.iloc[-1]
    
    # Define signal mappings with investor-friendly names and descriptions
    signal_definitions = {
        'execution_risk_signal': {
            'name': 'Execution Velocity',
            'description': 'Development momentum and task completion rate'
        },
        'team_health_risk_signal': {
            'name': 'Team Health',
            'description': 'Founder morale and team responsiveness'
        },
        'anomaly_risk_signal': {
            'name': 'Operational Anomaly',
            'description': 'Statistical deviation from normal patterns'
        },
        'spend_risk_signal': {
            'name': 'Burn Rate Stability',
            'description': 'Compute spend volatility and cost control'
        }
    }
    
    # Extract risk levels for available signals
    signals = []
    for signal_key, signal_meta in signal_definitions.items():
        if signal_key in latest:
            risk_level = latest[signal_key] * 100  # Convert to 0-100 scale
            signals.append({
                'signal_name': signal_meta['name'],
                'risk_level': round(risk_level, 1),
                'severity': label_risk_severity(risk_level),
                'description': signal_meta['description']
            })
    
    # Sort by risk level (descending) and return top N
    signals.sort(key=lambda x: x['risk_level'], reverse=True)
    return signals[:top_n]


def prepare_ai_reasoning_context(
    df: pd.DataFrame,
    risk_score: float,
    startup_name: str = "Target Portfolio Company"
) -> Dict[str, Any]:
    """
    Prepare a structured dictionary of metrics for Azure OpenAI reasoning.
    
    This function creates a comprehensive context package that contains:
    - Overall risk assessment
    - Time-series trends
    - Critical signal breakdown
    - Operational metrics
    
    This context is designed to be fed into Azure OpenAI GPT-4 to generate
    investor-grade risk reports with explanations and recommendations.
    
    Args:
        df: DataFrame with full feature engineering and risk signals
        risk_score: Computed risk score (0-100)
        startup_name: Name of the startup being analyzed
    
    Returns:
        Dictionary containing structured metrics for AI reasoning
    """
    if df.empty:
        return {}
    
    latest = df.iloc[-1]
    severity = label_risk_severity(risk_score)
    
    # ============================================================
    # EXECUTIVE SUMMARY METRICS
    # ============================================================
    
    context = {
        'startup_name': startup_name,
        'analysis_date': latest['date'].strftime('%Y-%m-%d') if pd.notna(latest['date']) else 'N/A',
        'risk_score': round(risk_score, 1),
        'risk_severity': severity,
        'severity_color': get_severity_color(severity),
        
        # ============================================================
        # OPERATIONAL HEALTH METRICS
        # ============================================================
        
        'operational_metrics': {
            'commit_velocity_7d': round(latest.get('commit_rolling_7d', 0), 1),
            'task_completion_rate': round((1 - latest.get('task_miss_rate', 0)) * 100, 1),
            'founder_morale_score': round(latest.get('founder_morale_score', 0), 1),
            'avg_response_time_hours': round(latest.get('avg_response_time_hours', 0), 1),
            'daily_compute_spend_usd': round(latest.get('compute_spend_usd', 0), 2),
            'execution_health_score': round(latest.get('execution_health', 0) * 100, 1)
        },
        
        # ============================================================
        # TREND ANALYSIS
        # ============================================================
        
        'trends': {
            'morale_trend': _interpret_trend(latest.get('morale_trend_7d', 0)),
            'commit_velocity_change': _interpret_trend(latest.get('commit_velocity_change', 0)),
            'spend_change_pct': round(latest.get('spend_change_pct', 0), 1),
            'is_anomaly_detected': bool(latest.get('is_anomaly', False))
        },
        
        # ============================================================
        # RISK COMPONENT BREAKDOWN
        # ============================================================
        
        'risk_components': {
            'execution_risk': round(latest.get('execution_risk_signal', 0) * 100, 1),
            'team_health_risk': round(latest.get('team_health_risk_signal', 0) * 100, 1),
            'anomaly_risk': round(latest.get('anomaly_risk_signal', 0) * 100, 1),
            'spend_risk': round(latest.get('spend_risk_signal', 0) * 100, 1)
        },
        
        # ============================================================
        # TOP CONTRIBUTING SIGNALS
        # ============================================================
        
        'top_risk_signals': extract_top_signals(df, top_n=3),
        
        # ============================================================
        # HISTORICAL CONTEXT (7-day window)
        # ============================================================
        
        'historical_context': _get_historical_summary(df, window=7)
    }
    
    return context


def _interpret_trend(value: float) -> str:
    """
    Convert numerical trend value to investor-friendly label.
    
    Args:
        value: Trend slope or change value
    
    Returns:
        Trend label: "Improving", "Stable", "Declining"
    """
    if abs(value) < 0.1:
        return "Stable"
    elif value > 0:
        return "Improving"
    else:
        return "Declining"


def _get_historical_summary(df: pd.DataFrame, window: int = 7) -> Dict[str, Any]:
    """
    Generate summary statistics for recent historical window.
    
    Args:
        df: DataFrame with time-series data
        window: Number of days to summarize
    
    Returns:
        Dictionary with historical statistics
    """
    if len(df) < window:
        window = len(df)
    
    if window == 0:
        return {}
    
    recent = df.tail(window)
    
    return {
        'avg_commits_per_day': round(recent['commit_count'].mean(), 1) if 'commit_count' in recent else 0,
        'avg_task_miss_rate': round(recent['task_miss_rate'].mean(), 3) if 'task_miss_rate' in recent else 0,
        'morale_volatility': round(recent['founder_morale_score'].std(), 2) if 'founder_morale_score' in recent else 0,
        'avg_daily_spend': round(recent['compute_spend_usd'].mean(), 2) if 'compute_spend_usd' in recent else 0,
        'days_analyzed': window
    }


def generate_intervention_recommendations(
    risk_score: float,
    top_signals: List[Dict[str, Any]]
) -> List[str]:
    """
    Generate actionable intervention recommendations based on risk profile.
    
    This translates risk scores into specific actions VCs can take.
    
    Args:
        risk_score: Overall risk score (0-100)
        top_signals: List of top contributing risk signals
    
    Returns:
        List of recommendation strings
    """
    recommendations = []
    severity = label_risk_severity(risk_score)
    
    # ============================================================
    # SEVERITY-BASED RECOMMENDATIONS
    # ============================================================
    
    if severity == "High":
        recommendations.append("Schedule immediate founder check-in call")
        recommendations.append("Review burn rate and runway calculations")
        recommendations.append("Assess need for emergency bridge funding or cost reduction")
    
    elif severity == "Medium":
        recommendations.append("Increase monitoring frequency to weekly")
        recommendations.append("Request updated financial projections")
        recommendations.append("Prepare contingency plans for potential deterioration")
    
    else:  # Low
        recommendations.append("Continue standard monthly monitoring")
        recommendations.append("Maintain current support level")
    
    # ============================================================
    # SIGNAL-SPECIFIC RECOMMENDATIONS
    # ============================================================
    
    if not top_signals:
        return recommendations
    
    # Check top contributing signal
    top_signal = top_signals[0]
    signal_name = top_signal.get('signal_name', '')
    
    if 'Execution' in signal_name:
        recommendations.append("Review product roadmap and engineering capacity")
        recommendations.append("Consider technical advisory support or talent introductions")
    
    if 'Team Health' in signal_name:
        recommendations.append("Assess founder wellbeing and team dynamics")
        recommendations.append("Evaluate need for executive coaching or HR support")
    
    if 'Burn Rate' in signal_name:
        recommendations.append("Conduct detailed spend analysis")
        recommendations.append("Review infrastructure optimization opportunities")
    
    if 'Anomaly' in signal_name:
        recommendations.append("Investigate operational deviations in detail")
        recommendations.append("Request explanation for unusual patterns")
    
    return recommendations


def format_risk_report(context: Dict[str, Any]) -> str:
    """
    Format risk analysis context into a human-readable text report.
    
    This is useful for logging, debugging, or quick text-based summaries.
    Not intended for production UI (use structured context instead).
    
    Args:
        context: Dictionary from prepare_ai_reasoning_context()
    
    Returns:
        Formatted text report string
    """
    if not context:
        return "No data available for report generation."
    
    lines = []
    lines.append("=" * 70)
    lines.append(f"PORTFOLIO RISK INTELLIGENCE REPORT")
    lines.append("=" * 70)
    lines.append(f"Company: {context['startup_name']}")
    lines.append(f"Analysis Date: {context['analysis_date']}")
    lines.append(f"Risk Score: {context['risk_score']} / 100")
    lines.append(f"Risk Severity: {context['risk_severity']}")
    lines.append("")
    
    # Operational metrics
    lines.append("OPERATIONAL HEALTH:")
    lines.append("-" * 70)
    ops = context.get('operational_metrics', {})
    lines.append(f"  Commit Velocity (7d):     {ops.get('commit_velocity_7d', 0)}")
    lines.append(f"  Task Completion Rate:     {ops.get('task_completion_rate', 0)}%")
    lines.append(f"  Founder Morale:           {ops.get('founder_morale_score', 0)} / 10")
    lines.append(f"  Execution Health:         {ops.get('execution_health_score', 0)} / 100")
    lines.append("")
    
    # Risk breakdown
    lines.append("RISK COMPONENT BREAKDOWN:")
    lines.append("-" * 70)
    components = context.get('risk_components', {})
    lines.append(f"  Execution Risk:           {components.get('execution_risk', 0)}")
    lines.append(f"  Team Health Risk:         {components.get('team_health_risk', 0)}")
    lines.append(f"  Anomaly Risk:             {components.get('anomaly_risk', 0)}")
    lines.append(f"  Spend Risk:               {components.get('spend_risk', 0)}")
    lines.append("")
    
    # Top signals
    lines.append("TOP CONTRIBUTING SIGNALS:")
    lines.append("-" * 70)
    for i, signal in enumerate(context.get('top_risk_signals', []), 1):
        lines.append(f"  {i}. {signal['signal_name']}: {signal['risk_level']} ({signal['severity']})")
        lines.append(f"     {signal['description']}")
    
    lines.append("=" * 70)
    
    return "\n".join(lines)


def export_to_dict(df: pd.DataFrame, risk_score: float) -> Dict[str, Any]:
    """
    Export complete analysis to a serializable dictionary.
    
    Useful for API responses, database storage, or Azure Function outputs.
    
    Args:
        df: Processed DataFrame with all features and risk signals
        risk_score: Computed risk score
    
    Returns:
        Complete analysis as dictionary (JSON-serializable)
    """
    context = prepare_ai_reasoning_context(df, risk_score)
    
    # Add recommendations
    top_signals = context.get('top_risk_signals', [])
    context['recommendations'] = generate_intervention_recommendations(
        risk_score,
        top_signals
    )
    
    # Add metadata
    context['metadata'] = {
        'analysis_engine': 'Portfolio Risk Intelligence v1.0',
        'data_points_analyzed': len(df),
        'date_range': {
            'start': df['date'].min().strftime('%Y-%m-%d') if not df.empty else None,
            'end': df['date'].max().strftime('%Y-%m-%d') if not df.empty else None
        },
        'generated_at': datetime.now().isoformat()
    }
    
    return context
