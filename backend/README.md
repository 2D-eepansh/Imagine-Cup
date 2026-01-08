# Portfolio Risk Intelligence System

**Early Warning Detection for Venture Capital Firms**

This system detects failure signals in startups by analyzing time-series operational data, producing risk scores, and generating investor-grade insights using Azure AI services.

---

## 🎯 System Overview

**Purpose:** Protect capital by identifying struggling portfolio companies before they fail.

**Approach:**
- Analyze operational metrics (commits, tasks, morale, spend)
- Detect anomalies using Isolation Forest
- Produce 0-100 risk scores with explainable components
- Generate intervention recommendations

**Not a chatbot.** Not generic analytics. This is predictive risk intelligence.

---

## 📁 Module Structure

```
backend/
├── feature_engineering.py   # Time-series signal extraction
├── risk_model.py             # Anomaly detection + risk scoring
├── portfolio_utils.py        # Investor-grade formatting
└── demo.py                   # Complete pipeline demonstration
```

### API (FastAPI)
- `GET /api/startups` → list of startups `{ id, name, sector, riskScore, severity, trend, trendDelta, riskHistory, riskDrivers, aiInsight, requiresPartnerAttention }`
- `GET /api/startups/{id}` → full risk object for one startup (same shape as above)

Example response (truncated):

```json
[
   {
      "id": "1",
      "name": "Lumina Health",
      "sector": "Healthcare",
      "riskScore": 78.4,
      "severity": "high",
      "trend": "up",
      "trendDelta": 12.1,
      "riskHistory": [45.2, 52.1, 58.3, 61.0, 68.4, 72.7, 78.4],
      "riskDrivers": [
         { "label": "Execution Velocity", "detail": "Development momentum and task completion rate" }
      ],
      "aiInsight": {
         "whyItMatters": "Execution Velocity is the dominant risk driver for Lumina Health this week.",
         "whatHappensNext": "If unaddressed, the current trajectory is likely to persist over the next 2-3 weeks.",
         "recommendedAction": "Schedule immediate founder check-in call"
      },
      "requiresPartnerAttention": true
   }
]
```

### **feature_engineering.py**
Transforms raw operational data into predictive signals:
- Rolling 7-day commit velocity
- Task miss rate and execution quality
- Morale trends and team health indicators
- Spend dynamics and burn rate signals
- Composite execution health score

### **risk_model.py**
Core intelligence layer using Azure ML concepts:
- Isolation Forest for multivariate anomaly detection
- Weighted signal combination (execution > morale > spend)
- Single risk score (0-100) for latest day
- Explainable risk component breakdown
- Trend analysis and critical signal identification

### **portfolio_utils.py**
Bridges technical signals with business decisions:
- Risk severity labeling (Low/Medium/High)
- Top contributing signal extraction
- AI reasoning context preparation (for Azure OpenAI)
- Intervention recommendation generation
- Investor-grade report formatting

---

## 📊 Input Data Format

CSV file with the following columns:

| Column | Description | Type |
|--------|-------------|------|
| `date` | Observation date | datetime |
| `commit_count` | Daily Git commits | int |
| `tasks_completed` | Tasks finished | int |
| `tasks_missed` | Tasks missed | int |
| `avg_response_time_hours` | Team response time | float |
| `founder_morale_score` | Morale (0-10 scale) | float |
| `compute_spend_usd` | Daily compute spend | float |

**Expected:** 30-45 days of data per startup.

---

## 🚀 Usage

### Basic Analysis

```python
from feature_engineering import engineer_features
from risk_model import compute_risk_score
from portfolio_utils import prepare_ai_reasoning_context
import pandas as pd

# Load data
df = pd.read_csv('startup_metrics.csv')

# Engineer features
df_features = engineer_features(df)

# Compute risk
risk_score, df_with_risk = compute_risk_score(df_features)

# Prepare context for AI reasoning
context = prepare_ai_reasoning_context(
    df_with_risk, 
    risk_score, 
    startup_name="Acme AI Corp"
)

print(f"Risk Score: {risk_score}/100")
print(f"Severity: {context['risk_severity']}")
```

### Run Complete Demo

