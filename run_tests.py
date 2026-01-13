import subprocess
import sys

def run_tests():
    print("="*70)
    print("RUNNING ALL TESTS")
    print("="*70)
    
    # Unit tests
    print("\n📦 UNIT TESTS")
    result = subprocess.run(
        ["pytest", "tests/unit", "-v"],
        capture_output=False
    )
    
    if result.returncode != 0:
        print("❌ Unit tests failed")
        return False
    
    # Integration tests (require a running server)
    print("\n🔗 INTEGRATION TESTS")
    print("⚠️  Make sure the server is running at http://localhost:8000")
    input("Press Enter to continue...")
    
    result = subprocess.run(
        ["pytest", "tests/integration", "-v"],
        capture_output=False
    )
    
    if result.returncode != 0:
        print("❌ Integration tests failed")
        return False
    
    # Scenario tests
    print("\n📋 SCENARIO TESTS")
    result = subprocess.run(
        ["pytest", "tests/scenarios", "-v", "-s"],
        capture_output=False
    )
    
    if result.returncode != 0:
        print("❌ Scenario tests failed")
        return False
    
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED SUCCESSFULLY!")
    print("="*70)
    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
