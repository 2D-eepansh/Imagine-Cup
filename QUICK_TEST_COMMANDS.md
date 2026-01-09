# Quick Test Commands

Run these commands to verify the system before demo.

---

## 1. Start Server

```powershell
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
✓ Determinism verified: cache keys exclude wall-clock timestamps
✓ Resilience verified: cache is read-only after startup
✓ Resilience verified: concurrent requests safe (read-only cache)
✓ Resilience verified: rapid refreshes safe (no recomputation)

✓ All hardening checks passed
✓ System is submission-grade and judge-proof
======================================================================
```

---

## 2. Run Automated Tests

```powershell
cd backend
python test_submission_ready.py
```

**Expected Output**:
```
✓ PASS: Startup Health
✓ PASS: Determinism
✓ PASS: Graceful Failure
✓ PASS: Rapid Refresh
✓ PASS: Concurrent Requests
✓ PASS: Scenario Switching

✓ ALL TESTS PASSED (6/6)
✓ System is SUBMISSION-READY and JUDGE-PROOF
```

---

## 3. Test Basic Endpoints

### List All Startups
```powershell
curl http://localhost:8000/api/startups | ConvertFrom-Json | Select-Object -ExpandProperty startups | Select-Object name, riskScore, severity | Format-Table
```

**Expected**: 15 startups with risk scores

---

### Get Single Startup (Base)
```powershell
curl http://localhost:8000/api/startups/1 | ConvertFrom-Json | Select-Object name, riskScore, severity
```

**Expected**: Lumina Health, 72.4 risk, high severity

---

### Get Single Startup (Full Intelligence)
```powershell
curl "http://localhost:8000/api/startups/1?include_intelligence=true" | ConvertFrom-Json | Select-Object -ExpandProperty intelligence | Select-Object -Property timeSnapshots, foresight, investor_memory | ConvertTo-Json
```

**Expected**: Full intelligence object with snapshots, foresight, memory

---

### Get Portfolio Attention
```powershell
curl http://localhost:8000/api/portfolio/attention | ConvertFrom-Json | Select-Object scenario, @{Name='ImmediateAttention';Expression={$_.attention_summary.immediate_attention_required.Count}}, @{Name='HighRiskCount';Expression={$_.risk_concentration.high_risk_count}}
```

**Expected**: scenario='no_intervention', 6 immediate attention, 6 high-risk

---

## 4. Test Determinism

```powershell
# Call same endpoint twice, compare outputs
$response1 = curl -s "http://localhost:8000/api/startups/1?include_intelligence=true" | ConvertFrom-Json
$response2 = curl -s "http://localhost:8000/api/startups/1?include_intelligence=true" | ConvertFrom-Json

$pattern1 = $response1.intelligence.investor_memory.canonical_pattern
$pattern2 = $response2.intelligence.investor_memory.canonical_pattern

if ($pattern1 -eq $pattern2) {
    Write-Host "✓ Determinism verified: Both calls returned '$pattern1'" -ForegroundColor Green
} else {
    Write-Host "✗ Non-deterministic: Got '$pattern1' and '$pattern2'" -ForegroundColor Red
}
```

**Expected**: ✓ Determinism verified

---

## 5. Test Graceful Failures

### Invalid Startup ID
```powershell
curl http://localhost:8000/api/startups/999
```

**Expected**: `{"detail":"Startup not found"}` (404, no stack trace)

---

### Invalid Scenario
```powershell
curl "http://localhost:8000/api/portfolio/attention?scenario=INVALID" | ConvertFrom-Json | Select-Object scenario
```

**Expected**: `scenario: no_intervention` (defaulted gracefully)

---

### Missing Optional Parameter
```powershell
curl http://localhost:8000/api/startups/1 | ConvertFrom-Json | Get-Member -Name intelligence
```

**Expected**: No 'intelligence' property (defaults to false)

---

## 6. Test Scenario Switching

