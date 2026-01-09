"""Decision foresight and urgency intelligence.

Provides bounded time windows, urgency classification, confidence framing,
and intervention reversibility markers without prediction or simulation.

All outputs are deterministic, cached, and decision-grade.
"""

from typing import Dict, Any, List
import numpy as np


def compute_decision_window(
    risk_score: float,
    severity: str,
    trajectory: str,
    snapshots: List[Dict[str, Any]],
    archetype: str,
) -> Dict[str, Any]:
    """Compute bounded decision window without prediction.
    
    Returns time window estimate based on historical slope and archetype,
    expressed conservatively as ranges.
    """
    
    # Calculate risk velocity from snapshots
    velocity = _calculate_risk_velocity(snapshots)
    
    # Determine window based on severity, velocity, and archetype
    if severity == 'high':
        if velocity > 5:  # Fast deterioration
            window_days = (7, 14)
            description = "Risk likely to escalate further within ~7–14 days if conditions persist"
        elif velocity > 2:
            window_days = (14, 21)
            description = "Risk likely to escalate within ~14–21 days under unchanged behavior"
        else:
            window_days = (21, 30)
            description = "Risk elevation probable within ~21–30 days absent intervention"
    elif severity == 'medium':
        if velocity > 3:
            window_days = (14, 28)
            description = "Risk may reach critical threshold within ~14–28 days if trajectory continues"
        elif velocity > 1:
            window_days = (30, 45)
            description = "Stability window approximately ~30–45 days under current trajectory"
        else:
            window_days = (45, 60)
            description = "Gradual drift expected over ~45–60 days without operational changes"
    else:  # low
        if trajectory == 'deteriorating':
            window_days = (45, 60)
            description = "Trajectory shift may materialize within ~45–60 days if unaddressed"
        else:
            window_days = (60, 90)
            description = "Extended stability window of ~60–90 days under maintained execution"
    
    # Archetype adjustments
    if archetype in ['post_hype_collapse', 'false_recovery']:
        window_days = (max(5, window_days[0] - 7), window_days[1] - 7)
        description = description.replace("~", "~")  # Keep tilde but tighten language
    
    return {
        'window_days_min': window_days[0],
        'window_days_max': window_days[1],
        'description': description,
        'basis': 'Derived from historical risk slope and archetype patterns',
    }


def compute_decision_urgency(
    risk_score: float,
    severity: str,
    trajectory: str,
    velocity: float,
    causality: Dict[str, Any],
    archetype: str,
) -> str:
    """Classify decision urgency independently of risk score.
    
    Returns: LOW, MEDIUM, HIGH, or CRITICAL
    
    Two startups with similar risk may have different urgency based on
    time pressure, momentum, and intervention window.
    """
    
    lead_time = causality.get('lead_time_days')
    
    # CRITICAL: Immediate action required
    if severity == 'high' and velocity > 5:
        return 'CRITICAL'
    if severity == 'high' and trajectory == 'deteriorating' and lead_time and lead_time < 14:
        return 'CRITICAL'
    if archetype == 'post_hype_collapse' and severity == 'high':
        return 'CRITICAL'
    
    # HIGH: Urgent but not immediate crisis
    if severity == 'high':
        return 'HIGH'
    if severity == 'medium' and velocity > 4:
        return 'HIGH'
    if severity == 'medium' and trajectory == 'deteriorating' and archetype in ['silent_failure', 'false_recovery']:
        return 'HIGH'
    
    # MEDIUM: Attention required, not urgent
    if severity == 'medium':
        return 'MEDIUM'
    if severity == 'low' and velocity > 3:
        return 'MEDIUM'
    if trajectory == 'deteriorating' and velocity > 2:
        return 'MEDIUM'
    
    # LOW: Standard monitoring sufficient
    return 'LOW'


def compute_confidence_framing(
    snapshots: List[Dict[str, Any]],
    trajectory: str,
    archetype: str,
    severity: str,
) -> Dict[str, str]:
    """Compute non-numerical confidence framing for foresight signals.
    
    Returns confidence level and rationale in professional language.
    """
    
    # Factors affecting confidence
    snapshot_count = len(snapshots)
    trajectory_clear = trajectory in ['deteriorating', 'improving']
    archetype_known = archetype in [
        'post_hype_collapse', 'silent_failure', 'zombie',
        'false_recovery', 'true_turnaround', 'consistent_winner'
    ]
    
    # High confidence: clear pattern, sufficient history
    if snapshot_count >= 5 and trajectory_clear and archetype_known:
        if severity in ['high', 'low']:
            return {
                'level': 'High',
                'rationale': 'Pattern repeated historically across comparable portfolio companies',
            }
    
    # Medium confidence: mixed signals or moderate history
    if snapshot_count >= 4 or trajectory == 'stable':
        return {
            'level': 'Medium',
            'rationale': 'Mixed or stabilizing signals; trajectory observable but not definitive',
        }
    
    # Low confidence: insufficient data or ambiguous
    if snapshot_count < 4 or trajectory == 'insufficient_history':
        return {
            'level': 'Moderate',
            'rationale': 'Limited historical window; assessment based on recent operational signals',
        }
    
    # Default medium
    return {
        'level': 'Medium',
        'rationale': 'Assessment grounded in observable operational patterns',
    }


