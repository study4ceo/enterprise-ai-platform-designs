"""Test action whitelist."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from security import ActionWhitelist

def test_action_whitelist():
    """Test action whitelisting functionality."""
    print("Testing Action Whitelist...")
    
    whitelist = ActionWhitelist()
    
    # Test 1: Whitelisted action (should pass)
    allowed, reason = whitelist.is_allowed('kubernetes', 'observe')
    assert allowed == True, f"Expected observe to be allowed: {reason}"
    print(f"✓ Test 1 PASSED: Whitelisted action allowed")
    
    # Test 2: Non-whitelisted action (should fail)
    allowed, reason = whitelist.is_allowed('kubernetes', 'delete_namespace')
    assert allowed == False, f"Expected delete_namespace to be blocked"
    print(f"✓ Test 2 PASSED: Non-whitelisted action blocked")
    
    # Test 3: Permanently blocked action (should fail)
    allowed, reason = whitelist.is_allowed('aws', 'terminate_all_instances')
    assert allowed == False, f"Expected terminate_all_instances to be blocked"
    print(f"✓ Test 3 PASSED: Blocked action prevented")
    
    # Test 4: High-risk detection
    is_high = whitelist.is_high_risk('kubernetes', 'delete_pod')
    assert is_high == True, "Expected delete_pod to be high-risk"
    print(f"✓ Test 4 PASSED: High-risk action detected")
    
    # Test 5: Get statistics
    stats = whitelist.get_stats()
    print(f"✓ Test 5 PASSED: Statistics retrieved")
    print(f"  - Total whitelisted: {stats['total_whitelisted_actions']}")
    print(f"  - Total high-risk: {stats['total_high_risk_actions']}")
    print(f"  - Total blocked: {stats['total_blocked_actions']}")
    
    print("\n✅ Action Whitelist test PASSED\n")

if __name__ == "__main__":
    try:
        test_action_whitelist()
    except AssertionError as e:
        print(f"\n❌ Action Whitelist test FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Action Whitelist test FAILED with exception: {e}\n")
        sys.exit(1)
