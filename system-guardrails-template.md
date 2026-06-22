# System Guardrails & Safety Framework - Universal Template

**Document Date:** June 18, 2026  
**Version:** 1.0  
**Purpose:** Comprehensive guardrails for production systems  
**Applicability:** All projects in `project-designs/`

---

## 📋 Overview

This document defines mandatory guardrails that must be implemented in every production system. These guardrails ensure safety, compliance, security, reliability, and ethical operation.

---

## 🛡️ 1. Security Guardrails

### **1.1 Authentication & Authorization**

**Mandatory Controls:**
- ✅ Multi-factor authentication (MFA) for admin accounts
- ✅ PASETO v4 tokens (NOT JWT) with 15-minute expiry
- ✅ Refresh tokens stored as HTTP-only cookies
- ✅ Role-based access control (RBAC)
- ✅ Principle of least privilege
- ✅ Session timeout after 15 minutes of inactivity
- ✅ Account lockout after 5 failed login attempts (30-minute lockout)

**Implementation:**
```python
# Example: Account lockout guardrail
class AuthenticationGuardrail:
    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_DURATION = 1800  # 30 minutes
    
    async def verify_login(self, user_id: str, password: str) -> dict:
        """Login with rate limiting guardrail"""
        
        # Check if account is locked
        lockout_until = await self.get_lockout_time(user_id)
        if lockout_until and datetime.now() < lockout_until:
            raise AccountLockedError(
                f"Account locked until {lockout_until}. "
                f"Contact support if you need immediate access."
            )
        
        # Verify credentials
        if not await self.verify_password(user_id, password):
            failed_attempts = await self.increment_failed_attempts(user_id)
            
            if failed_attempts >= self.MAX_FAILED_ATTEMPTS:
                await self.lock_account(user_id, self.LOCKOUT_DURATION)
                raise AccountLockedError(
                    "Too many failed attempts. Account locked for 30 minutes."
                )
            
            raise InvalidCredentialsError(
                f"Invalid credentials. {self.MAX_FAILED_ATTEMPTS - failed_attempts} attempts remaining."
            )
        
        # Success - reset failed attempts
        await self.reset_failed_attempts(user_id)
        return await self.generate_tokens(user_id)
```

---

### **1.2 Data Protection**

**Mandatory Controls:**
- ✅ TLS 1.3 for all data in transit
- ✅ AES-256 encryption for data at rest
- ✅ Secrets stored in Vault (never in code/config)
- ✅ PII/PHI encrypted with field-level encryption
- ✅ No sensitive data in logs or error messages
- ✅ Secure deletion (overwrite before delete)

**Example:**
```python
# Guardrail: Sanitize logs
class SecureLogger:
    SENSITIVE_PATTERNS = [
        r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
        r'\b\d{16}\b',              # Credit card
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
        r'password["\']?\s*[:=]\s*["\']?([^"\']+)',  # Password
    ]
    
    def sanitize(self, message: str) -> str:
        """Remove sensitive data from logs"""
        for pattern in self.SENSITIVE_PATTERNS:
            message = re.sub(pattern, '[REDACTED]', message, flags=re.IGNORECASE)
        return message
    
    def info(self, message: str, **kwargs):
        safe_message = self.sanitize(message)
        safe_kwargs = {k: self.sanitize(str(v)) for k, v in kwargs.items()}
        logfire.info(safe_message, **safe_kwargs)
```

---

### **1.3 Input Validation**

**Mandatory Controls:**
- ✅ Validate all user inputs (whitelist approach)
- ✅ Sanitize inputs to prevent injection attacks
- ✅ File upload restrictions (type, size, content scan)
- ✅ API request size limits
- ✅ SQL parameterized queries only

**Example:**
```python
# Guardrail: Input validation
from pydantic import BaseModel, validator, constr

class UserInput(BaseModel):
    email: EmailStr  # Built-in email validation
    age: int = Field(ge=13, le=120)  # Age constraints
    username: constr(min_length=3, max_length=30, regex=r'^[a-zA-Z0-9_]+$')
    
    @validator('username')
    def validate_username(cls, v):
        """Additional username validation"""
        forbidden = ['admin', 'root', 'system']
        if v.lower() in forbidden:
            raise ValueError('Username not allowed')
        return v

# File upload guardrail
class FileUploadGuardrail:
    MAX_SIZE = 20 * 1024 * 1024  # 20MB
    ALLOWED_TYPES = {'image/jpeg', 'image/png', 'application/pdf'}
    
    async def validate_upload(self, file: bytes, content_type: str) -> dict:
        """Validate file upload"""
        
        # Size check
        if len(file) > self.MAX_SIZE:
            raise ValueError(f"File too large. Max size: {self.MAX_SIZE} bytes")
        
        # Type check
        if content_type not in self.ALLOWED_TYPES:
            raise ValueError(f"File type not allowed: {content_type}")
        
        # Content scan (malware)
        is_safe = await self.scan_for_malware(file)
        if not is_safe:
            raise SecurityError("File failed security scan")
        
        return {'valid': True, 'size': len(file)}
```

