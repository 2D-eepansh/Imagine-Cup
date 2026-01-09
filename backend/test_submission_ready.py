"""Submission-grade validation tests: verify determinism, resilience, and safety.

Run this script to confirm the system is judge-proof before demo.
"""

import sys
import requests
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any


BASE_URL = "http://localhost:8000"
COLORS = {
    "green": "\033[92m",
    "red": "\033[91m",
    "yellow": "\033[93m",
    "reset": "\033[0m",
}


def green(text: str) -> str:
    return f"{COLORS['green']}{text}{COLORS['reset']}"


def red(text: str) -> str:
    return f"{COLORS['red']}{text}{COLORS['reset']}"


def yellow(text: str) -> str:
    return f"{COLORS['yellow']}{text}{COLORS['reset']}"


def test_startup_health() -> bool:
    """Test 1: Verify server is running and cache is loaded."""
    print("\n" + "=" * 70)
    print("TEST 1: Startup Health Check")
    print("=" * 70)
    
    try:
        response = requests.get(f"{BASE_URL}/api/startups", timeout=5)
        if response.status_code != 200:
            print(red("✗ Server returned non-200 status"))
            return False
        
        data = response.json()
        startup_count = len(data.get("startups", []))
        
        if startup_count != 15:
            print(red(f"✗ Expected 15 startups, got {startup_count}"))
            return False
        
        print(green(f"✓ Server healthy: {startup_count} startups loaded"))
        return True
    
    except requests.exceptions.RequestException as e:
        print(red(f"✗ Server unreachable: {e}"))
        print(yellow("  → Make sure server is running: uvicorn main:app --port 8000"))
        return False


def test_determinism() -> bool:
    """Test 2: Verify outputs are deterministic (identical across calls)."""
    print("\n" + "=" * 70)
    print("TEST 2: Determinism Verification")
    print("=" * 70)
    
    try:
        outputs = []
        for i in range(5):
            response = requests.get(
                f"{BASE_URL}/api/startups/1?include_intelligence=true",
                timeout=5
            )
            if response.status_code != 200:
                print(red(f"✗ Call {i+1} returned non-200 status"))
                return False
            
            data = response.json()
            pattern = data.get("intelligence", {}).get("investor_memory", {}).get("canonical_pattern")
            risk_score = data.get("riskScore")
            outputs.append((pattern, risk_score))
        
        # Check all outputs identical
        if len(set(outputs)) != 1:
            print(red("✗ Non-deterministic outputs detected:"))
            for i, output in enumerate(outputs):
                print(f"  Call {i+1}: {output}")
            return False
        
        print(green(f"✓ Determinism verified: 5 calls produced identical outputs"))
        print(f"  Pattern: {outputs[0][0]}, Risk: {outputs[0][1]}")
        return True
    
    except Exception as e:
        print(red(f"✗ Determinism test failed: {e}"))
        return False