```powershell
$scenarios = @("no_intervention", "early_intervention", "delayed_intervention")

foreach ($scenario in $scenarios) {
    $response = curl -s "http://localhost:8000/api/portfolio/attention?scenario=$scenario" | ConvertFrom-Json
    $returned_scenario = $response.scenario
    
    if ($returned_scenario -eq $scenario) {
        Write-Host "✓ Scenario '$scenario' works" -ForegroundColor Green
    } else {
        Write-Host "✗ Requested '$scenario', got '$returned_scenario'" -ForegroundColor Red
    }
}
```

**Expected**: All 3 scenarios pass

---

## 7. Test Rapid Refreshes

```powershell
Measure-Command {
    1..20 | ForEach-Object {
        curl -s http://localhost:8000/api/portfolio/attention | Out-Null
    }
}
```

**Expected**: <5 seconds total

---

## 8. Quick Intelligence Spot Check

### Show Time Snapshots
```powershell
curl -s "http://localhost:8000/api/startups/1?include_intelligence=true" | ConvertFrom-Json | Select-Object -ExpandProperty intelligence | Select-Object -ExpandProperty timeSnapshots | Format-Table days_ago, risk_score, severity
```

**Expected**: 6 snapshots from 60 days ago to present

---

### Show Foresight Signals
```powershell
curl -s "http://localhost:8000/api/startups/1?include_intelligence=true" | ConvertFrom-Json | Select-Object -ExpandProperty intelligence | Select-Object -ExpandProperty foresight | Select-Object -ExpandProperty no_intervention | Select-Object urgency, confidence, action_window_days, reversibility_marker
```

**Expected**: urgency='HIGH', confidence='HIGH', action_window_days=7-14, reversibility='VIABLE'

---

### Show Investor Memory
```powershell
curl -s "http://localhost:8000/api/startups/1?include_intelligence=true" | ConvertFrom-Json | Select-Object -ExpandProperty intelligence | Select-Object -ExpandProperty investor_memory | Select-Object canonical_pattern, pattern_label, memory_signal
```

**Expected**: pattern='post_hype_collapse', label='Post-Hype Collapse', memory signal present

---

### Show Portfolio Memory Insights
```powershell
curl -s http://localhost:8000/api/portfolio/attention | ConvertFrom-Json | Select-Object -ExpandProperty portfolio_memory | Select-Object -ExpandProperty portfolio_memory_insights
```

**Expected**: 2-3 insights about portfolio pattern distribution

---

## 9. Demo-Ready One-Liners

### Show All Startups with Risk Scores
```powershell
curl -s http://localhost:8000/api/startups | ConvertFrom-Json | Select-Object -ExpandProperty startups | Sort-Object riskScore -Descending | Select-Object name, riskScore, severity | Format-Table
```

---

### Show High-Risk Startups Only
```powershell
curl -s http://localhost:8000/api/startups | ConvertFrom-Json | Select-Object -ExpandProperty startups | Where-Object {$_.severity -eq 'high'} | Select-Object name, riskScore | Format-Table
```

---

### Show Immediate Attention List
```powershell
curl -s http://localhost:8000/api/portfolio/attention | ConvertFrom-Json | Select-Object -ExpandProperty attention_summary | Select-Object -ExpandProperty immediate_attention_required | Format-Table
```

---

## 10. Emergency Checks (If Something Breaks)

### Check Server is Running
```powershell
curl http://localhost:8000/api/startups | Select-Object -First 1
```

**If Fails**: Server not started or crashed

---

### Check Hardening Module Loads
```powershell
cd backend
python -c "from hardening import run_hardening_checks; run_hardening_checks()"
```

**Expected**: Hardening checks pass

---

### Check All Dependencies Installed
```powershell
cd backend
python -c "import fastapi, pandas, numpy, sklearn, openai; print('✓ All dependencies OK')"
```

**Expected**: ✓ All dependencies OK

---

### View Server Logs
```powershell
# Check terminal where uvicorn is running
# Look for ERROR or WARNING lines
```

---

## Quick Reference URLs

- **API Docs**: http://localhost:8000/docs (FastAPI auto-generated)
- **List Startups**: http://localhost:8000/api/startups
- **Single Startup**: http://localhost:8000/api/startups/1?include_intelligence=true
- **Portfolio Attention**: http://localhost:8000/api/portfolio/attention

---

**Status**: Ready for testing  
**Last Updated**: January 8, 2026
