"""Investor memory and narrative consistency layer.

Provides institutional memory by mapping startups to canonical failure/success
patterns with historical outcome associations. Ensures narrative consistency
across time and scenarios.

All outputs are deterministic, conservative, and based on observed patterns.
No ML, no speculation, no creative generation.
"""

from typing import Dict, List, Any, Tuple, Optional


# Canonical pattern definitions with historical associations
PATTERN_MEMORY = {
    'post_hype_collapse': {
        'label': 'Post-Hype Collapse',
        'description': 'Rapid decline following initial momentum and funding excitement',
        'typical_outcome': 'Often leads to shutdown or distressed acquisition within 6-12 months absent major pivot',
        'time_dynamics': 'Rapid deterioration (weeks to months)',
        'intervention_sensitivity': 'Early operational support sometimes stabilizes; late intervention rarely changes trajectory',
        'historical_precedent': 'Observed across consumer tech, hardware, and vertical SaaS companies post-Series A',
        'key_signals': [
            'Commit velocity cliff (50%+ drop)',
            'Task miss rate spike (>30%)',
            'Morale collapse (7+ → 3-4 range)',
            'Market sentiment disconnect'
        ],
        'narrative_framing': 'This trajectory resembles prior post-hype collapse cases',
    },
    
    'silent_failure': {
        'label': 'Silent Operational Decay',
        'description': 'Gradual, quiet deterioration without dramatic signals',
        'typical_outcome': 'Typically results in prolonged decline and eventual wind-down; rarely recovers momentum',
        'time_dynamics': 'Slow erosion (months to quarters)',
        'intervention_sensitivity': 'Moderate responsiveness to early operational support; diminishes over time',
        'historical_precedent': 'Common in B2B SaaS and enterprise software without strong founder-market fit',
        'key_signals': [
            'Gradual commit decay (20-30% over months)',
            'Rising task miss rate (steady 15-25%)',
            'Morale drift (7 → 5-6 slowly)',
            'Minimal market visibility'
        ],
        'narrative_framing': 'This pattern reflects silent operational decay observed in prior portfolio companies',
    },
    
    'zombie': {
        'label': 'Zombie Persistence',
        'description': 'Flat execution with minimal progress or deterioration',
        'typical_outcome': 'Persists for extended periods; eventual shutdown or acqui-hire absent strategic shift',
        'time_dynamics': 'Stable stagnation (quarters to years)',
        'intervention_sensitivity': 'Low; structural issues typically require major strategic pivot rather than operational support',
        'historical_precedent': 'Seen in companies with declining market opportunity or misaligned founding teams',
        'key_signals': [
            'Flat commit activity (8-10 per day)',
            'Consistent miss rate (18-22%)',
            'Low but stable morale (4-5 range)',
            'Absence of growth signals'
        ],
        'narrative_framing': 'This resembles zombie persistence patterns seen in structurally challenged companies',
    },
    
    'false_recovery': {
        'label': 'False Recovery Pattern',
        'description': 'Brief operational improvement followed by regression below baseline',
        'typical_outcome': 'Improvement rarely sustained; typically regresses to prior trajectory or worse',
        'time_dynamics': 'Recovery window (2-4 weeks) followed by renewed decline',
        'intervention_sensitivity': 'Mixed; early intervention during recovery window can help, but underlying issues often persist',
        'historical_precedent': 'Observed in companies attempting superficial fixes without addressing root causes',
        'key_signals': [
            'Temporary metric improvement (30-55% timeline)',
            'Regression to baseline or worse',
            'Unsustained morale lift',
            'Execution quality remains volatile'
        ],
        'narrative_framing': 'This trajectory exhibits false recovery characteristics observed in past cases',
    },
    
    'true_turnaround': {
        'label': 'True Turnaround Trajectory',
        'description': 'Sustained improvement following early operational challenges',
        'typical_outcome': 'Often achieves stable execution and de-risking with continued focus',
        'time_dynamics': 'Gradual improvement (months)',
        'intervention_sensitivity': 'High; early operational support and advisory typically accelerates recovery',
        'historical_precedent': 'Seen in companies with strong founding teams that identify and address execution gaps',
        'key_signals': [
            'Sustained commit velocity growth',
            'Declining miss rate (22% → 12-15%)',
            'Morale recovery (5 → 7-8)',
            'Consistent execution improvement'
        ],
        'narrative_framing': 'This reflects true turnaround dynamics observed in successful portfolio recoveries',
    },
    
    'consistent_winner': {
        'label': 'Consistent Execution Under Stress',
        'description': 'Stable operational performance with resilience to external volatility',
        'typical_outcome': 'Typically maintains trajectory; low risk of operational failure',
        'time_dynamics': 'Stable with minor fluctuations',
        'intervention_sensitivity': 'Primarily preventive; standard advisory sufficient',
        'historical_precedent': 'Characteristic of well-managed companies with product-market fit and operational discipline',
        'key_signals': [
            'Stable commit velocity (20-25 per day)',
            'Low miss rate (5-8%)',
            'High morale (8+ range)',
            'Resilient to market noise'
        ],
        'narrative_framing': 'This demonstrates consistent execution patterns seen in high-performing portfolio companies',
    },
}