---

## 🔒 2. Privacy & Compliance Guardrails

### **2.1 GDPR Compliance**

**Mandatory Controls:**
- ✅ Consent management for data processing
- ✅ Right to access (download all user data)
- ✅ Right to rectification (update data)
- ✅ Right to erasure ("right to be forgotten")
- ✅ Data portability (export in machine-readable format)
- ✅ Privacy by design and by default
- ✅ Data breach notification within 72 hours

**Implementation:**
```python
# GDPR right to erasure guardrail
class GDPRCompliance:
    async def handle_deletion_request(self, user_id: str) -> dict:
        """GDPR-compliant user data deletion"""
        
        # 1. Log the request (audit trail)
        await self.audit_log.record({
            'event': 'gdpr_deletion_request',
            'user_id': user_id,
            'timestamp': datetime.now()
        })
        
        # 2. Verify user identity (prevent malicious deletions)
        if not await self.verify_user_identity(user_id):
            raise UnauthorizedError("Identity verification failed")
        
        # 3. Check legal retention requirements
        retention_hold = await self.check_retention_holds(user_id)
        if retention_hold:
            return {
                'status': 'pending',
                'reason': f'Data retention required until {retention_hold.expiry}',
                'legal_basis': retention_hold.reason
            }
        
        # 4. Delete personal data
        deleted_records = await self.delete_personal_data(user_id)
        
        # 5. Anonymize analytics (retain for business, remove PII)
        await self.anonymize_analytics(user_id)
        
        # 6. Notify user
        await self.notify_deletion_complete(user_id)
        
        return {
            'status': 'completed',
            'deleted_records': deleted_records,
            'completed_at': datetime.now()
        }
    
    async def delete_personal_data(self, user_id: str) -> int:
        """Delete all PII for a user"""
        tables_to_clean = [
            'users',
            'profiles',
            'addresses',
            'payment_methods',
            'sessions',
            'audit_logs'  # Remove PII but keep anonymized audit trail
        ]
        
        total_deleted = 0
        for table in tables_to_clean:
            deleted = await self.db.execute(
                f"DELETE FROM {table} WHERE user_id = $1",
                user_id
            )
            total_deleted += deleted
        
        return total_deleted
```

---

### **2.2 Data Retention & Deletion**

**Mandatory Controls:**
- ✅ Define retention periods per data type
- ✅ Automatic deletion after retention period
- ✅ Secure deletion (not just marking as deleted)
- ✅ Audit logs retained for 7 years (compliance)

**Example:**
```python
# Automatic data retention guardrail
class DataRetentionGuardrail:
    RETENTION_POLICIES = {
        'user_sessions': 30,      # days
        'api_logs': 90,
        'user_data': 365 * 2,     # 2 years after account closure
        'audit_logs': 365 * 7,    # 7 years (legal requirement)
        'payment_records': 365 * 7
    }
    
    async def enforce_retention(self):
        """Daily job to enforce retention policies"""
        
        for data_type, retention_days in self.RETENTION_POLICIES.items():
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            deleted = await self.secure_delete(
                table=data_type,
                where=f"created_at < '{cutoff_date}'"
            )
            
            logfire.info(
                f"Retention enforced: {data_type}",
                deleted_records=deleted,
                cutoff_date=cutoff_date
            )
```

---

## 🚨 3. Operational Guardrails

### **3.1 Rate Limiting**

**Mandatory Controls:**
- ✅ API rate limiting per user/IP
- ✅ Exponential backoff for retries
- ✅ Circuit breakers for external services
- ✅ Request queuing with max queue depth

