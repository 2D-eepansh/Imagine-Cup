# VC Portfolio Intelligence System

> **Submission-Ready Enterprise AI for Venture Capital Portfolio Risk Management**  
> Detects early failure signals, provides decision-grade foresight, and allocates attention across portfolios

[![Status](https://img.shields.io/badge/Status-Submission--Ready-brightgreen)]()
[![Determinism](https://img.shields.io/badge/Determinism-Verified-blue)]()
[![Tests](https://img.shields.io/badge/Tests-6%2F6%20Passing-success)]()

Built for: **Microsoft Imagine Cup 2026** - Enterprise AI Category

---

## 🎯 What This Solves

**Problem**: VCs manage 15-30 startups but can only deeply engage with 3-5 at a time. By the time a failure is obvious, it's often too late.

**Solution**: An intelligence system that:
1. **Detects** early operational failure signals before capital is lost
2. **Explains** why each startup is at risk using investor language
3. **Forecasts** what happens if you act now vs. wait
4. **Prioritizes** which startups need immediate attention
5. **Remembers** historical patterns to provide institutional context

**Not a chatbot. Not generic dashboards. Decision-grade portfolio intelligence.**

---

## 🚀 Quick Demo (3 Minutes)

### 1. Start Server
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Expected Output**:
```
======================================================================
RUNNING SUBMISSION-GRADE HARDENING CHECKS
======================================================================
✓ Determinism verified: seeded RNG produces identical outputs
✓ Determinism verified: all intelligence precomputed at startup
✓ All hardening checks passed
✓ System is submission-grade and judge-proof
======================================================================
```

### 2. Run Validation Tests
```bash
python test_submission_ready.py
```

**Expected**: `✓ ALL TESTS PASSED (6/6)`

### 3. Test Endpoints
```bash
# List portfolio (15 startups)
curl http://localhost:8000/api/startups

# Deep dive on high-risk startup
curl http://localhost:8000/api/startups/1?include_intelligence=true

# Get portfolio attention priorities
curl http://localhost:8000/api/portfolio/attention
```

---

## 📊 System Architecture

### 8 Intelligence Layers (Phase 1-7 Complete)

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 1: Core Risk Scoring                                │
│  → Isolation Forest anomaly detection (seeded)             │
│  → Weighted risk aggregation (0-100 scale)                 │
│  → Severity classification (LOW/MEDIUM/HIGH)               │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│  Phase 2: Reasoning Layer                                  │
│  → Azure OpenAI with deterministic fallback                │
│  → "Why it matters" + "What happens next" + "Action"       │
│  → Investment committee language                           │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│  Phase 3: Time-Aware Intelligence                          │
│  → Historical snapshots (60d → 0d)                         │
│  → Causality markers (first risk, lead time)               │
│  → Intervention scenarios (no/early/delayed)               │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│  Phase 4: Decision Foresight                               │
│  → Urgency classification (act now vs. monitor)            │
│  → Action windows (days until critical)                    │
│  → Reversibility markers (can we fix this?)                │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│  Phase 5: Portfolio Attention                              │
│  → Priority ranking (not just risk scores)                 │
│  → Risk concentration by sector                            │
│  → Cross-startup pattern detection                         │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│  Phase 6: Investor Memory                                  │
│  → 6 canonical patterns (post-hype collapse, zombie, etc.) │
│  → Historical outcome associations                         │
│  → "Have we seen this before?" institutional context       │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│  Phase 7: Submission Hardening ⭐ NEW                      │
│  → Determinism verification (fixed seeds, stable cache)    │
│  → Graceful failure handling (never expose errors)         │
│  → Request validation (safe defaults)                      │
│  → Demo resilience (rapid refreshes, concurrent users)     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔥 Key Features

### 1. Time-Aware Intelligence (Phase 3)
**See how risk evolved over time**
```json
{
  "timeSnapshots": [
    {"days_ago": 60, "risk_score": 45.2, "severity": "medium"},
    {"days_ago": 30, "risk_score": 58.7, "severity": "medium"},
    {"days_ago": 0, "risk_score": 72.4, "severity": "high"}
  ]
}
```

**Why it matters**: Traditional dashboards show current risk. We show **when it started** and **how fast it's accelerating**.

---

### 2. Decision Foresight (Phase 4)
**Know when to act and what's possible**
```json
{
  "foresight": {
    "urgency": "HIGH",
    "action_window_days": "7-14",
    "confidence": "HIGH",
    "reversibility_marker": "VIABLE",
    "intervention_note": "Early operational support recommended"
  }
}
```

**Why it matters**: VCs don't just need "what's wrong", they need **"when to act"** and **"can we fix this?"**.

---

### 3. Portfolio Attention (Phase 5)
**Prioritize which startups need attention NOW**
```json
{
  "attention_summary": {
    "immediate_attention_required": [
      {"name": "Lumina Health", "attention_priority": 0.94},
      {"name": "Quantum Logistics", "attention_priority": 0.89}
    ],
    "monitor_closely": [...],
    "standard_monitoring": [...]
  }
}
```

**Why it matters**: Partners can't deeply engage with 30 startups. We **rank by urgency**, not just risk.

---

### 4. Investor Memory (Phase 6)
**Institutional pattern recognition**
```json
{
  "investor_memory": {
    "canonical_pattern": "post_hype_collapse",
    "pattern_label": "Post-Hype Collapse",
    "memory_signal": "This trajectory resembles prior post-hype collapse cases. Historically, early intervention has improved outcomes.",
    "typical_outcome": "Often leads to shutdown within 6-12 months absent major pivot"
  }
}
```

**Why it matters**: System "remembers" similar patterns from past portfolio companies. Speaks in **institutional language** VCs already use.

---

### 5. Submission Hardening (Phase 7) ⭐
**Judge-proof and demo-resilient**

✅ **Determinism Verified**: Fixed random seeds, precomputed intelligence, stable cache keys  
✅ **Graceful Failures**: Azure OpenAI fallback, safe defaults, no stack traces  
✅ **Request Validation**: Invalid params default gracefully  
✅ **Demo Resilience**: Rapid refreshes (<5s for 20 calls), concurrent users (30 simultaneous)  
✅ **Audit Trail**: Internal logging for traceability  

**Run Checks**:
```bash
cd backend
python -c "from hardening import run_hardening_checks; run_hardening_checks()"
```

---

## 📁 Project Structure

```
backend/
├── hardening.py                 ⭐ Submission-grade safety
├── risk_model.py                Core risk scoring
├── feature_engineering.py       Time-series features
├── portfolio_utils.py           Utilities
├── reasoning/
│   ├── orchestrator.py          Caching layer
│   ├── client.py                Azure OpenAI wrapper
│   └── prompts.py               System prompts
├── intelligence/
│   ├── time_snapshots.py        Historical risk
│   ├── scenarios.py             Intervention modeling
│   ├── foresight.py             Decision signals
│   ├── portfolio_attention.py   Portfolio intelligence
│   └── investor_memory.py       Canonical patterns
├── api/
│   └── routes.py                Hardened API endpoints
├── test_submission_ready.py     ⭐ Validation suite
├── main.py                      FastAPI entry point
└── requirements.txt             Dependencies

docs/
├── FINAL_SUMMARY.md             Complete system overview
├── PHASE_9_HARDENING.md         Hardening implementation
├── SUBMISSION_CHECKLIST.md      Pre-demo validation
├── JUDGE_QA_GUIDE.md            Q&A preparation
└── QUICK_TEST_COMMANDS.md       Testing commands
```

---

## 🔧 API Endpoints

### 1. List Portfolio
```bash
GET /api/startups
```

Returns 15 startups with base risk data.

---

### 2. Get Startup Intelligence
```bash
GET /api/startups/{id}?include_intelligence=true
```

**Response Fields**:
- `riskScore`: 0-100 risk score
- `severity`: low/medium/high
- `riskDrivers`: Top 3 contributing signals
- `aiInsight`: Why it matters, what happens next, recommended action
- `intelligence.timeSnapshots`: Historical risk evolution
- `intelligence.interventionScenarios`: No/early/delayed intervention outcomes
- `intelligence.foresight`: Urgency, action windows, reversibility
- `intelligence.investor_memory`: Canonical pattern, historical context

---

### 3. Get Portfolio Attention
```bash
GET /api/portfolio/attention?scenario={no_intervention|early_intervention|delayed_intervention}
```

**Response Fields**:
- `prioritized_startups`: Ranked by attention priority (not just risk)
- `risk_concentration`: High/medium/low counts by sector
- `cross_startup_patterns`: Archetype distribution, common risk drivers
- `attention_summary`: Immediate/monitor/standard lists
- `portfolio_memory`: Pattern prevalence, historical insights

---

## ✅ Validation & Testing

### Automated Test Suite
```bash
cd backend
python test_submission_ready.py
```

**Tests**:
1. ✅ Startup health (15 startups loaded)
2. ✅ Determinism (5 identical calls)
3. ✅ Graceful failures (invalid inputs)
4. ✅ Rapid refresh (20 calls <5s)
5. ✅ Concurrent requests (30 simultaneous)
6. ✅ Scenario switching (all 3 scenarios)

**Expected**: `✓ ALL TESTS PASSED (6/6)`

---

### Manual Spot Checks
```bash
# Test determinism
curl -s http://localhost:8000/api/startups/1?include_intelligence=true | jq '.intelligence.investor_memory.canonical_pattern'
curl -s http://localhost:8000/api/startups/1?include_intelligence=true | jq '.intelligence.investor_memory.canonical_pattern'
# Both should return: "post_hype_collapse"

# Test invalid scenario (should default gracefully)
curl http://localhost:8000/api/portfolio/attention?scenario=INVALID | jq '.scenario'
# Should return: "no_intervention"

# Test rapid refreshes
time for i in {1..20}; do curl -s http://localhost:8000/api/portfolio/attention > /dev/null; done
# Should complete in <5 seconds
```

---

## 🎓 Documentation

| Document | Purpose |
|----------|---------|
| [FINAL_SUMMARY.md](FINAL_SUMMARY.md) | Complete system overview, all phases |
| [PHASE_9_HARDENING.md](PHASE_9_HARDENING.md) | Submission hardening details |
| [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md) | Pre-demo validation steps |
| [JUDGE_QA_GUIDE.md](JUDGE_QA_GUIDE.md) | Q&A preparation, talking points |
| [QUICK_TEST_COMMANDS.md](QUICK_TEST_COMMANDS.md) | PowerShell test commands |
| [backend/README.md](backend/README.md) | Technical deep dive |
| [backend/ARCHITECTURE.md](backend/ARCHITECTURE.md) | System architecture |

---

## 🚀 Deployment

### Local Development
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Production (Azure)
```bash
# Azure App Service deployment
az webapp up --name vc-portfolio-intelligence \
  --resource-group imagine-cup-2026 \
  --runtime "PYTHON:3.10"
```

### Environment Variables
```bash
# Optional: Azure OpenAI (has deterministic fallback)
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=https://your-instance.openai.azure.com
AZURE_OPENAI_DEPLOYMENT=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-01
```

---

## 🎯 Competitive Advantages

### vs. Traditional VC Portfolio Trackers
❌ **Traditional**: Static metrics, manual review  
✅ **This System**: Time-aware intelligence, automated foresight, attention allocation

### vs. Basic ML Risk Models
❌ **Basic ML**: Black-box scores, no explanations  
✅ **This System**: Explainable signals, investor reasoning, institutional memory

### vs. Generic LLM Tools
❌ **Generic LLMs**: Non-deterministic, speculative  
✅ **This System**: Deterministic outputs, conservative language, fallback reasoning

---

## 📊 Success Metrics

### Technical Excellence
✅ **100% determinism** (verified at startup)  
✅ **Zero live computation** (precomputed cache)  
✅ **Graceful degradation** (never exposes errors)  
✅ **Demo resilience** (rapid refreshes, concurrent users)

### Intelligence Quality
✅ **7 intelligence layers** (risk → memory → hardening)  
✅ **3 intervention scenarios** (no/early/delayed action)  
✅ **6 canonical patterns** (institutional memory)  
✅ **4 foresight dimensions** (urgency, windows, confidence, reversibility)

### Production Readiness
✅ **Submission-ready** (hardening complete)  
✅ **Judge-proof** (can explain all design choices)  
✅ **Demo-safe** (survives live scrutiny)  
✅ **Extensible** (clean module boundaries)

---

## 🤝 Contributing

This is a hackathon submission. For questions or collaboration:
- Review [JUDGE_QA_GUIDE.md](JUDGE_QA_GUIDE.md) for system design rationale
- Check [FINAL_SUMMARY.md](FINAL_SUMMARY.md) for complete feature list
- See [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md) for validation steps

---

## 📄 License

MIT License - Built for Microsoft Imagine Cup 2026

---

## 🏆 Submission Status

**Status**: ✅ SUBMISSION-READY

**Confidence Level**: HIGH
- Determinism verified
- Failures graceful
- Demo-resilient
- Judge-proof

**Ready for**: Live demo, judge scrutiny, production deployment

---

**Last Updated**: January 8, 2026  
**Version**: 1.0 (Production)  
**Built for**: Microsoft Imagine Cup 2026 - Enterprise AI Category