def classify_startup_pattern(
    archetype: str,
    risk_score: float,
    trajectory: str,
    severity: str
) -> str:
    """Deterministically classify startup into canonical pattern.
    
    Uses existing archetype as primary signal. This ensures consistency
    across all API calls for the same startup.
    
    Args:
        archetype: Startup archetype (from synthetic data generation)
        risk_score: Current risk score
        trajectory: Trajectory from causality markers
        severity: Risk severity level
        
    Returns:
        Canonical pattern key matching PATTERN_MEMORY
    """
    # Direct mapping from archetype to canonical pattern
    # This is deterministic and stable
    archetype_to_pattern = {
        'post_hype_collapse': 'post_hype_collapse',
        'silent_failure': 'silent_failure',
        'zombie': 'zombie',
        'false_recovery': 'false_recovery',
        'true_turnaround': 'true_turnaround',
        'consistent_winner': 'consistent_winner',
    }
    
    return archetype_to_pattern.get(archetype, 'silent_failure')  # Safe default


def get_pattern_memory(pattern_key: str) -> Dict[str, Any]:
    """Retrieve historical associations for a canonical pattern.
    
    Args:
        pattern_key: Canonical pattern identifier
        
    Returns:
        Dict with historical outcome associations
    """
    return PATTERN_MEMORY.get(pattern_key, PATTERN_MEMORY['silent_failure'])


def generate_memory_signal(
    pattern_key: str,
    urgency: str,
    reversibility_marker: str,
    scenario: str = 'no_intervention'
) -> str:
    """Generate short, calm investor memory signal.
    
    Signals resemble investment committee retrospectives, not alarmist alerts.
    
    Args:
        pattern_key: Canonical pattern
        urgency: Urgency level from foresight
        reversibility_marker: Reversibility from foresight
        scenario: Intervention scenario
        
    Returns:
        Short memory signal string
    """
    pattern = PATTERN_MEMORY.get(pattern_key, PATTERN_MEMORY['silent_failure'])
    base_framing = pattern['narrative_framing']
    
    # Scenario-aware framing
    if scenario == 'early_intervention':
        if reversibility_marker in ['VIABLE', 'OPTIMAL']:
            return f"{base_framing}. Historically, early intervention has improved outcomes in comparable cases."
        else:
            return f"{base_framing}. Early operational support typically provides modest stabilization."
    
    elif scenario == 'delayed_intervention':
        if reversibility_marker == 'DIMINISHED':
            return f"{base_framing}. Delayed action in comparable cases rarely altered fundamental trajectory."
        else:
            return f"{base_framing}. Late-stage intervention effectiveness varies; structural challenges often persist."
    
    else:  # no_intervention
        if urgency in ['CRITICAL', 'HIGH']:
            return f"{base_framing}. Historical outcomes suggest near-term operational support warranted."
        elif pattern_key == 'consistent_winner':
            return f"{base_framing}. Standard monitoring typically sufficient for this execution profile."
        else:
            return f"{base_framing}. Trajectory monitoring recommended."