**Implementation:**
```python
# Rate limiting guardrail
from redis import Redis
from datetime import datetime, timedelta

class RateLimitGuardrail:
    def __init__(self, redis: Redis):
        self.redis = redis
    
    async def check_rate_limit(
        self,
        user_id: str,
        endpoint: str,
        limit: int = 1000,
        window: int = 60  # seconds
    ) -> dict:
        """Token bucket rate limiting"""
        
        key = f"rate_limit:{user_id}:{endpoint}"
        current = await self.redis.get(key)
        
        if current is None:
            # First request in window
            await self.redis.setex(key, window, 1)
            return {'allowed': True, 'remaining': limit - 1}
        
        current = int(current)
        
        if current >= limit:
            # Rate limit exceeded
            ttl = await self.redis.ttl(key)
            raise RateLimitExceededError(
                f"Rate limit exceeded. Retry after {ttl} seconds.",
                retry_after=ttl
            )
        
        # Increment counter
        await self.redis.incr(key)
        
        return {
            'allowed': True,
            'remaining': limit - current - 1,
            'reset_in': await self.redis.ttl(key)
        }


# Circuit breaker guardrail
class CircuitBreakerGuardrail:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure = None
        self.state = 'closed'  # closed, open, half_open
    
    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker"""
        
        # Check if circuit is open
        if self.state == 'open':
            if datetime.now() - self.last_failure > timedelta(seconds=self.timeout):
                self.state = 'half_open'
            else:
                raise CircuitOpenError(
                    f"Circuit breaker open. Retry after {self.timeout}s"
                )
        
        try:
            result = await func(*args, **kwargs)
            
            # Success - reset if in half_open
            if self.state == 'half_open':
                self.state = 'closed'
                self.failures = 0
            
            return result
        
        except Exception as e:
            self.failures += 1
            self.last_failure = datetime.now()
            
            if self.failures >= self.failure_threshold:
                self.state = 'open'
                logfire.error(
                    "Circuit breaker opened",
                    failures=self.failures,
                    threshold=self.failure_threshold
                )
            
            raise
```

---

### **3.2 Resource Limits**

**Mandatory Controls:**
- ✅ Database connection pooling (max connections)
- ✅ Memory limits per request
- ✅ Timeout for all operations
- ✅ Maximum file size uploads
- ✅ Request payload size limits

**Example:**
```python
# Resource limit guardrail
class ResourceLimitGuardrail:
    MAX_QUERY_TIME = 30  # seconds
    MAX_MEMORY_PER_REQUEST = 512 * 1024 * 1024  # 512MB
    MAX_DB_CONNECTIONS = 100
    
    async def execute_query_with_timeout(self, query: str, *args):
        """Execute database query with timeout"""
        
        try:
            result = await asyncio.wait_for(
                self.db.execute(query, *args),
                timeout=self.MAX_QUERY_TIME
            )
            return result
        except asyncio.TimeoutError:
            logfire.error(
                "Query timeout exceeded",
                query=query[:100],  # Log first 100 chars
                timeout=self.MAX_QUERY_TIME
            )
            raise QueryTimeoutError(
                f"Query exceeded {self.MAX_QUERY_TIME}s timeout"
            )
    
    def check_memory_usage(self):
        """Check if memory usage is within limits"""
        import psutil
        process = psutil.Process()
        memory_usage = process.memory_info().rss
        
        if memory_usage > self.MAX_MEMORY_PER_REQUEST:
            logfire.warning(
                "Memory usage high",
                usage_mb=memory_usage / 1024 / 1024,
                limit_mb=self.MAX_MEMORY_PER_REQUEST / 1024 / 1024
            )
```

---

## 🎯 4. AI/ML Specific Guardrails

### **4.1 Content Safety**

**Mandatory Controls:**
- ✅ Content moderation for user inputs
- ✅ Toxic content detection
- ✅ PII detection in prompts
- ✅ Prompt injection prevention
- ✅ Output filtering for harmful content

**Implementation:**
```python
# AI content safety guardrail
class AIContentSafetyGuardrail:
    TOXIC_THRESHOLD = 0.7
    PII_PATTERNS = [
        r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
        r'\b\d{16}\b',              # Credit card
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'  # Email
    ]
    
    async def validate_prompt(self, prompt: str) -> dict:
        """Validate user prompt before sending to AI"""
        
        # 1. Check for PII
        pii_found = self.detect_pii(prompt)
        if pii_found:
            raise PromptValidationError(
                "Prompt contains personal information. Please remove sensitive data."
            )
        
        # 2. Check for prompt injection
        if self.is_prompt_injection(prompt):
            logfire.warning("Prompt injection attempt detected", prompt=prompt[:100])
            raise SecurityError("Invalid prompt detected")
        
        # 3. Check toxicity
        toxicity_score = await self.check_toxicity(prompt)
        if toxicity_score > self.TOXIC_THRESHOLD:
            raise ContentPolicyViolation(
                "Prompt violates content policy"
            )
        
        return {'safe': True, 'toxicity_score': toxicity_score}
    
    def detect_pii(self, text: str) -> bool:
        """Detect PII in text"""
        for pattern in self.PII_PATTERNS:
            if re.search(pattern, text):
                return True
        return False
    
    def is_prompt_injection(self, prompt: str) -> bool:
        """Detect prompt injection attempts"""
        injection_patterns = [
            r'ignore (previous|above) instructions',
            r'you are now',
            r'disregard',
            r'new instructions:',
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                return True
        return False
```

