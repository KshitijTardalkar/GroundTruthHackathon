"""
Run all tests in sequence
Run: python tests/run_all_tests.py
"""

import subprocess
import sys


def run_test(script_name):
    """Run a test script and return success status"""
    print(f"\n{'=' * 60}")
    print(f"Running: {script_name}")
    print(f"{'=' * 60}")

    result = subprocess.run([sys.executable, f"tests/{script_name}"])
    return result.returncode == 0


if __name__ == "__main__":
    tests = [
        "test_pii_masking.py",
        "test_rag_retrieval.py",
        "test_conversation_memory.py",
        "test_full_integration.py",
    ]

    print("🚀 Starting Full Test Suite...")

    results = {}
    for test in tests:
        try:
            success = run_test(test)
            results[test] = "✅ PASSED" if success else "❌ FAILED"
        except Exception as e:
            results[test] = f"❌ ERROR: {str(e)}"

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    for test, result in results.items():
        print(f"  {test}: {result}")

    all_passed = all("✅" in r for r in results.values())
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 60)