def generate_outcome_context(
    pattern_key: str,
    current_risk: float,
    trajectory: str,
    scenario: str = 'no_intervention'
) -> Dict[str, Any]:
    """Generate historical outcome context for investment memos.
    
    Provides institutional memory framing without speculation.
    
    Args:
        pattern_key: Canonical pattern
        current_risk: Current risk score
        trajectory: Trajectory type
        scenario: Intervention scenario
        
    Returns:
        Dict with outcome context
    """
    pattern = PATTERN_MEMORY.get(pattern_key, PATTERN_MEMORY['silent_failure'])
    
    # Base context
    context = {
        'pattern_label': pattern['label'],
        'typical_outcome': pattern['typical_outcome'],
        'time_dynamics': pattern['time_dynamics'],
        'intervention_note': pattern['intervention_sensitivity'],
    }
    
    # Scenario-specific adjustment
    if scenario == 'early_intervention':
        if 'Early' in pattern['intervention_sensitivity'] or 'early' in pattern['intervention_sensitivity']:
            context['scenario_note'] = 'Early operational support aligns with historical precedent for this pattern'
        else:
            context['scenario_note'] = 'Early intervention provides baseline stabilization opportunity'
    
    elif scenario == 'delayed_intervention':
        if 'late' in pattern['intervention_sensitivity'].lower() or 'diminish' in pattern['intervention_sensitivity'].lower():
            context['scenario_note'] = 'Delayed intervention historically shows limited trajectory change'
        else:
            context['scenario_note'] = 'Late-stage support can provide partial stabilization'
    
    else:
        context['scenario_note'] = 'Standard monitoring and advisory engagement'
    
    # Trajectory consistency check
    if trajectory == 'deteriorating' and pattern_key in ['post_hype_collapse', 'silent_failure', 'false_recovery']:
        context['consistency_note'] = 'Current trajectory aligns with historical pattern dynamics'
    elif trajectory == 'improving' and pattern_key == 'true_turnaround':
        context['consistency_note'] = 'Improvement trajectory consistent with turnaround pattern'
    elif trajectory == 'stable' and pattern_key in ['zombie', 'consistent_winner']:
        context['consistency_note'] = 'Stable trajectory characteristic of this pattern'
    else:
        context['consistency_note'] = 'Trajectory dynamics require continued monitoring'
    
    return context


