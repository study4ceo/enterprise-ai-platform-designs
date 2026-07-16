# AI SRE Stack - Tests

This directory contains tests for the AI SRE Stack.

## Quick Start

### 1. Install Dependencies
```bash
cd d:\code_ai\code\project-designs\ai-sre-stack
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Create .env file with at minimum:
ANTHROPIC_API_KEY=your_key_here
```

### 3. Run Quick Tests
```bash
cd tests
python run_quick_tests.py
```

## Test Files

### Basic Tests (Included)
- `test_config.py` - Configuration loading test
- `test_security_imports.py` - Security modules import test
- `test_whitelist.py` - Action whitelist functionality test
- `run_quick_tests.py` - Quick test runner

### Complete Test Suite
See `../TESTING_GUIDE.md` for the full testing guide with all test files.

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
✓ 12 MCP servers enabled: ['kubernetes', 'aws', ...]

✅ Configuration test PASSED

============================================================
TEST SUMMARY
============================================================
✅ PASSED: test_config.py
✅ PASSED: test_security_imports.py
✅ PASSED: test_whitelist.py

Total: 3/3 tests passed

🎉 ALL QUICK TESTS PASSED!
```

## Troubleshooting

### "Anthropic API key not set"
- Create `.env` file in project root
- Add: `ANTHROPIC_API_KEY=your_key_here`

### "ModuleNotFoundError"
- Install dependencies: `pip install -r requirements.txt`
- Check you're in the correct directory

### "Permission denied" on logs
- Create logs directory: `mkdir ../logs`

## Next Steps

After quick tests pass:
1. Review `../TESTING_GUIDE.md` for comprehensive testing
2. Test individual MCP servers
3. Test full orchestrator cycle
4. Run integration tests
5. Deploy to production

## Documentation

- **TESTING_GUIDE.md** - Complete testing guide
- **README.md** - Main project readme
- **SECURITY_HARDENING_GUIDE.md** - Security documentation
