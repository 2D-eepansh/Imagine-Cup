"""
Demo Example: Portfolio Risk Intelligence System

This script demonstrates the complete risk analysis pipeline:
1. Load startup operational data
2. Engineer predictive features
3. Compute risk score with anomaly detection
4. Generate investor-grade insights

Usage:
    python demo.py <path_to_csv>

Example:
    python demo.py data/startup_metrics.csv
"""

import sys
import pandas as pd
from pathlib import Path

# Import core modules
from feature_engineering import engineer_features, get_feature_summary
from risk_model import compute_risk_score, get_risk_components, get_risk_trend, identify_critical_signals
from portfolio_utils import (
    prepare_ai_reasoning_context,
    format_risk_report,
    export_to_dict,
    generate_intervention_recommendations
)


def analyze_startup_risk(csv_path: str, startup_name: str = "Portfolio Company") -> dict:
    """
    Complete risk analysis pipeline for a single startup.
    
    Args:
        csv_path: Path to CSV file with operational data
        startup_name: Name of the startup being analyzed
    
    Returns:
        Complete analysis dictionary ready for Azure OpenAI reasoning
    """
    
    print("=" * 70)
    print("PORTFOLIO RISK INTELLIGENCE SYSTEM")
    print("Early Warning Detection for Venture Capital")
    print("=" * 70)
    print()
    
    # ============================================================
    # STEP 1: LOAD DATA
    # ============================================================
    
    print(f"📊 Loading operational data from: {csv_path}")
    try:
        df = pd.read_csv(csv_path)
        print(f"   ✓ Loaded {len(df)} days of operational data")
    except Exception as e:
        print(f"   ✗ Error loading data: {e}")
        return {}
    
    # Validate required columns
    required_columns = [
        'date', 'commit_count', 'tasks_completed', 'tasks_missed',
        'avg_response_time_hours', 'founder_morale_score', 'compute_spend_usd'
    ]
    
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        print(f"   ✗ Missing required columns: {missing}")
        return {}
    
    print()
    
    # ============================================================
    # STEP 2: FEATURE ENGINEERING
    # ============================================================
    
    print("🔧 Engineering predictive features...")
    try:
        df_features = engineer_features(df)
        feature_summary = get_feature_summary(df_features)
        print(f"   ✓ Created {len(df_features.columns)} feature columns")
        print(f"   ✓ Latest commit velocity (7d): {feature_summary.get('commit_velocity_7d', 0)}")
        print(f"   ✓ Latest execution health: {feature_summary.get('execution_health', 0)}")
    except Exception as e:
        print(f"   ✗ Error in feature engineering: {e}")
        return {}
    
    print()
    
    # ============================================================
    # STEP 3: RISK SCORING
    # ============================================================
    
    print("🎯 Computing risk score with anomaly detection...")
    try:
        risk_score, df_with_risk = compute_risk_score(df_features)
        print(f"   ✓ Risk Score: {risk_score:.1f} / 100")
        
        # Get risk components
        components = get_risk_components(df_with_risk)
        print(f"   ✓ Execution Risk: {components.get('execution_risk', 0)}")
        print(f"   ✓ Team Health Risk: {components.get('team_health_risk', 0)}")
        print(f"   ✓ Anomaly Detected: {components.get('is_anomaly_detected', False)}")
        
    except Exception as e:
        print(f"   ✗ Error in risk computation: {e}")
        return {}
    
    print()
    
    # ============================================================
    # STEP 4: TREND ANALYSIS
    # ============================================================
    
    print("📈 Analyzing risk trends...")
    try:
        trend_info = get_risk_trend(df_with_risk, window=7)
        print(f"   ✓ Trend Direction: {trend_info.get('trend_direction', 'N/A')}")
        print(f"   ✓ Risk Volatility: {trend_info.get('volatility', 0)}")
    except Exception as e:
        print(f"   ⚠ Could not analyze trends: {e}")
    
    print()
    
    # ============================================================
    # STEP 5: CRITICAL SIGNALS
    # ============================================================
    
    print("🚨 Identifying critical signals...")
    try:
        critical = identify_critical_signals(df_with_risk, threshold=0.6)
        if critical:
            print(f"   ⚠ Critical signals detected: {', '.join(critical)}")
        else:
            print(f"   ✓ No critical signals detected")
    except Exception as e:
        print(f"   ⚠ Could not identify critical signals: {e}")
    
    print()
    
    # ============================================================
    # STEP 6: PREPARE AI REASONING CONTEXT
    # ============================================================
    
    print("🤖 Preparing context for Azure OpenAI reasoning...")
    try:
        analysis_context = prepare_ai_reasoning_context(
            df_with_risk,
            risk_score,
            startup_name=startup_name
        )
        print(f"   ✓ Context prepared with {len(analysis_context)} top-level keys")
    except Exception as e:
        print(f"   ✗ Error preparing context: {e}")
        return {}
    
    print()
    
    # ============================================================
    # STEP 7: GENERATE RECOMMENDATIONS
    # ============================================================
    
    print("💡 Generating intervention recommendations...")
    try:
        recommendations = generate_intervention_recommendations(
            risk_score,
            analysis_context.get('top_risk_signals', [])
        )
        print(f"   ✓ Generated {len(recommendations)} recommendations:")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"      {i}. {rec}")
    except Exception as e:
        print(f"   ⚠ Could not generate recommendations: {e}")
    
    print()
    
    # ============================================================
    # STEP 8: DISPLAY REPORT
    # ============================================================
    
    print()
    report = format_risk_report(analysis_context)
    print(report)
    print()
    
    # ============================================================
    # STEP 9: EXPORT COMPLETE ANALYSIS
    # ============================================================
    
    print("💾 Exporting complete analysis...")
    try:
        complete_export = export_to_dict(df_with_risk, risk_score)
        print(f"   ✓ Analysis exported (ready for API/Azure Function)")
        print(f"   ✓ Total data points analyzed: {complete_export['metadata']['data_points_analyzed']}")
    except Exception as e:
        print(f"   ⚠ Could not export: {e}")
        complete_export = analysis_context
    
    print()
    print("=" * 70)
    print("✓ ANALYSIS COMPLETE")
    print("=" * 70)
    
    return complete_export


def main():
    """
    Main entry point for demo script.
    """
    if len(sys.argv) < 2:
        print("Usage: python demo.py <path_to_csv> [startup_name]")
        print()
        print("Example:")
        print("  python demo.py data/startup_metrics.csv \"Acme AI Corp\"")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    startup_name = sys.argv[2] if len(sys.argv) > 2 else "Portfolio Company"
    
    # Validate file exists
    if not Path(csv_path).exists():
        print(f"Error: File not found: {csv_path}")
        sys.exit(1)
    
    # Run analysis
    result = analyze_startup_risk(csv_path, startup_name)
    
    if not result:
        print("\n❌ Analysis failed. Check error messages above.")
        sys.exit(1)
    
    print("\n✅ Analysis data is now ready to be sent to Azure OpenAI for reasoning generation.")
    print("   The 'result' dictionary contains all structured metrics needed for GPT-4.")


if __name__ == "__main__":
    main()