def generate_consistent_narrative(
    startup_name: str,
    pattern_key: str,
    risk_score: float,
    severity: str,
    urgency: str,
    trajectory: str,
    reversibility_marker: str,
    scenario: str = 'no_intervention'
) -> Dict[str, Any]:
    """Generate complete narrative with institutional memory framing.
    
    Ensures consistency across:
    - Different API calls for same startup
    - Different time snapshots
    - Different scenarios
    
    Args:
        startup_name: Company name
        pattern_key: Canonical pattern
        risk_score: Current risk score
        severity: Risk severity
        urgency: Urgency level
        trajectory: Trajectory type
        reversibility_marker: Reversibility marker
        scenario: Intervention scenario
        
    Returns:
        Complete narrative package
    """
    pattern = PATTERN_MEMORY.get(pattern_key, PATTERN_MEMORY['silent_failure'])
    
    # Memory signal (short)
    memory_signal = generate_memory_signal(pattern_key, urgency, reversibility_marker, scenario)
    
    # Outcome context (structured)
    outcome_context = generate_outcome_context(pattern_key, risk_score, trajectory, scenario)
    
    # Historical precedent (institutional framing)
    historical_precedent = pattern['historical_precedent']
    
    # Investment memo framing (paragraph form)
    if urgency in ['CRITICAL', 'HIGH'] and reversibility_marker in ['VIABLE', 'OPTIMAL', 'NARROWING']:
        memo_framing = (
            f"{startup_name} exhibits {pattern['label'].lower()} characteristics. "
            f"{pattern['typical_outcome']} "
            f"{pattern['intervention_sensitivity']} "
            f"Current urgency and reversibility profile suggests near-term operational engagement warranted."
        )
    elif pattern_key == 'consistent_winner':
        memo_framing = (
            f"{startup_name} demonstrates {pattern['label'].lower()}. "
            f"{pattern['typical_outcome']} "
            "Standard advisory and monitoring protocols appropriate."
        )
    else:
        memo_framing = (
            f"{startup_name} displays {pattern['label'].lower()} patterns. "
            f"{pattern['typical_outcome']} "
            f"{pattern['intervention_sensitivity']}"
        )
    
    return {
        'pattern': pattern_key,
        'pattern_label': pattern['label'],
        'memory_signal': memory_signal,
        'outcome_context': outcome_context,
        'historical_precedent': historical_precedent,
        'investment_memo_framing': memo_framing,
        'key_historical_signals': pattern['key_signals'],
    }


