"""Portfolio-level attention allocation intelligence.

Helps investors prioritize attention across multiple startups by considering:
- Risk severity + decision urgency + intervention reversibility
- Risk concentration by sector and time
- Cross-startup pattern detection
- Actionable attention summaries for partner meetings

All outputs are deterministic and derived from startup-level intelligence.
No new ML models, no live computation.
"""

from typing import Dict, List, Any, Tuple
from collections import defaultdict, Counter
import numpy as np


def compute_attention_priority(
    startups: List[Dict[str, Any]], 
    scenario: str = 'no_intervention'
) -> List[Dict[str, Any]]:
    """Compute portfolio-wide attention priority ranking.
    
    Priority considers:
    - Risk severity (base signal)
    - Decision urgency (time pressure)
    - Intervention reversibility (action viability)
    
    A time-critical, reversible startup may outrank a higher-risk but
    irreversible one, reflecting rational attention allocation.
    
    Args:
        startups: List of startup payloads with intelligence data
        scenario: Scenario name (no_intervention, early_intervention, delayed_intervention)
        
    Returns:
        List of startups with attention_priority scores, sorted by priority
    """
    scored_startups = []
    
    for startup in startups:
        # Extract base signals
        risk_score = startup.get('riskScore', 0)
        severity = startup.get('severity', 'low')
        
        # Extract foresight from specified scenario
        foresight = startup.get('intelligence', {}).get('foresight', {}).get(scenario, {})
        if not foresight:
            # Fallback if no intelligence data
            scored_startups.append({
                **startup,
                'attention_priority': risk_score,
                'priority_rationale': 'Based on risk score only (no foresight available)',
            })
            continue
        
        urgency = foresight.get('urgency', 'LOW')
        reversibility = foresight.get('reversibility', {}).get('marker', 'UNKNOWN')
        decision_window = foresight.get('decisionWindow', {})
        
        # Compute attention priority (0-100 scale)
        priority_score = _compute_attention_score(
            risk_score, severity, urgency, reversibility, decision_window
        )
        
        # Generate rationale
        rationale = _generate_priority_rationale(
            severity, urgency, reversibility, decision_window
        )
        
        scored_startups.append({
            **startup,
            'attention_priority': round(priority_score, 1),
            'priority_rationale': rationale,
        })
    
    # Sort by attention priority (highest first)
    scored_startups.sort(key=lambda s: s['attention_priority'], reverse=True)
    
    # Add rank
    for rank, startup in enumerate(scored_startups, start=1):
        startup['attention_rank'] = rank
    
    return scored_startups


def _compute_attention_score(
    risk_score: float,
    severity: str,
    urgency: str,
    reversibility: str,
    decision_window: Dict[str, Any]
) -> float:
    """Internal: Compute attention priority score.
    
    Priority = f(risk, urgency, reversibility)
    Not equal to risk score alone.
    """
    # Base from risk score (40% weight)
    base_score = risk_score * 0.4
    
    # Urgency multiplier (30% weight)
    urgency_weights = {
        'CRITICAL': 30.0,
        'HIGH': 22.0,
        'MEDIUM': 12.0,
        'LOW': 5.0,
    }
    urgency_score = urgency_weights.get(urgency, 5.0)
    
    # Reversibility multiplier (30% weight)
    # Higher priority for VIABLE/OPTIMAL (intervention can help)
    # Lower priority for DIMINISHED (likely too late)
    reversibility_weights = {
        'CRITICAL': 25.0,      # Special case: critical state
        'OPTIMAL': 28.0,       # Best intervention point
        'VIABLE': 25.0,        # Intervention likely effective
        'NARROWING': 20.0,     # Window closing
        'OPEN': 20.0,          # Standard window
        'CONSTRAINED': 12.0,   # Possible but costly
        'DIMINISHED': 8.0,     # Limited impact
        'ACCELERATIVE': 15.0,  # Positive momentum
        'PREVENTIVE': 10.0,    # Standard monitoring
    }
    reversibility_score = reversibility_weights.get(reversibility, 10.0)
    
    # Time pressure adjustment (tighter windows = higher priority)
    days_max = decision_window.get('days_max', 30)
    if days_max <= 7:
        time_pressure = 1.2
    elif days_max <= 14:
        time_pressure = 1.1
    elif days_max <= 21:
        time_pressure = 1.0
    else:
        time_pressure = 0.9
    
    # Combine
    priority = (base_score + urgency_score + reversibility_score) * time_pressure
    
    # Cap at 100
    return min(priority, 100.0)


