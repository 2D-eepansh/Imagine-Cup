"""
Validation Test Script

Runs basic tests to ensure the risk intelligence system is working correctly.
This is NOT comprehensive unit tests - just smoke tests for demo readiness.
"""

import pandas as pd
import numpy as np
from pathlib import Path


def test_feature_engineering():
    """Test feature engineering module."""
    print("Testing feature_engineering.py...")
    
    try:
        from feature_engineering import engineer_features, get_feature_summary
        
        # Create minimal test data
        test_data = {
            'date': pd.date_range('2026-01-01', periods=10),
            'commit_count': [15, 14, 13, 12, 11, 10, 9, 8, 7, 6],
            'tasks_completed': [8, 7, 7, 6, 6, 5, 5, 4, 3, 3],
            'tasks_missed': [2, 2, 3, 3, 4, 4, 5, 5, 6, 7],
            'avg_response_time_hours': [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5],
            'founder_morale_score': [7.5, 7.0, 6.5, 6.0, 5.5, 5.0, 4.5, 4.0, 3.5, 3.0],
            'compute_spend_usd': [100, 105, 110, 115, 120, 125, 130, 135, 140, 145]
        }
        df = pd.DataFrame(test_data)
        
        # Run feature engineering
        df_features = engineer_features(df)
        
        # Validate output
        assert 'commit_rolling_7d' in df_features.columns, "Missing rolling commit feature"
        assert 'task_miss_rate' in df_features.columns, "Missing task miss rate"
        assert 'execution_health' in df_features.columns, "Missing execution health"
        assert len(df_features) == len(df), "Row count mismatch"
        
        # Get summary
        summary = get_feature_summary(df_features)
        assert 'commit_velocity_7d' in summary, "Missing summary metric"
        
        print("  ✓ Feature engineering works correctly")
        return True
        
    except Exception as e:
        print(f"  ✗ Feature engineering failed: {e}")
        return False


def test_risk_model():
    """Test risk model module."""
    print("Testing risk_model.py...")
    
    try:
        from feature_engineering import engineer_features
        from risk_model import compute_risk_score, get_risk_components, get_risk_trend
        
        # Create test data with clear deterioration
        test_data = {
            'date': pd.date_range('2026-01-01', periods=15),
            'commit_count': list(range(15, 0, -1)),  # Declining
            'tasks_completed': [8, 8, 7, 7, 6, 6, 5, 5, 4, 4, 3, 3, 2, 2, 1],
            'tasks_missed': [1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8],
            'avg_response_time_hours': [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0],
            'founder_morale_score': [8.0, 7.5, 7.0, 6.5, 6.0, 5.5, 5.0, 4.5, 4.0, 3.5, 3.0, 2.5, 2.0, 1.5, 1.0],
            'compute_spend_usd': list(range(100, 250, 10))
        }
        df = pd.DataFrame(test_data)
        
        # Engineer features
        df_features = engineer_features(df)
        
        # Compute risk score
        risk_score, df_with_risk = compute_risk_score(df_features)
        
        # Validate output
        assert 0 <= risk_score <= 100, f"Risk score out of bounds: {risk_score}"
        assert 'daily_risk_score' in df_with_risk.columns, "Missing daily risk scores"
        assert 'anomaly_score' in df_with_risk.columns, "Missing anomaly scores"
        
        # Should be high risk due to deterioration
        assert risk_score > 40, f"Expected high risk for deteriorating data, got {risk_score}"
        
        # Get components
        components = get_risk_components(df_with_risk)
        assert 'execution_risk' in components, "Missing risk component"
        
        # Get trend
        trend = get_risk_trend(df_with_risk)
        assert 'trend_direction' in trend, "Missing trend info"
        
        print(f"  ✓ Risk model works correctly (score: {risk_score:.1f})")
        return True
        
    except Exception as e:
        print(f"  ✗ Risk model failed: {e}")
        return False


