# Portfolio Risk Intelligence System

> **Enterprise AI for Venture Capital Risk Management**  
> Early warning detection to protect capital and time intervention timing

---

## 🎯 What This Is

A **production-grade risk intelligence system** that analyzes startup operational data to detect failure signals before capital is lost.

**Not a chatbot.** Not generic analytics. **Predictive risk scoring with explainable AI.**

Built for: Microsoft Imagine Cup 2026 - Enterprise AI Category

---

## 🚀 Quick Start

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Run validation tests
python test_system.py

# Analyze sample data
python demo.py sample_data.csv "Demo Startup"
```

**Expected output:** Risk score ~75/100 (High) with detailed breakdown and recommendations.

---

## 📊 System Capabilities

### Core Intelligence
- ✅ **Time-series feature engineering** - Rolling averages, trends, momentum signals
- ✅ **Anomaly detection** - Isolation Forest for multivariate pattern detection
- ✅ **Risk scoring** - Single 0-100 score with explainable components
- ✅ **Severity classification** - Low/Medium/High risk labeling
- ✅ **Decision foresight** - Urgency classification, time windows, reversibility markers
- ✅ **Portfolio attention** - Priority ranking, sector concentration, cross-startup patterns
- ✅ **Intervention recommendations** - Actionable next steps for VCs

### Input Data
Analyzes 7 operational metrics over 30-45 days:
- Development velocity (commits)
- Execution quality (task completion)
- Team health (morale, responsiveness)
- Burn rate dynamics (compute spend)

### Output
- **Risk score:** 0-100 (higher = more risk)
- **Severity:** Low / Medium / High
- **Components:** Execution, team health, anomaly, spend
- **Trends:** Stable / Improving / Declining
- **Recommendations:** Specific intervention actions
- **AI context:** Structured data ready for Azure OpenAI reasoning

---

## 📁 Project Structure

```
backend/
├── feature_engineering.py    # Time-series signal extraction
├── risk_model.py              # Anomaly detection + risk scoring
├── portfolio_utils.py         # Investor-grade formatting
├── demo.py                    # End-to-end pipeline demo
├── test_system.py             # Validation tests
├── sample_data.csv            # Example dataset (39 days)
├── requirements.txt           # Python dependencies
├── README.md                  # System documentation
├── QUICKSTART.md              # Usage guide
└── ARCHITECTURE.md            # Technical design details
```

---

## 🔬 Technical Approach

### 1. Feature Engineering
Transforms raw data into predictive signals:
- Rolling 7-day windows for noise reduction
- Miss rate calculation for execution discipline
- Morale trend detection (linear regression)
- Response time normalization (z-scores)
- Spend volatility tracking

### 2. Anomaly Detection
Uses Isolation Forest (sklearn) to detect:
- Multivariate operational abnormalities
- Statistical deviations from normal patterns
- Calibrated for startup volatility (10% contamination)

### 3. Risk Scoring
Weighted combination of signals:
- **Execution:** 35% (development + task quality)
- **Team Health:** 25% (morale + responsiveness)
- **Anomaly:** 25% (statistical deviation)
- **Spend:** 15% (burn rate stability)

Recent days weighted more heavily (exponential decay).

### 4. Explainability
Every risk score component is:
- Traceable to source data
- Human-interpretable
- Backed by domain logic
- No black-box ML

---

## 📈 Example Analysis

**Input:** 39 days of declining operational metrics  
**Output:**
```
Risk Score: 75.3 / 100
Severity: HIGH RISK
Trend: Increasing ↗

Top Signals:
  1. Team Health: 72.5 (High) - Morale declining from 7.5 → 3.0
  2. Anomaly: 65.0 (High) - Statistical deviation detected
  3. Execution: 48.0 (Medium) - Commit velocity down 73%

Recommendations:
  • Schedule immediate founder check-in call
  • Review burn rate and runway calculations
  • Assess need for emergency bridge funding
```

---

## 🔷 Azure Integration Roadmap

### Phase 1: ✅ Core Intelligence (Current)
- Feature engineering
- Risk scoring
- Anomaly detection
- Portfolio utilities

### Phase 2: ✅ Full-Stack Architecture
- Frontend/backend separation
- FastAPI REST endpoints
- React dashboard with data binding
- CORS-secured local demo

### Phase 3: ✅ Azure OpenAI Reasoning
- GPT-4 integration for investor-grade explanations
- Deterministic caching (hash-based)
- Why it matters / What happens next / Recommended action

### Phase 4: ✅ Portfolio Expansion
- 15 startups with realistic archetypes
- Post-hype collapse, silent failure, zombie, etc.
- 45-60 days operational history per startup

### Phase 5: ✅ Time & Scenario Intelligence
- Historical snapshots (60→0 days back)
- Causality markers (when risk first detected)
- Intervention scenarios (no/early/delayed)

### Phase 6: ✅ Decision Foresight
- Urgency classification (LOW/MEDIUM/HIGH/CRITICAL)
- Decision windows (bounded time estimates)
- Confidence framing (qualitative assessment)
- Reversibility markers (intervention viability)

### Phase 7: ✅ Portfolio Attention
- Attention priority ranking (not just risk scores)
- Risk concentration by sector/urgency
- Cross-startup pattern detection
- Actionable attention summaries for partners

### Future: Real-time Monitoring
- Azure Event Grid for data ingestion
- Automated risk assessment on data updates
- Email alerts for threshold breaches

### Phase 3: Azure Functions API
```
POST /api/analyze
{
  "startup_id": "acme-ai",
  "data": [...]
}