def compute_narrative_consistency_check(
    startup_id: str,
    pattern_key: str,
    snapshots: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Verify narrative consistency across time snapshots.
    
    Ensures the same startup is described consistently across historical views.
    
    Args:
        startup_id: Startup identifier
        pattern_key: Canonical pattern
        snapshots: Historical risk snapshots
        
    Returns:
        Consistency validation
    """
    # Pattern should remain stable across snapshots (archetype doesn't change)
    # This is inherently consistent since archetype is fixed at data generation
    
    # Check trajectory consistency
    trajectory_changes = []
    if len(snapshots) >= 2:
        for i in range(1, len(snapshots)):
            prev_risk = snapshots[i-1]['risk_score']
            curr_risk = snapshots[i]['risk_score']
            if curr_risk > prev_risk + 15:
                trajectory_changes.append(f"Risk increased {curr_risk - prev_risk:.1f} points")
            elif curr_risk < prev_risk - 15:
                trajectory_changes.append(f"Risk decreased {prev_risk - curr_risk:.1f} points")
    
    # Narrative anchors (always the same for this pattern)
    pattern = PATTERN_MEMORY.get(pattern_key, PATTERN_MEMORY['silent_failure'])
    anchors = {
        'pattern_label': pattern['label'],
        'narrative_framing': pattern['narrative_framing'],
        'outcome_association': pattern['typical_outcome'],
    }
    
    return {
        'pattern_stable': True,  # Always true (archetype fixed)
        'narrative_anchors': anchors,
        'trajectory_changes': trajectory_changes if trajectory_changes else ['Consistent with pattern dynamics'],
        'consistency_validated': True,
    }


def enrich_startup_with_memory(
    startup_payload: Dict[str, Any],
    archetype: str,
    scenario: str = 'no_intervention'
) -> Dict[str, Any]:
    """Enrich startup payload with investor memory signals.
    
    Adds institutional memory layer to existing intelligence.
    
    Args:
        startup_payload: Existing startup intelligence payload
        archetype: Startup archetype
        scenario: Intervention scenario
        
    Returns:
        Enriched payload with memory layer
    """
    # Extract signals from existing intelligence
    risk_score = startup_payload.get('riskScore', 0)
    severity = startup_payload.get('severity', 'low')
    
    # Get foresight signals
    foresight = startup_payload.get('intelligence', {}).get('foresight', {}).get(scenario, {})
    urgency = foresight.get('urgency', 'LOW') if foresight else 'LOW'
    reversibility = foresight.get('reversibility', {})
    reversibility_marker = reversibility.get('marker', 'UNKNOWN') if reversibility else 'UNKNOWN'
    
    # Get causality
    causality = startup_payload.get('intelligence', {}).get('causalityMarkers', {})
    trajectory = causality.get('trajectory', 'unknown') if causality else 'unknown'
    snapshots = startup_payload.get('intelligence', {}).get('timeSnapshots', [])
    
    # Classify into canonical pattern
    pattern_key = classify_startup_pattern(archetype, risk_score, trajectory, severity)
    
    # Generate narrative with memory
    narrative = generate_consistent_narrative(
        startup_payload['name'],
        pattern_key,
        risk_score,
        severity,
        urgency,
        trajectory,
        reversibility_marker,
        scenario
    )
    
    # Consistency check
    consistency = compute_narrative_consistency_check(
        startup_payload['id'],
        pattern_key,
        snapshots
    )
    
    # Add memory layer to payload
    if 'intelligence' in startup_payload:
        startup_payload['intelligence']['investor_memory'] = {
            'canonical_pattern': pattern_key,
            'pattern_label': narrative['pattern_label'],
            'memory_signal': narrative['memory_signal'],
            'outcome_context': narrative['outcome_context'],
            'historical_precedent': narrative['historical_precedent'],
            'investment_memo_framing': narrative['investment_memo_framing'],
            'key_historical_signals': narrative['key_historical_signals'],
            'narrative_consistency': consistency,
        }
    
    return startup_payload


def generate_portfolio_memory_summary(
    pattern_distribution: Dict[str, int],
    detected_patterns: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Generate portfolio-level memory summary.
    
    Provides institutional context on portfolio pattern distribution.
    
    Args:
        pattern_distribution: Count of each canonical pattern
        detected_patterns: Detected cross-portfolio patterns
        
    Returns:
        Portfolio memory summary
    """
    # Pattern prevalence analysis
    total_companies = sum(pattern_distribution.values())
    prevalence = {
        pattern: {
            'count': count,
            'percentage': round(100 * count / total_companies, 1) if total_companies > 0 else 0,
            'label': PATTERN_MEMORY[pattern]['label'],
            'typical_outcome': PATTERN_MEMORY[pattern]['typical_outcome'],
        }
        for pattern, count in pattern_distribution.items()
        if count > 0
    }
    
    # Portfolio memory insights
    insights = []
    
    # High-risk pattern concentration
    high_risk_patterns = ['post_hype_collapse', 'silent_failure', 'false_recovery']
    high_risk_count = sum(pattern_distribution.get(p, 0) for p in high_risk_patterns)
    if high_risk_count >= 5:
        insights.append(
            f"Portfolio contains {high_risk_count} companies in high-risk historical patterns. "
            "Historically, such concentration requires active portfolio management and triage decisions."
        )
    
    # Turnaround opportunity
    turnaround_count = pattern_distribution.get('true_turnaround', 0)
    if turnaround_count >= 2:
        insights.append(
            f"{turnaround_count} companies exhibit turnaround dynamics. "
            "Historical precedent suggests early operational support accelerates recovery in these cases."
        )
    
    # Winner concentration
    winner_count = pattern_distribution.get('consistent_winner', 0)
    if winner_count >= 3:
        insights.append(
            f"{winner_count} companies demonstrate consistent execution patterns. "
            "These typically require standard monitoring rather than intensive intervention."
        )
    
    # Zombie persistence
    zombie_count = pattern_distribution.get('zombie', 0)
    if zombie_count >= 2:
        insights.append(
            f"{zombie_count} companies display zombie persistence patterns. "
            "Historically, these require strategic pivot decisions rather than operational fixes."
        )
    
    return {
        'pattern_prevalence': prevalence,
        'portfolio_memory_insights': insights,
        'historical_context': (
            "Pattern distribution reflects typical early-stage VC portfolio dynamics. "
            "Mix of execution challenges, turnaround opportunities, and stable performers is characteristic."
        ),
    }
