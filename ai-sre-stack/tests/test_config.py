"""Test configuration loading."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import config, get_enabled_mcps

def test_config_loading():
    """Test that configuration loads without errors."""
    print("Testing configuration loading...")
    
    # Test Anthropic config
    assert config.anthropic.api_key is not None, "Anthropic API key not set (check .env file)"
    print(f"✓ Anthropic API key configured")
    
    # Test security config
    assert config.security.enable_action_whitelist == True
    assert config.security.enable_rate_limiting == True
    assert config.security.enable_audit_logging == True
    assert config.security.enable_approval_workflow == True
    print(f"✓ All security controls enabled")
    
    # Test enabled MCPs
    enabled = get_enabled_mcps()
    print(f"✓ {len(enabled)} MCP servers enabled: {list(enabled.keys())}")
    
    print("\n✅ Configuration test PASSED\n")

if __name__ == "__main__":
    try:
        test_config_loading()
    except AssertionError as e:
        print(f"\n❌ Configuration test FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Configuration test FAILED with exception: {e}\n")
        sys.exit(1)