def test_portfolio_utils():
    """Test portfolio utilities module."""
    print("Testing portfolio_utils.py...")
    
    try:
        from feature_engineering import engineer_features
        from risk_model import compute_risk_score
        from portfolio_utils import (
            label_risk_severity,
            prepare_ai_reasoning_context,
            generate_intervention_recommendations,
            format_risk_report,
            export_to_dict
        )
        
        # Create test data
        test_data = {
            'date': pd.date_range('2026-01-01', periods=10),
            'commit_count': [10] * 10,
            'tasks_completed': [5] * 10,
            'tasks_missed': [5] * 10,
            'avg_response_time_hours': [5.0] * 10,
            'founder_morale_score': [5.0] * 10,
            'compute_spend_usd': [150.0] * 10
        }
        df = pd.DataFrame(test_data)
        
        # Process data
        df_features = engineer_features(df)
        risk_score, df_with_risk = compute_risk_score(df_features)
        
        # Test severity labeling
        severity = label_risk_severity(risk_score)
        assert severity in ['Low', 'Medium', 'High'], f"Invalid severity: {severity}"
        
        # Test context preparation
        context = prepare_ai_reasoning_context(df_with_risk, risk_score, "Test Startup")
        assert 'risk_score' in context, "Missing risk score in context"
        assert 'operational_metrics' in context, "Missing operational metrics"
        assert 'recommendations' not in context, "Context should not include recommendations yet"
        
        # Test recommendations
        recommendations = generate_intervention_recommendations(risk_score, [])
        assert len(recommendations) > 0, "No recommendations generated"
        
        # Test report formatting
        report = format_risk_report(context)
        assert len(report) > 0, "Empty report"
        assert "PORTFOLIO RISK INTELLIGENCE" in report, "Report missing header"
        
        # Test export
        export = export_to_dict(df_with_risk, risk_score)
        assert 'metadata' in export, "Missing metadata in export"
        assert 'recommendations' in export, "Missing recommendations in export"
        
        print("  ✓ Portfolio utils work correctly")
        return True
        
    except Exception as e:
        print(f"  ✗ Portfolio utils failed: {e}")
        return False


def test_sample_data():
    """Test with actual sample data file."""
    print("Testing with sample_data.csv...")
    
    try:
        from feature_engineering import engineer_features
        from risk_model import compute_risk_score
        from portfolio_utils import export_to_dict
        
        # Check if sample data exists
        sample_path = Path(__file__).parent / 'sample_data.csv'
        if not sample_path.exists():
            print("  ⚠ Sample data file not found, skipping")
            return True
        
        # Load and process
        df = pd.read_csv(sample_path)
        df_features = engineer_features(df)
        risk_score, df_with_risk = compute_risk_score(df_features)
        
        # Should be high risk (deteriorating data)
        assert risk_score > 50, f"Expected high risk for sample data, got {risk_score}"
        
        print(f"  ✓ Sample data analysis works (risk: {risk_score:.1f})")
        return True
        
    except Exception as e:
        print(f"  ✗ Sample data test failed: {e}")
        return False


def run_all_tests():
    """Run all validation tests."""
    print("=" * 70)
    print("PORTFOLIO RISK INTELLIGENCE - VALIDATION TESTS")
    print("=" * 70)
    print()
    
    results = []
    
    results.append(("Feature Engineering", test_feature_engineering()))
    results.append(("Risk Model", test_risk_model()))
    results.append(("Portfolio Utils", test_portfolio_utils()))
    results.append(("Sample Data", test_sample_data()))
    
    print()
    print("=" * 70)
    print("TEST RESULTS")
    print("=" * 70)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name:30s} {status}")
    
    print("=" * 70)
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! System is ready for demo.")
        return 0
    else:
        print("\n❌ Some tests failed. Please check errors above.")
        return 1


if __name__ == "__main__":
    import sys
    exit_code = run_all_tests()
    sys.exit(exit_code)