---

### **4.2 AI Output Validation**

**Mandatory Controls:**
- ✅ Validate AI output format
- ✅ Check for hallucinations (confidence scores)
- ✅ Filter harmful/biased content
- ✅ Verify factual accuracy (where possible)
- ✅ Log all AI interactions for audit

**Example:**
```python
# AI output validation guardrail
class AIOutputValidationGuardrail:
    MIN_CONFIDENCE = 0.7
    
    async def validate_output(
        self,
        output: str,
        expected_format: str = None,
        confidence: float = None
    ) -> dict:
        """Validate AI-generated output"""
        
        # 1. Confidence check
        if confidence and confidence < self.MIN_CONFIDENCE:
            logfire.warning(
                "Low confidence AI output",
                confidence=confidence,
                threshold=self.MIN_CONFIDENCE
            )
            return {
                'valid': False,
                'reason': 'Low confidence',
                'recommendation': 'Request human review'
            }
        
        # 2. Format validation
        if expected_format and not self.validate_format(output, expected_format):
            return {
                'valid': False,
                'reason': 'Invalid format'
            }
        
        # 3. Content safety
        if self.contains_harmful_content(output):
            logfire.error("Harmful content in AI output")
            return {
                'valid': False,
                'reason': 'Content policy violation'
            }
        
        return {'valid': True}
    
    def contains_harmful_content(self, text: str) -> bool:
        """Check for harmful content in output"""
        harmful_patterns = [
            r'discriminat',
            r'illegal',
            # Add more patterns
        ]
        
        for pattern in harmful_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
```

---

### **4.3 Cost Controls**

**Mandatory Controls:**
- ✅ Token usage limits per user/session
- ✅ Cost estimation before API calls
- ✅ Budget alerts and hard limits
- ✅ Model selection based on complexity

**Example:**
```python
# AI cost control guardrail
class AICostControlGuardrail:
    MAX_TOKENS_PER_REQUEST = 4000
    MAX_COST_PER_USER_DAILY = 10.0  # USD
    
    MODEL_COSTS = {
        'gpt-5.5': 0.0001,  # per token
        'claude-opus-4.8': 0.00015
    }
    
    async def check_budget(self, user_id: str, estimated_tokens: int, model: str) -> dict:
        """Check if request is within budget"""
        
        # 1. Token limit check
        if estimated_tokens > self.MAX_TOKENS_PER_REQUEST:
            raise BudgetExceededError(
                f"Request exceeds max tokens: {self.MAX_TOKENS_PER_REQUEST}"
            )
        
        # 2. Daily cost check
        daily_usage = await self.get_daily_usage(user_id)
        estimated_cost = estimated_tokens * self.MODEL_COSTS.get(model, 0.0001)
        
        if daily_usage + estimated_cost > self.MAX_COST_PER_USER_DAILY:
            raise BudgetExceededError(
                f"Daily budget exceeded. Used: ${daily_usage:.2f}, "
                f"Limit: ${self.MAX_COST_PER_USER_DAILY}"
            )
        
        return {
            'approved': True,
            'estimated_cost': estimated_cost,
            'remaining_budget': self.MAX_COST_PER_USER_DAILY - daily_usage
        }
```

---

## 📊 5. Monitoring & Alerting Guardrails

### **5.1 Health Checks**

**Mandatory Controls:**
- ✅ Liveness probe (is service running?)
- ✅ Readiness probe (can service accept traffic?)
- ✅ Dependency health checks
- ✅ Automated recovery on failure

**Implementation:**
```python
# Health check guardrail
class HealthCheckGuardrail:
    async def liveness_probe(self) -> dict:
        """Check if service is alive"""
        return {'status': 'ok', 'timestamp': datetime.now()}
    
    async def readiness_probe(self) -> dict:
        """Check if service can accept traffic"""
        
        checks = {
            'database': await self.check_database(),
            'redis': await self.check_redis(),
            'external_apis': await self.check_external_apis()
        }
        
        all_healthy = all(checks.values())
        
        return {
            'status': 'ready' if all_healthy else 'not_ready',
            'checks': checks,
            'timestamp': datetime.now()
        }
    
    async def check_database(self) -> bool:
        """Check database connectivity"""
        try:
            await self.db.execute("SELECT 1")
            return True
        except Exception as e:
            logfire.error("Database health check failed", error=str(e))
            return False
```

