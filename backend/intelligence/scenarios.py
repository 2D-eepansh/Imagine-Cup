"""Scenario modeling: precomputed intervention outcomes.

Shows what happens with no/early/delayed intervention without live simulation.
Scenarios are deterministic trajectories based on historical patterns.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np

from feature_engineering import engineer_features
from risk_model import compute_risk_score
from portfolio_utils import label_risk_severity


def compute_intervention_scenarios(
    df: pd.DataFrame,
    current_risk: float,
    current_severity: str,
    archetype: str,
) -> Dict[str, Any]:
    """Precompute three intervention scenarios.
    
    Scenarios:
    1. no_intervention: default trajectory (current state)
    2. early_intervention: operational support after first signal
    3. delayed_intervention: action after risk becomes severe
    
    Returns outcome projections (not simulations).
    """
    
    # Base scenario: no intervention (current reality)
    no_intervention = {
        'label': 'No Intervention',
        'description': 'Continue current trajectory without operational support',
        'projected_30d_risk': _project_no_intervention(current_risk, archetype),
        'projected_60d_risk': _project_no_intervention(current_risk, archetype, days=60),
        'outcome': _outcome_no_intervention(current_severity, archetype),
    }
    
    # Early intervention: support provided shortly after first signal
    early_intervention = {
        'label': 'Early Intervention',
        'description': 'Operational support and advisory provided when risk first exceeded 40',
        'projected_30d_risk': _project_early_intervention(current_risk, archetype),
        'projected_60d_risk': _project_early_intervention(current_risk, archetype, days=60),
        'outcome': _outcome_early_intervention(current_severity, archetype),
    }
    
    # Delayed intervention: action after severity
    delayed_intervention = {
        'label': 'Delayed Intervention',
        'description': 'Action taken only after risk exceeded 60',
        'projected_30d_risk': _project_delayed_intervention(current_risk, archetype),
        'projected_60d_risk': _project_delayed_intervention(current_risk, archetype, days=60),
        'outcome': _outcome_delayed_intervention(current_severity, archetype),
    }
    
    return {
        'no_intervention': no_intervention,
        'early_intervention': early_intervention,
        'delayed_intervention': delayed_intervention,
        'assumptions': 'Projections based on historical portfolio patterns for similar archetypes.',
    }


def _project_no_intervention(current_risk: float, archetype: str, days: int = 30) -> float:
    """Project risk continuation without support."""
    if archetype in ['post_hype_collapse', 'silent_failure']:
        # Deteriorating archetypes continue to worsen
        delta = 8 if days == 30 else 15
        return min(100, current_risk + delta)
    elif archetype == 'zombie':
        # Zombies stay flat
        return current_risk + np.random.default_rng(42).normal(0, 2)
    elif archetype in ['false_recovery']:
        # False recovery regresses
        delta = 5 if days == 30 else 12
        return min(100, current_risk + delta)
    elif archetype in ['true_turnaround', 'consistent_winner']:
        # Positive momentum continues
        delta = -3 if days == 30 else -6
        return max(0, current_risk + delta)
    else:
        return current_risk


def _project_early_intervention(current_risk: float, archetype: str, days: int = 30) -> float:
    """Project outcome with early operational support."""
    if archetype in ['post_hype_collapse', 'silent_failure']:
        # Early support stabilizes but doesn't reverse immediately
        delta = -2 if days == 30 else -5
        return max(30, current_risk + delta)  # Floor at 30 (medium)
    elif archetype == 'zombie':
        # Zombies can show modest improvement with help
        delta = -5 if days == 30 else -10
        return max(25, current_risk + delta)
    elif archetype == 'false_recovery':
        # Can prevent regression
        delta = -4 if days == 30 else -8
        return max(35, current_risk + delta)
    elif archetype in ['true_turnaround', 'consistent_winner']:
        # Already improving; intervention accelerates
        delta = -8 if days == 30 else -15
        return max(15, current_risk + delta)
    else:
        return max(30, current_risk - 5)


def _project_delayed_intervention(current_risk: float, archetype: str, days: int = 30) -> float:
    """Project outcome with late intervention."""
    if archetype in ['post_hype_collapse', 'silent_failure']:
        # Late action slows decline but damage is done
        delta = 3 if days == 30 else 7
        return min(95, current_risk + delta)  # Near ceiling
    elif archetype == 'zombie':
        # Late help has minimal effect on zombies
        delta = 0 if days == 30 else -2
        return current_risk + delta
    elif archetype == 'false_recovery':
        # Too late to prevent regression
        delta = 2 if days == 30 else 5
        return min(90, current_risk + delta)
    elif archetype in ['true_turnaround', 'consistent_winner']:
        # Less effective but still helps
        delta = -4 if days == 30 else -7
        return max(20, current_risk + delta)
    else:
        return current_risk


def _outcome_no_intervention(severity: str, archetype: str) -> str:
    """Describe likely outcome without action."""
    if severity == 'high' and archetype in ['post_hype_collapse', 'silent_failure']:
        return 'Likely failure within 90 days; team attrition and missed fundraise window highly probable.'
    elif severity == 'high':
        return 'Continued operational distress; extended runway burn without revenue traction.'
    elif severity == 'medium' and archetype in ['zombie', 'false_recovery']:
        return 'Persistent stagnation; unlikely to achieve next milestone or valuation inflection.'
    elif severity == 'medium':
        return 'Moderate risk persists; execution gaps remain unaddressed.'
    else:
        return 'Trajectory stable; standard monitoring sufficient.'


def _outcome_early_intervention(severity: str, archetype: str) -> str:
    """Describe outcome with early support."""
    if severity == 'high' and archetype in ['post_hype_collapse', 'silent_failure']:
        return 'Stabilization achievable; operational reset extends runway by 4-6 months with advisory support.'
    elif severity == 'high':
        return 'Significant improvement likely; execution gaps addressable before critical mass attrition.'
    elif severity == 'medium':
        return 'De-risking trajectory; proactive support prevents escalation to high-risk state.'
    else:
        return 'Accelerated improvement; early support compounds positive momentum.'


def _outcome_delayed_intervention(severity: str, archetype: str) -> str:
    """Describe outcome with late action."""
    if severity == 'high' and archetype in ['post_hype_collapse', 'silent_failure']:
        return 'Limited salvage potential; team cohesion and market position materially degraded.'
    elif severity == 'high':
        return 'Partial stabilization possible but costly; bridge financing likely required.'
    elif severity == 'medium':
        return 'Intervention effective but requires more capital and time than early action.'
    else:
        return 'Modest gains; delayed timing reduces leverage and compounds inefficiencies.'