def _generate_priority_rationale(
    severity: str,
    urgency: str,
    reversibility: str,
    decision_window: Dict[str, Any]
) -> str:
    """Internal: Generate human-readable priority rationale."""
    
    # High priority cases
    if urgency == 'CRITICAL' and reversibility in ['VIABLE', 'NARROWING']:
        return "Critical urgency with viable intervention window"
    
    if urgency == 'HIGH' and reversibility == 'OPTIMAL':
        return "High urgency at optimal intervention point"
    
    if urgency in ['HIGH', 'CRITICAL'] and reversibility == 'DIMINISHED':
        return "High urgency but diminished reversibility; triage decision required"
    
    # Medium priority cases
    if urgency == 'MEDIUM' and reversibility in ['VIABLE', 'OPTIMAL']:
        return "Medium urgency with effective intervention opportunity"
    
    if urgency == 'HIGH' and reversibility in ['CONSTRAINED', 'PREVENTIVE']:
        return "Elevated urgency but limited intervention leverage"
    
    # Low priority cases
    if urgency == 'LOW':
        return "Low urgency; standard monitoring sufficient"
    
    # Default
    days_max = decision_window.get('days_max', 30)
    return f"Attention warranted within {days_max}-day window"


def compute_risk_concentration(
    startups: List[Dict[str, Any]],
    scenario: str = 'no_intervention'
) -> Dict[str, Any]:
    """Compute portfolio risk concentration insights.
    
    Identifies:
    - Risk concentration by sector
    - Urgency concentration over time
    - Simultaneous deterioration events
    
    Args:
        startups: List of startup payloads with intelligence
        scenario: Scenario name
        
    Returns:
        Dict with concentration insights
    """
    # Sector concentration
    sector_risks = defaultdict(list)
    sector_urgencies = defaultdict(list)
    
    for startup in startups:
        sector = startup.get('sector', 'Unknown')
        risk = startup.get('riskScore', 0)
        foresight = startup.get('intelligence', {}).get('foresight', {}).get(scenario, {})
        urgency = foresight.get('urgency', 'LOW') if foresight else 'LOW'
        
        sector_risks[sector].append(risk)
        sector_urgencies[sector].append(urgency)
    
    # Calculate sector risk metrics
    sector_analysis = {}
    for sector, risks in sector_risks.items():
        avg_risk = np.mean(risks)
        urgencies = sector_urgencies[sector]
        high_urgency_count = sum(1 for u in urgencies if u in ['HIGH', 'CRITICAL'])
        
        sector_analysis[sector] = {
            'count': len(risks),
            'avg_risk': round(avg_risk, 1),
            'high_urgency_count': high_urgency_count,
        }
    
    # Find concentration hotspot
    hotspot_sector = max(
        sector_analysis.items(),
        key=lambda x: x[1]['avg_risk'] * x[1]['count']
    )[0] if sector_analysis else None
    
    # Urgency concentration
    urgency_counts = Counter()
    for startup in startups:
        foresight = startup.get('intelligence', {}).get('foresight', {}).get(scenario, {})
        urgency = foresight.get('urgency', 'LOW') if foresight else 'LOW'
        urgency_counts[urgency] += 1
    
    # Simultaneous deterioration detection
    deteriorating_count = 0
    for startup in startups:
        causality = startup.get('intelligence', {}).get('causalityMarkers', {})
        trajectory = causality.get('trajectory', 'unknown') if causality else 'unknown'
        if trajectory == 'deteriorating':
            deteriorating_count += 1
    
    # Generate qualitative insights
    insights = []
    
    # Sector concentration insight
    if hotspot_sector and sector_analysis[hotspot_sector]['avg_risk'] > 60:
        insights.append(
            f"Risk concentrated in {hotspot_sector} sector "
            f"({sector_analysis[hotspot_sector]['count']} companies, "
            f"avg risk {sector_analysis[hotspot_sector]['avg_risk']})"
        )
    
    # Urgency concentration insight
    critical_high_count = urgency_counts['CRITICAL'] + urgency_counts['HIGH']
    if critical_high_count >= 3:
        insights.append(
            f"{critical_high_count} startups require near-term intervention "
            f"({urgency_counts['CRITICAL']} critical, {urgency_counts['HIGH']} high urgency)"
        )
    
    # Simultaneous deterioration insight
    if deteriorating_count >= 3:
        insights.append(
            f"Operational decay observed across {deteriorating_count} startups; "
            "potential systemic factor or market shift"
        )
    
    return {
        'sector_concentration': sector_analysis,
        'urgency_distribution': dict(urgency_counts),
        'deteriorating_count': deteriorating_count,
        'hotspot_sector': hotspot_sector,
        'insights': insights,
    }


