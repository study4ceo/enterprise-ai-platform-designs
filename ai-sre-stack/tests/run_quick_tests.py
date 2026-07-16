"""Run quick test suite - basic validation tests only."""
import subprocess
import sys
from pathlib import Path

def run_test(test_file):
    """Run a single test file."""
    print(f"\n{'='*60}")
    print(f"Running: {test_file}")
    print('='*60)
    
    test_path = Path(__file__).parent / test_file
    result = subprocess.run([sys.executable, str(test_path)], capture_output=False)
    return result.returncode == 0

def main():
    """Run quick tests."""
    tests = [
        'test_config.py',
        'test_security_imports.py',
        'test_whitelist.py',
    ]
    
    print("AI SRE Stack - Quick Test Suite")
    print("="*60)
    print("Running basic validation tests...")
    print("="*60)
    
    results = {}
    for test in tests:
        try:
            results[test] = run_test(test)
        except Exception as e:
            print(f"✗ {test} failed with exception: {e}")
            results[test] = False
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL QUICK TESTS PASSED!")
        print("\nYour AI SRE Stack is properly configured.")
        print("\nNext steps:")
        print("  1. Review TESTING_GUIDE.md for more comprehensive tests")
        print("  2. Test with real MCP servers (Kubernetes, AWS, etc.)")
        print("  3. Run in dry-run mode: python sre_orchestrator.py")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review.")
        print("\nCommon issues:")
        print("  - Missing ANTHROPIC_API_KEY in .env file")
        print("  - Missing dependencies: pip install -r requirements.txt")
        print("  - Import errors: Check Python path")
        return 1

if __name__ == "__main__":
    sys.exit(main())