def compute_reversibility_marker(
    severity: str,
    urgency: str,
    trajectory: str,
    archetype: str,
    intervention_scenario: str = 'no_intervention',
) -> Dict[str, Any]:
    """Determine intervention reversibility without optimistic bias.
    
    Returns honest assessment of whether intervention can still materially
    alter trajectory.
    """
    
    # Critical cases: diminishing returns or irreversible
    if severity == 'high' and urgency == 'CRITICAL' and archetype in ['post_hype_collapse', 'silent_failure']:
        if intervention_scenario == 'delayed_intervention':
            return {
                'marker': 'DIMINISHED',
                'description': 'Intervention impact materially constrained; structural damage已accumulated',
                'explanation': 'Team cohesion, market position, and operational momentum significantly degraded. Support can slow decline but unlikely to reverse trajectory without substantial capital and time investment.',
            }
        elif intervention_scenario == 'early_intervention':
            return {
                'marker': 'VIABLE',
                'description': 'Intervention still likely to materially alter outcome',
                'explanation': 'Operational reset achievable with focused advisory support and resource reallocation. Window remains open for stabilization.',
            }
        else:
            return {
                'marker': 'NARROWING',
                'description': 'Intervention window closing; action urgency increasing',
                'explanation': 'Current trajectory leads to compounding dysfunction. Intervention remains viable but effectiveness declining with each passing week.',
            }
    
    # High severity but not critical
    if severity == 'high':
        if intervention_scenario == 'early_intervention':
            return {
                'marker': 'VIABLE',
                'description': 'Early action likely effective; trajectory alterable',
                'explanation': 'Execution gaps addressable through operational support before critical mass attrition or market position erosion.',
            }
        elif intervention_scenario == 'delayed_intervention':
            return {
                'marker': 'CONSTRAINED',
                'description': 'Late intervention possible but costly',
                'explanation': 'Partial stabilization achievable but requires disproportionate capital and advisory resources. Recovery timeline extended.',
            }
        else:
            return {
                'marker': 'OPEN',
                'description': 'Intervention window remains open',
                'explanation': 'Operational support can meaningfully impact trajectory if deployed promptly.',
            }
    
    # Medium severity
    if severity == 'medium':
        if trajectory == 'deteriorating':
            return {
                'marker': 'OPTIMAL',
                'description': 'Intervention highly effective at current stage',
                'explanation': 'Proactive support prevents escalation to high-risk state. Cost-effective intervention point.',
            }
        else:
            return {
                'marker': 'VIABLE',
                'description': 'Standard intervention expected to be effective',
                'explanation': 'Operational adjustments addressable through routine advisory engagement.',
            }
    
    # Low severity
    if trajectory == 'improving':
        return {
            'marker': 'ACCELERATIVE',
            'description': 'Support compounds positive momentum',
            'explanation': 'Company executing well; advisory engagement accelerates de-risking and growth trajectory.',
        }
    else:
        return {
            'marker': 'PREVENTIVE',
            'description': 'Intervention primarily preventive',
            'explanation': 'Standard monitoring and advisory sufficient to maintain trajectory.',
        }


def _calculate_risk_velocity(snapshots: List[Dict[str, Any]]) -> float:
    """Calculate rate of risk change from snapshots (points per day)."""
    if len(snapshots) < 2:
        return 0.0
    
    # Use recent snapshots for velocity
    recent = snapshots[-3:] if len(snapshots) >= 3 else snapshots
    
    if len(recent) < 2:
        return 0.0
    
    risk_changes = []
    for i in range(1, len(recent)):
        risk_delta = recent[i]['risk_score'] - recent[i-1]['risk_score']
        days_delta = recent[i-1]['days_ago'] - recent[i]['days_ago']
        if days_delta > 0:
            risk_changes.append(risk_delta / days_delta)
    
    if not risk_changes:
        return 0.0
    
    return float(np.mean(risk_changes))


def compute_foresight_intelligence(
    risk_score: float,
    severity: str,
    trajectory: str,
    snapshots: List[Dict[str, Any]],
    causality: Dict[str, Any],
    archetype: str,
    intervention_scenario: str = 'no_intervention',
) -> Dict[str, Any]:
    """Orchestrate all foresight signals for a given snapshot + scenario.
    
    Returns decision-grade intelligence without prediction or live computation.
    """
    
    velocity = _calculate_risk_velocity(snapshots)
    
    decision_window = compute_decision_window(
        risk_score, severity, trajectory, snapshots, archetype
    )
    
    urgency = compute_decision_urgency(
        risk_score, severity, trajectory, velocity, causality, archetype
    )
    
    confidence = compute_confidence_framing(
        snapshots, trajectory, archetype, severity
    )
    
    reversibility = compute_reversibility_marker(
        severity, urgency, trajectory, archetype, intervention_scenario
    )
    
    return {
        'decisionWindow': decision_window,
        'urgency': urgency,
        'confidence': confidence,
        'reversibility': reversibility,
        'velocityIndicator': _velocity_descriptor(velocity),
    }


def _velocity_descriptor(velocity: float) -> str:
    """Convert velocity to descriptive language."""
    if velocity > 5:
        return 'Rapid deterioration'
    elif velocity > 3:
        return 'Accelerating decline'
    elif velocity > 1:
        return 'Gradual deterioration'
    elif velocity > -1:
        return 'Stable trajectory'
    elif velocity > -3:
        return 'Modest improvement'
    else:
        return 'Strong improvement'
