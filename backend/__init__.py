"""
Portfolio Risk Intelligence System

Enterprise-grade risk detection for venture capital firms.
"""

__version__ = "1.0.0"
__author__ = "Portfolio Intelligence Team"

from .feature_engineering import engineer_features, get_feature_summary
from .risk_model import compute_risk_score, get_risk_components, get_risk_trend
from .portfolio_utils import (
    label_risk_severity,
    prepare_ai_reasoning_context,
    generate_intervention_recommendations,
    export_to_dict
)

__all__ = [
    'engineer_features',
    'get_feature_summary',
    'compute_risk_score',
    'get_risk_components',
    'get_risk_trend',
    'label_risk_severity',
    'prepare_ai_reasoning_context',
    'generate_intervention_recommendations',
    'export_to_dict'
]