```bash
python backend/demo.py data/startup_metrics.csv "Acme AI Corp"
```

The demo script runs the full pipeline and displays:
- Feature engineering summary
- Risk score with component breakdown
- Trend analysis
- Critical signal identification
- Intervention recommendations
- Formatted risk report

---

## 🧠 Risk Score Interpretation

| Score | Severity | Meaning | Action |
|-------|----------|---------|--------|
| 0-30 | **Low** | Healthy execution, normal operations | Passive monitoring |
| 31-60 | **Medium** | Warning signals present | Active monitoring, prepare contingencies |
| 61-100 | **High** | Intervention required, capital at risk | Immediate founder check-in |

---

## 🔬 Technical Design

### Anomaly Detection
- **Algorithm:** Isolation Forest (sklearn)
- **Contamination:** 10% (calibrated for startup volatility)
- **Features:** Commit velocity, task miss rate, morale trend, response delays, spend changes

### Risk Weighting
- **Execution:** 35% (velocity + task quality)
- **Team Health:** 25% (morale + responsiveness)
- **Anomaly:** 25% (statistical deviation)
- **Spend:** 15% (burn rate volatility)

### Temporal Bias
Recent days weighted more heavily using exponential decay. Risk trend adjustments applied if risk is increasing.

---

## 📦 Dependencies

```bash
pip install pandas numpy scikit-learn
```

**Python:** 3.8+

**Azure Integration (Phase 2):**
- Azure OpenAI for reasoning generation
- Azure ML for model deployment
- Azure Functions for API endpoints

---

## 🎓 Design Philosophy

**Explainable**
- Every risk component traceable to source data
- No black-box deep learning
- Transparent weighting and logic

**Predictive**
- Leading indicators, not lagging metrics
- Detects "gradually failing" phase
- Time-series momentum tracking

**Enterprise-Credible**
- Investor-grade language and formatting
- Risk thresholds calibrated for VC decision-making
- Production-ready code structure

**Minimal**
- MVP scope: core intelligence only
- No UI, no chat, no unnecessary features
- Pure logic, ready for integration

---

## 🔄 Next Steps (Phase 2)

1. **Azure OpenAI Integration**
   - Feed `prepare_ai_reasoning_context()` output to GPT-4
   - Generate natural language risk reports
   - Explain "why" behind risk scores

2. **API Layer**
   - Azure Functions for REST endpoints
   - Batch analysis for portfolio-wide insights
   - Real-time monitoring webhooks

3. **Azure ML Deployment**
   - Deploy Isolation Forest as managed endpoint
   - Model versioning and A/B testing
   - Automated retraining pipeline

---

## 📝 Example Output

```
PORTFOLIO RISK INTELLIGENCE REPORT
======================================================================
Company: Acme AI Corp
Analysis Date: 2026-01-08
Risk Score: 67.3 / 100
Risk Severity: High

OPERATIONAL HEALTH:
----------------------------------------------------------------------
  Commit Velocity (7d):     12.4
  Task Completion Rate:     68.0%
  Founder Morale:           4.2 / 10
  Execution Health:         52.0 / 100

RISK COMPONENT BREAKDOWN:
----------------------------------------------------------------------
  Execution Risk:           48.0
  Team Health Risk:         72.5
  Anomaly Risk:             65.0
  Spend Risk:               41.2

TOP CONTRIBUTING SIGNALS:
----------------------------------------------------------------------
  1. Team Health: 72.5 (High)
     Founder morale and team responsiveness
  2. Anomaly: 65.0 (High)
     Statistical deviation from normal patterns
  3. Execution Velocity: 48.0 (Medium)
     Development momentum and task completion rate
======================================================================
```

---

## 🛡️ Data Privacy

- CSV input only (no API keys required for core modules)
- No data transmission in Phase 1
- Designed for on-premise or Azure secure deployment

---

## 📧 System Context

Built for: **Microsoft Imagine Cup 2026**  
Category: **Enterprise AI Solutions**  
Focus: **Venture Capital Portfolio Risk Management**

---

**This is not a prototype.** This is production-grade intelligence infrastructure ready for enterprise deployment.