def detect_cross_startup_patterns(
    startups: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Detect patterns across multiple startups.
    
    Identifies:
    - Common failure patterns (archetypes)
    - Repeated signals (e.g., team disengagement)
    - Correlated deterioration
    
    This is structured comparison, not ML pattern recognition.
    
    Args:
        startups: List of startup payloads with intelligence
        
    Returns:
        Dict with detected patterns
    """
    patterns = {
        'archetype_distribution': defaultdict(int),
        'common_risk_drivers': defaultdict(int),
        'trajectory_clusters': defaultdict(list),
        'market_correlation_signals': [],
    }
    
    # Archetype distribution
    archetype_map = {
        'Lumina Health': 'post_hype_collapse',
        'Quantum Logistics': 'post_hype_collapse',
        'Strata AI': 'post_hype_collapse',
        'Nexus Fintech': 'silent_failure',
        'Beacon Retail': 'silent_failure',
        'Frontier Labs': 'silent_failure',
        'Atlas Robotics': 'zombie',
        'WaveGrid': 'zombie',
        'Aurora Mobility': 'false_recovery',
        'Nova Payments': 'false_recovery',
        'Helix Bio': 'true_turnaround',
        'Pioneer Ops': 'true_turnaround',
        'Verde Climate': 'consistent_winner',
        'Cipher Security': 'consistent_winner',
        'TerraSense': 'consistent_winner',
    }
    
    for startup in startups:
        name = startup.get('name', '')
        archetype = archetype_map.get(name, 'unknown')
        patterns['archetype_distribution'][archetype] += 1
        
        # Collect risk drivers
        for driver in startup.get('riskDrivers', []):
            label = driver.get('label', '')
            if label:
                patterns['common_risk_drivers'][label] += 1
        
        # Cluster by trajectory
        causality = startup.get('intelligence', {}).get('causalityMarkers', {})
        trajectory = causality.get('trajectory', 'unknown') if causality else 'unknown'
        patterns['trajectory_clusters'][trajectory].append(name)
    
    # Detect repeated patterns
    detected_patterns = []
    
    # Post-hype collapse pattern
    if patterns['archetype_distribution']['post_hype_collapse'] >= 2:
        detected_patterns.append({
            'pattern': 'Post-hype collapse',
            'count': patterns['archetype_distribution']['post_hype_collapse'],
            'description': 'Multiple companies experiencing rapid decline after initial momentum',
            'implication': 'Review Series A diligence process and early-stage risk indicators',
        })
    
    # Silent failure pattern
    if patterns['archetype_distribution']['silent_failure'] >= 2:
        detected_patterns.append({
            'pattern': 'Silent failure',
            'count': patterns['archetype_distribution']['silent_failure'],
            'description': 'Gradual, quiet decay without obvious red flags',
            'implication': 'Strengthen operational monitoring for low-visibility companies',
        })
    
    # Team health pattern
    team_health_mentions = sum(
        count for signal, count in patterns['common_risk_drivers'].items()
        if 'morale' in signal.lower() or 'team' in signal.lower()
    )
    if team_health_mentions >= 5:
        detected_patterns.append({
            'pattern': 'Founder/team disengagement',
            'count': team_health_mentions,
            'description': 'Team health signals appearing across multiple portfolio companies',
            'implication': 'Consider founder mental health check-ins and team dynamics assessment',
        })
    
    # Simultaneous deterioration
    deteriorating = patterns['trajectory_clusters'].get('deteriorating', [])
    if len(deteriorating) >= 3:
        detected_patterns.append({
            'pattern': 'Correlated deterioration',
            'count': len(deteriorating),
            'description': f'Multiple companies deteriorating simultaneously: {", ".join(deteriorating[:3])}',
            'implication': 'Investigate potential macro factors (market shift, funding climate)',
        })
    
    return {
        'archetype_distribution': dict(patterns['archetype_distribution']),
        'common_risk_drivers': dict(sorted(
            patterns['common_risk_drivers'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]),  # Top 5 drivers
        'trajectory_clusters': dict(patterns['trajectory_clusters']),
        'detected_patterns': detected_patterns,
    }


def generate_attention_summary(
    prioritized_startups: List[Dict[str, Any]],
    concentration: Dict[str, Any],
    patterns: Dict[str, Any],
    scenario: str = 'no_intervention'
) -> Dict[str, Any]:
    """Generate actionable portfolio attention summary.
    
    Produces partner-ready update highlighting:
    - 2-3 startups requiring immediate attention
    - Startups that can be deprioritized
    - Rationale for attention allocation
    
    Language matches weekly partner updates and investment committee notes.
    
    Args:
        prioritized_startups: Attention-ranked startups
        concentration: Risk concentration insights
        patterns: Cross-startup patterns
        scenario: Scenario name
        
    Returns:
        Dict with attention summary
    """
    # Top priority startups (immediate attention)
    immediate_attention = prioritized_startups[:3]
    
    # Low priority startups (can deprioritize)
    low_priority = [
        s for s in prioritized_startups
        if s.get('severity', '') == 'low' and 
        s.get('intelligence', {}).get('foresight', {}).get(scenario, {}).get('urgency', '') == 'LOW'
    ]
    
    # Middle priority (monitoring)
    monitoring = [
        s for s in prioritized_startups[3:]
        if s not in low_priority
    ]
    
    # Generate narrative summary
    summary_text = _generate_summary_narrative(
        immediate_attention,
        low_priority,
        concentration,
        patterns,
        scenario
    )
    
    return {
        'scenario': scenario,
        'summary': summary_text,
        'immediate_attention': [
            {
                'name': s['name'],
                'sector': s['sector'],
                'risk_score': s['riskScore'],
                'attention_priority': s['attention_priority'],
                'rationale': s['priority_rationale'],
                'urgency': s.get('intelligence', {}).get('foresight', {}).get(scenario, {}).get('urgency', 'UNKNOWN'),
            }
            for s in immediate_attention
        ],
        'monitoring': [
            {
                'name': s['name'],
                'sector': s['sector'],
                'risk_score': s['riskScore'],
                'status': 'Stable' if s.get('trend', '') == 'stable' else 'Watch',
            }
            for s in monitoring[:5]  # Top 5 monitoring
        ],
        'deprioritize': [
            {
                'name': s['name'],
                'sector': s['sector'],
                'risk_score': s['riskScore'],
                'rationale': 'Low risk, standard monitoring sufficient',
            }
            for s in low_priority[:3]  # Top 3 low priority
        ],
        'key_insights': concentration.get('insights', []),
        'portfolio_patterns': [p['description'] for p in patterns.get('detected_patterns', [])[:2]],
    }


def _generate_summary_narrative(
    immediate_attention: List[Dict[str, Any]],
    low_priority: List[Dict[str, Any]],
    concentration: Dict[str, Any],
    patterns: Dict[str, Any],
    scenario: str
) -> str:
    """Internal: Generate natural language portfolio summary."""
    
    lines = []
    
    # Header
    scenario_label = scenario.replace('_', ' ').title()
    lines.append(f"Portfolio Attention Summary ({scenario_label})")
    lines.append("")
    
    # Immediate attention section
    if immediate_attention:
        lines.append("IMMEDIATE ATTENTION REQUIRED:")
        for startup in immediate_attention:
            foresight = startup.get('intelligence', {}).get('foresight', {}).get(scenario, {})
            urgency = foresight.get('urgency', 'UNKNOWN') if foresight else 'UNKNOWN'
            window = foresight.get('decisionWindow', {}).get('description', '') if foresight else ''
            
            lines.append(
                f"• {startup['name']} ({startup['sector']}) - "
                f"{urgency} urgency, {startup['priority_rationale']}"
            )
            if window:
                lines.append(f"  {window}")
        lines.append("")
    
    # Concentration insights
    if concentration.get('insights'):
        lines.append("PORTFOLIO CONCENTRATIONS:")
        for insight in concentration['insights']:
            lines.append(f"• {insight}")
        lines.append("")
    
    # Pattern detection
    detected_patterns = patterns.get('detected_patterns', [])
    if detected_patterns:
        lines.append("CROSS-PORTFOLIO PATTERNS:")
        for pattern in detected_patterns[:2]:  # Top 2
            lines.append(f"• {pattern['description']}")
            lines.append(f"  Implication: {pattern['implication']}")
        lines.append("")
    
    # Deprioritization guidance
    if low_priority:
        lines.append("STANDARD MONITORING (Can Deprioritize):")
        for startup in low_priority[:3]:
            lines.append(
                f"• {startup['name']} ({startup['sector']}) - "
                f"Low risk ({startup['riskScore']}), stable trajectory"
            )
        lines.append("")
    
    # Closing recommendation
    immediate_count = len(immediate_attention)
    if immediate_count >= 3:
        lines.append(
            f"RECOMMENDATION: Focus partner bandwidth on {immediate_count} high-priority companies. "
            "Consider escalating to full partnership meeting if intervention resources are constrained."
        )
    elif immediate_count > 0:
        lines.append(
            f"RECOMMENDATION: Address {immediate_count} priority "
            f"{'company' if immediate_count == 1 else 'companies'} this week. "
            "Remaining portfolio stable for standard monitoring."
        )
    else:
        lines.append(
            "RECOMMENDATION: No immediate escalations required. "
            "Continue standard monitoring across portfolio."
        )
    
    return "\n".join(lines)


def compute_portfolio_intelligence(
    startups: List[Dict[str, Any]],
    scenario: str = 'no_intervention'
) -> Dict[str, Any]:
    """Orchestrate all portfolio-level intelligence.
    
    Single function to compute:
    - Attention priority ranking
    - Risk concentration
    - Cross-startup patterns
    - Actionable summary
    
    Args:
        startups: List of startup payloads with intelligence
        scenario: Scenario name
        
    Returns:
        Complete portfolio intelligence payload
    """
    # Compute components
    prioritized = compute_attention_priority(startups, scenario)
    concentration = compute_risk_concentration(startups, scenario)
    patterns = detect_cross_startup_patterns(startups)
    summary = generate_attention_summary(prioritized, concentration, patterns, scenario)
    
    return {
        'scenario': scenario,
        'prioritized_startups': prioritized,
        'risk_concentration': concentration,
        'cross_startup_patterns': patterns,
        'attention_summary': summary,
        'portfolio_size': len(startups),
        'timestamp': 'cached_at_startup',  # Indicates deterministic precomputation
    }
