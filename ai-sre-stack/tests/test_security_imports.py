"""Test security module imports."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from security import ActionWhitelist, ActionThrottle, AuditLogger, ApprovalWorkflow

def test_security_imports():
    """Test that all security modules import correctly."""
    print("Testing security module imports...")
    
    # Test ActionWhitelist
    whitelist = ActionWhitelist()
    print(f"✓ ActionWhitelist initialized")
    print(f"  - Whitelisted actions: {whitelist.get_stats()['total_whitelisted_actions']}")
    
    # Test ActionThrottle
    throttle = ActionThrottle()
    print(f"✓ ActionThrottle initialized")
    print(f"  - Max per minute: {throttle.max_actions_per_minute}")
    
    # Test AuditLogger
    audit = AuditLogger({'audit_log_path': './logs/test_audit.jsonl'})
    print(f"✓ AuditLogger initialized")
    print(f"  - Log path: {audit.audit_log_path}")
    
    # Test ApprovalWorkflow
    approval = ApprovalWorkflow()
    print(f"✓ ApprovalWorkflow initialized")
    print(f"  - Pending approvals: {approval.get_stats()['pending_count']}")
    
    print("\n✅ Security imports test PASSED\n")

if __name__ == "__main__":
    try:
        test_security_imports()
    except Exception as e:
        print(f"\n❌ Security imports test FAILED: {e}\n")
        sys.exit(1)
