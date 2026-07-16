# Quick Test Instructions

Get your AI SRE Stack tested in 5 minutes!

---

## Step 1: Install Dependencies (1 minute)

```bash
cd d:\code_ai\code\project-designs\ai-sre-stack
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed anthropic-0.x.x hvac-1.x.x pydantic-2.x.x ...
```

---

## Step 2: Create Environment File (1 minute)

### Option A: Use .env.example as template
```bash
copy .env.example .env
```

Then edit `.env` and add your Anthropic API key:
```bash
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

### Option B: Create minimal .env
Create `.env` file with just this:
```bash
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
DRY_RUN=true
AUTO_REMEDIATION=false
```

---

## Step 3: Run Quick Tests (1 minute)

### On Windows:
Double-click `run_tests.bat` or run:
```bash
run_tests.bat
```

### On Linux/Mac or in terminal:
```bash
cd tests
python run_quick_tests.py
```

---

## Expected Output

```
AI SRE Stack - Quick Test Suite
============================================================
Running basic validation tests...
============================================================

============================================================
Running: test_config.py
============================================================
Testing configuration loading...
✓ Anthropic API key configured
✓ All security controls enabled
✓ 12 MCP servers enabled: [...]

✅ Configuration test PASSED


============================================================
Running: test_security_imports.py
============================================================
Testing security module imports...
✓ ActionWhitelist initialized
  - Whitelisted actions: 48
✓ ActionThrottle initialized
  - Max per minute: 10
✓ AuditLogger initialized
  - Log path: logs\test_audit.jsonl
✓ ApprovalWorkflow initialized
  - Pending approvals: 0

✅ Security imports test PASSED


============================================================
Running: test_whitelist.py
============================================================
Testing Action Whitelist...
✓ Test 1 PASSED: Whitelisted action allowed
✓ Test 2 PASSED: Non-whitelisted action blocked
✓ Test 3 PASSED: Blocked action prevented
✓ Test 4 PASSED: High-risk action detected
✓ Test 5 PASSED: Statistics retrieved
  - Total whitelisted: 48
  - Total high-risk: 10
  - Total blocked: 3

✅ Action Whitelist test PASSED


============================================================
TEST SUMMARY
============================================================
✅ PASSED: test_config.py
✅ PASSED: test_security_imports.py
✅ PASSED: test_whitelist.py

Total: 3/3 tests passed

🎉 ALL QUICK TESTS PASSED!

Your AI SRE Stack is properly configured.

Next steps:
  1. Review TESTING_GUIDE.md for more comprehensive tests
  2. Test with real MCP servers (Kubernetes, AWS, etc.)
  3. Run in dry-run mode: python sre_orchestrator.py
```

---

## What These Tests Verify

### ✅ Test 1: Configuration (test_config.py)
- Anthropic API key is set
- Security controls are enabled
- Configuration loads without errors
- MCP servers are configured

### ✅ Test 2: Security Imports (test_security_imports.py)
- All security modules import correctly
- ActionWhitelist initializes
- ActionThrottle initializes
- AuditLogger initializes
- ApprovalWorkflow initializes

### ✅ Test 3: Action Whitelist (test_whitelist.py)
- Whitelisted actions are allowed
- Non-whitelisted actions are blocked
- Permanently blocked actions are prevented
- High-risk actions are detected
- Statistics are calculated correctly

---

## Troubleshooting

### ❌ Error: "Anthropic API key not set"

**Problem**: No API key in .env file

**Solution**:
1. Create `.env` file in project root (same directory as `sre_orchestrator.py`)
2. Add: `ANTHROPIC_API_KEY=sk-ant-your-key-here`
3. Get key from: https://console.anthropic.com/

---

### ❌ Error: "ModuleNotFoundError: No module named 'anthropic'"

**Problem**: Dependencies not installed

**Solution**:
```bash
pip install -r requirements.txt
```

---

### ❌ Error: "ModuleNotFoundError: No module named 'config'"

**Problem**: Running from wrong directory

**Solution**:
```bash
# Make sure you're in the tests directory
cd d:\code_ai\code\project-designs\ai-sre-stack\tests
python run_quick_tests.py
```

---

### ❌ Error: "Permission denied" writing to logs

**Problem**: No permission to create logs directory

**Solution**:
```bash
# Create logs directory manually
cd d:\code_ai\code\project-designs\ai-sre-stack
mkdir logs
```

---

## Next Steps After Tests Pass

### 1. Test Individual MCP Servers (Optional)
If you have Kubernetes, AWS, or other services configured:

```bash
# Test Kubernetes MCP
python -c "
import asyncio
from mcp_servers import KubernetesMCP