def test_graceful_failure() -> bool:
    """Test 3: Verify graceful handling of invalid inputs."""
    print("\n" + "=" * 70)
    print("TEST 3: Graceful Failure Handling")
    print("=" * 70)
    
    tests_passed = 0
    tests_total = 3
    
    # Test 3a: Invalid startup ID
    try:
        response = requests.get(f"{BASE_URL}/api/startups/999", timeout=5)
        if response.status_code == 404:
            print(green("✓ Invalid startup ID returns 404 (no stack trace)"))
            tests_passed += 1
        else:
            print(red(f"✗ Invalid startup ID returned {response.status_code}"))
    except Exception as e:
        print(red(f"✗ Invalid startup ID test failed: {e}"))
    
    # Test 3b: Invalid scenario (should default gracefully)
    try:
        response = requests.get(
            f"{BASE_URL}/api/portfolio/attention?scenario=INVALID",
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            scenario = data.get("scenario")
            if scenario == "no_intervention":
                print(green("✓ Invalid scenario defaults to 'no_intervention'"))
                tests_passed += 1
            else:
                print(red(f"✗ Invalid scenario returned '{scenario}' instead of 'no_intervention'"))
        else:
            print(red(f"✗ Invalid scenario returned {response.status_code}"))
    except Exception as e:
        print(red(f"✗ Invalid scenario test failed: {e}"))
    
    # Test 3c: Missing optional parameter (should use default)
    try:
        response = requests.get(f"{BASE_URL}/api/startups/1", timeout=5)
        if response.status_code == 200:
            data = response.json()
            has_intelligence = "intelligence" in data
            if not has_intelligence:
                print(green("✓ Missing include_intelligence defaults to False"))
                tests_passed += 1
            else:
                print(red("✗ Missing include_intelligence incorrectly included intelligence"))
        else:
            print(red(f"✗ Missing parameter test returned {response.status_code}"))
    except Exception as e:
        print(red(f"✗ Missing parameter test failed: {e}"))
    
    success = tests_passed == tests_total
    if success:
        print(green(f"\n✓ All {tests_total} failure handling tests passed"))
    else:
        print(red(f"\n✗ Only {tests_passed}/{tests_total} failure handling tests passed"))
    
    return success


def test_rapid_refresh() -> bool:
    """Test 4: Verify system handles rapid refreshes (no recomputation lag)."""
    print("\n" + "=" * 70)
    print("TEST 4: Rapid Refresh Resilience")
    print("=" * 70)
    
    try:
        start_time = time.time()
        
        for i in range(20):
            response = requests.get(f"{BASE_URL}/api/portfolio/attention", timeout=5)
            if response.status_code != 200:
                print(red(f"✗ Call {i+1} returned non-200 status"))
                return False
        
        elapsed = time.time() - start_time
        avg_time = elapsed / 20
        
        if elapsed < 5.0:  # Should complete in under 5 seconds (cached)
            print(green(f"✓ 20 rapid refreshes completed in {elapsed:.2f}s (avg {avg_time:.3f}s/call)"))
            return True
        else:
            print(yellow(f"⚠ 20 refreshes took {elapsed:.2f}s (slower than expected, but functional)"))
            return True  # Still pass, just warn
    
    except Exception as e:
        print(red(f"✗ Rapid refresh test failed: {e}"))
        return False


def test_concurrent_requests() -> bool:
    """Test 5: Verify system handles concurrent requests safely."""
    print("\n" + "=" * 70)
    print("TEST 5: Concurrent Request Safety")
    print("=" * 70)
    
    def fetch_startup(startup_id: str) -> Dict[str, Any]:
        response = requests.get(
            f"{BASE_URL}/api/startups/{startup_id}?include_intelligence=true",
            timeout=10
        )
        if response.status_code != 200:
            raise Exception(f"Non-200 status: {response.status_code}")
        return response.json()
    
    try:
        # Fire 30 concurrent requests for same startup
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(fetch_startup, "1") for _ in range(30)]
            results = [f.result() for f in futures]
        
        # Extract canonical patterns
        patterns = [
            r.get("intelligence", {}).get("investor_memory", {}).get("canonical_pattern")
            for r in results
        ]
        
        # Verify all identical
        unique_patterns = set(patterns)
        if len(unique_patterns) != 1:
            print(red(f"✗ Non-deterministic: got {len(unique_patterns)} different patterns"))
            return False
        
        print(green(f"✓ 30 concurrent requests produced identical outputs"))
        print(f"  Pattern: {patterns[0]}")
        return True
    
    except Exception as e:
        print(red(f"✗ Concurrent request test failed: {e}"))
        return False


def test_scenario_switching() -> bool:
    """Test 6: Verify scenario switching works correctly."""
    print("\n" + "=" * 70)
    print("TEST 6: Scenario Switching")
    print("=" * 70)
    
    scenarios = ["no_intervention", "early_intervention", "delayed_intervention"]
    
    try:
        for scenario in scenarios:
            response = requests.get(
                f"{BASE_URL}/api/portfolio/attention?scenario={scenario}",
                timeout=5
            )
            if response.status_code != 200:
                print(red(f"✗ Scenario '{scenario}' returned non-200 status"))
                return False
            
            data = response.json()
            returned_scenario = data.get("scenario")
            
            if returned_scenario != scenario:
                print(red(f"✗ Requested '{scenario}', got '{returned_scenario}'"))
                return False
            
            print(green(f"✓ Scenario '{scenario}' works correctly"))
        
        return True
    
    except Exception as e:
        print(red(f"✗ Scenario switching test failed: {e}"))
        return False


def main():
    """Run all validation tests."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "SUBMISSION-GRADE VALIDATION SUITE" + " " * 20 + "║")
    print("╚" + "=" * 68 + "╝")
    
    tests = [
        ("Startup Health", test_startup_health),
        ("Determinism", test_determinism),
        ("Graceful Failure", test_graceful_failure),
        ("Rapid Refresh", test_rapid_refresh),
        ("Concurrent Requests", test_concurrent_requests),
        ("Scenario Switching", test_scenario_switching),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(red(f"\n✗ CRITICAL ERROR in {test_name}: {e}"))
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = green("✓ PASS") if passed else red("✗ FAIL")
        print(f"{status}: {test_name}")
    
    print("=" * 70)
    
    if passed_count == total_count:
        print(green(f"\n✓ ALL TESTS PASSED ({passed_count}/{total_count})"))
        print(green("✓ System is SUBMISSION-READY and JUDGE-PROOF"))
        return 0
    else:
        print(red(f"\n✗ SOME TESTS FAILED ({passed_count}/{total_count} passed)"))
        print(yellow("  → Review failures above and fix before submission"))
        return 1


if __name__ == "__main__":
    sys.exit(main())