---

### **5.2 Error Budgets & SLOs**

**Mandatory Controls:**
- ✅ Define Service Level Objectives (SLOs)
- ✅ Error budget tracking
- ✅ Automatic alerts when budget burns too fast
- ✅ Feature freeze when budget depleted

**Example:**
```python
# SLO and error budget guardrail
class SLOGuardrail:
    TARGET_AVAILABILITY = 0.999  # 99.9%
    MEASUREMENT_WINDOW = 30  # days
    
    async def check_error_budget(self) -> dict:
        """Check remaining error budget"""
        
        # Get metrics for last 30 days
        total_requests = await self.get_total_requests(days=30)
        failed_requests = await self.get_failed_requests(days=30)
        
        actual_availability = 1 - (failed_requests / total_requests)
        error_budget_remaining = (actual_availability - self.TARGET_AVAILABILITY) / (1 - self.TARGET_AVAILABILITY)
        
        # Alert if budget < 10%
        if error_budget_remaining < 0.1:
            await self.alert_on_call_team(
                "Error budget critically low",
                remaining=error_budget_remaining,
                failed_requests=failed_requests
            )
        
        return {
            'target_availability': self.TARGET_AVAILABILITY,
            'actual_availability': actual_availability,
            'error_budget_remaining': error_budget_remaining,
            'failed_requests': failed_requests,
            'total_requests': total_requests
        }
```

---

## 🧪 6. Testing Guardrails

### **6.1 Property-Based Testing**

**Mandatory Controls:**
- ✅ Test invariants (properties that must always hold)
- ✅ Fuzz testing for inputs
- ✅ 85% minimum code coverage
- ✅ Integration tests for all APIs

**Example:**
```python
# Property-based testing guardrail
from hypothesis import given, strategies as st

@given(st.integers())
def test_rate_limit_never_negative(request_count):
    """Property: Rate limit remaining should never be negative"""
    limiter = RateLimitGuardrail()
    result = limiter.check_rate_limit('user_id', 'endpoint', limit=100)
    assert result['remaining'] >= 0

@given(st.text())
def test_sanitize_logs_removes_pii(text):
    """Property: Sanitized logs should contain no PII"""
    logger = SecureLogger()
    sanitized = logger.sanitize(text)
    
    # Should not contain patterns
    assert not re.search(r'\b\d{3}-\d{2}-\d{4}\b', sanitized)  # SSN
    assert not re.search(r'\b\d{16}\b', sanitized)  # CC
```

---

## 📋 7. Checklist: Pre-Production Guardrails

**Before deploying to production, verify ALL items:**

### Security
- [ ] MFA enabled for admin accounts
- [ ] PASETO tokens implemented (not JWT)
- [ ] TLS 1.3 enforced
- [ ] Secrets in Vault (not code)
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (output encoding)
- [ ] CSRF protection enabled
- [ ] Rate limiting implemented
- [ ] Account lockout after failed attempts

### Privacy & Compliance
- [ ] GDPR compliance (if EU users)
- [ ] Data retention policies defined
- [ ] Audit logging enabled
- [ ] PII encrypted at rest
- [ ] Privacy policy published
- [ ] Cookie consent (if applicable)
- [ ] Data breach response plan

### Operational
- [ ] Health checks (liveness, readiness)
- [ ] Circuit breakers for external calls
- [ ] Timeout on all operations
- [ ] Resource limits enforced
- [ ] Auto-scaling configured
- [ ] Backup and restore tested
- [ ] Disaster recovery plan
- [ ] Monitoring and alerting
- [ ] On-call rotation defined

### AI/ML (if applicable)
- [ ] Content moderation enabled
- [ ] Prompt injection prevention
- [ ] Output validation
- [ ] Cost controls implemented
- [ ] Model versioning
- [ ] A/B testing framework
- [ ] Human-in-the-loop for high-risk decisions

### Testing
- [ ] 85%+ code coverage
- [ ] Property-based tests
- [ ] Load testing completed
- [ ] Security penetration testing
- [ ] Chaos engineering (failure scenarios)

---

**Document Status:** ✅ Complete Universal Guardrails Template

**Version:** 1.0  
**Date:** June 18, 2026

**Usage:** Apply these guardrails to every project before production deployment.