async def test():
    mcp = KubernetesMCP({'kubeconfig_path': '~/.kube/config', 'namespace': 'default'})
    await mcp.initialize()
    print(await mcp.observe())

asyncio.run(test())
"
```

### 2. Run Full Orchestrator (Dry Run)
```bash
# Set in .env
DRY_RUN=true
AUTO_REMEDIATION=false

# Run orchestrator
python sre_orchestrator.py
```

Expected output:
```
Initializing AI SRE Stack...
✓ Action whitelist enabled
✓ Rate limiting enabled
✓ Audit logging enabled
✓ Approval workflow enabled
✓ Kubernetes MCP initialized
Initialized 1/12 MCP servers

============================================================
Starting new SRE cycle...
============================================================
Cycle ID: 12345-...

=== OBSERVE PHASE ===
📊 kubernetes: healthy

=== DECIDE PHASE ===
🤖 Claude's Analysis:
{...}

=== ACT PHASE ===
🔒 DRY RUN MODE - No actions will be executed
```

### 3. Review Comprehensive Testing
See [TESTING_GUIDE.md](TESTING_GUIDE.md) for:
- Complete test suite (9 tests)
- MCP server testing
- Security integration testing
- Load testing
- Production readiness checklist

### 4. Production Deployment
Once all tests pass:
1. Configure production credentials in Vault
2. Set `DRY_RUN=false` in production .env
3. Configure Slack for notifications
4. Enable auto-remediation cautiously
5. Monitor audit logs regularly

---

## Test Results Checklist

Before moving to production, verify:

- [x] Quick tests all pass (3/3)
- [ ] All desired MCP servers initialize
- [ ] Full orchestrator cycle completes
- [ ] Security controls block unauthorized actions
- [ ] Audit log is writing correctly
- [ ] Slack notifications work (if enabled)
- [ ] Vault integration works (if enabled)
- [ ] Dry run mode produces sensible decisions
- [ ] Documentation reviewed
- [ ] Team trained on system

---

## Getting Help

### Documentation
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Complete testing guide
- [README.md](README.md) - Main documentation
- [SECURITY_HARDENING_GUIDE.md](SECURITY_HARDENING_GUIDE.md) - Security guide
- [QUICK_START.md](QUICK_START.md) - Quick start guide

### Common Issues
- API key issues: Check .env file location and format
- Import errors: Check Python version (3.9+ required)
- MCP failures: Check service credentials and connectivity
- Permission errors: Check file/directory permissions

---

## Success! What You've Validated

If all quick tests pass, you've verified:

✅ **Configuration System** - Loads correctly with all settings  
✅ **Security Modules** - All 5 security controls initialize  
✅ **Action Whitelist** - Properly blocks/allows actions  
✅ **Code Quality** - No import or syntax errors  
✅ **Basic Functionality** - Core systems operational  

**Your AI SRE Stack is ready for the next phase of testing!** 🎉

---

**Total Time**: ~5 minutes  
**Tests Run**: 3 basic validation tests  
**Status**: ✅ Quick validation complete  
**Next**: See TESTING_GUIDE.md for comprehensive testing