Response:
{
  "risk_score": 67.3,
  "severity": "High",
  "report": "...",
  "recommendations": [...]
}
```

### Phase 4: Real-time Monitoring
- Azure Event Grid for data ingestion
- Automated risk assessment on data updates
- Email alerts for threshold breaches
- Dashboard integration

---

## 🎯 Design Principles

### Explainable
- No black-box models
- Feature importance visible
- Domain-driven weighting

### Predictive
- Leading indicators, not lagging metrics
- Time-series momentum tracking
- Anomaly detection for unknowns

### Enterprise-Credible
- Investor-grade language
- Risk-to-action mapping
- Production-ready code

### Minimal (MVP)
- Core intelligence only
- No unnecessary features
- Fast execution (<1 second)

---

## 📚 Documentation

- **[README.md](backend/README.md)** - Comprehensive system overview
- **[QUICKSTART.md](backend/QUICKSTART.md)** - Usage guide and examples
- **[ARCHITECTURE.md](backend/ARCHITECTURE.md)** - Technical design details

All modules have extensive docstrings with:
- Function purpose and context
- Parameter descriptions
- Return value specifications
- Design rationale explanations

---

## 🧪 Validation

```bash
python backend/test_system.py
```

Runs smoke tests for:
- Feature engineering correctness
- Risk model output validity
- Portfolio utilities functionality
- Sample data processing

**All tests must pass before demo.**

---

## 📦 Dependencies

```
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
```

Python 3.8+ required. No GPU needed.

---

## 💡 Key Innovations

1. **Hybrid ML + Domain Logic**
   - Isolation Forest for pattern detection
   - VC-calibrated weights and thresholds
   - Best of both worlds

2. **Temporal Intelligence**
   - Exponential weighting of recent data
   - Trend adjustment for risk trajectories
   - Momentum tracking across signals

3. **LLM-Ready Context**
   - Pre-structured for GPT-4 reasoning
   - Eliminates prompt engineering complexity
   - Consistent, reproducible outputs

4. **Intervention-Focused**
   - Not just risk scores
   - Actionable recommendations
   - Urgency classification

---

## 🎓 Use Cases

### Portfolio Management
- Monitor 10-50 startups continuously
- Identify at-risk companies early
- Prioritize partner attention

### Due Diligence
- Analyze operational health pre-investment
- Detect red flags in founder behavior
- Assess execution capability

### Board Support
- Prepare data-driven board materials
- Track improvement/deterioration post-investment
- Justify intervention decisions

---

## 🛡️ Data Privacy

- **CSV-based:** No API keys required for core functionality
- **Local execution:** No data transmission in Phase 1
- **Azure-ready:** Designed for secure cloud deployment

---

## 🏆 Competition Positioning

**Microsoft Imagine Cup 2026**  
**Category:** Enterprise AI Solutions  
**Focus:** Venture Capital Portfolio Risk Management

### Differentiation
- **Not generic:** Purpose-built for VC use case
- **Not conversational:** Predictive intelligence, not chatbot
- **Not exploratory:** Production-grade, demo-ready system
- **Azure-native roadmap:** Clear path to full Azure stack integration

### Impact Potential
- **Capital protection:** Early warning saves millions
- **Portfolio scalability:** Monitor 10x more companies
- **Decision confidence:** Data-driven intervention timing
- **Founder support:** Identify help needed before crisis

---

## 👥 Team

Built by a senior AI engineer with deep expertise in:
- Enterprise ML systems
- Time-series analysis
- Risk modeling
- Azure cloud architecture

---

## 📧 Next Steps

1. ✅ **Test locally** - Run validation and demo
2. **Calibrate** - Adjust thresholds for your portfolio
3. **Integrate Azure OpenAI** - Generate natural language reports
4. **Deploy Azure Functions** - Build API layer
5. **Scale** - Real-time monitoring for full portfolio

---

## 📄 License

Proprietary - Built for Microsoft Imagine Cup 2026

---

**This is not a prototype. This is production intelligence infrastructure ready for enterprise deployment.**

🔗 **Demo:** `python backend/demo.py backend/sample_data.csv`  
📊 **Validate:** `python backend/test_system.py`  
📚 **Learn:** Read `backend/ARCHITECTURE.md`
