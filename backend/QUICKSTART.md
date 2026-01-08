# Quick Start Guide

## Installation

```bash
cd backend
pip install -r requirements.txt
```

## Run Demo with Sample Data

```bash
python demo.py sample_data.csv "Demo Startup Inc"
```

This will analyze the included sample dataset and display:
- Risk score (0-100)
- Risk severity classification
- Component breakdown
- Top contributing signals
- Intervention recommendations
- Full risk report

## Expected Output

You should see a risk score of **~70-80** (High Risk) because the sample data shows:
- Declining commit velocity (15 → 4 commits/day)
- Increasing task miss rate (20% → 80%)
- Deteriorating founder morale (7.5 → 3.0)
- Escalating compute spend ($125 → $190)
- Multiple anomalies detected

This pattern simulates a startup in distress requiring immediate VC intervention.

## Understanding the Output

### Risk Score Scale
- **0-30:** Low risk - healthy operations
- **31-60:** Medium risk - monitor closely
- **61-100:** High risk - intervention required

### Risk Components
- **Execution Risk:** Development velocity and task completion
- **Team Health Risk:** Morale trends and responsiveness
- **Anomaly Risk:** Statistical deviations from normal patterns
- **Spend Risk:** Burn rate volatility

### Recommendations
The system generates actionable next steps based on:
- Overall risk severity
- Top contributing signals
- Historical trend direction

## Custom Data Analysis

### Prepare Your CSV

Ensure your CSV has these columns:
- `date` (YYYY-MM-DD format)
- `commit_count` (integer)
- `tasks_completed` (integer)
- `tasks_missed` (integer)
- `avg_response_time_hours` (float)
- `founder_morale_score` (float, 0-10 scale)
- `compute_spend_usd` (float)

### Run Analysis

```bash
python demo.py path/to/your/data.csv "Your Startup Name"
```

## Programmatic Usage

```python
import pandas as pd
from feature_engineering import engineer_features
from risk_model import compute_risk_score
from portfolio_utils import prepare_ai_reasoning_context, export_to_dict

# Load and analyze
df = pd.read_csv('your_data.csv')
df_features = engineer_features(df)
risk_score, df_with_risk = compute_risk_score(df_features)

# Get structured output
analysis = export_to_dict(df_with_risk, risk_score)

# Access key metrics
print(f"Risk Score: {analysis['risk_score']}")
print(f"Severity: {analysis['risk_severity']}")
print(f"Top Signals: {analysis['top_risk_signals']}")
print(f"Recommendations: {analysis['recommendations']}")
```

## Integration with Azure OpenAI

```python
from portfolio_utils import prepare_ai_reasoning_context
import openai  # Azure OpenAI SDK

# Prepare context
context = prepare_ai_reasoning_context(df_with_risk, risk_score, "Startup Name")

# Generate reasoning with GPT-4
prompt = f"""
You are a senior venture capital analyst. Based on the following risk intelligence data,
write a concise investment memo explaining the risk assessment and recommended actions.

Risk Data:
{context}

Format: Executive Summary, Risk Analysis, Recommendations
"""

# Call Azure OpenAI (requires Azure OpenAI setup)
# response = openai.ChatCompletion.create(...)
# print(response.choices[0].message.content)
```

## Troubleshooting

### "Missing required columns" error
- Check CSV column names match exactly (case-sensitive)
- Ensure no extra spaces in column headers

### "Not enough data" warning
- Minimum 7 days recommended for meaningful trends
- Optimal: 30-45 days of data

### Low/unexpected risk scores
- Verify data quality (no missing values)
- Check that morale score is on 0-10 scale
- Ensure date column is parseable

## Next Steps

1. **Test with your portfolio data**
2. **Calibrate thresholds** if needed (see risk_model.py weights)
3. **Integrate with Azure OpenAI** for natural language reports
4. **Deploy as Azure Function** for API access

## Support

For issues or questions:
- Review module docstrings for detailed API documentation
- Check README.md for system architecture
- Examine demo.py for pipeline flow
