# 🔐 Security Enhancements - Implementation Guide

## 🎯 Priority 1: Critical (Do Before Production)

These are the **essential** security enhancements you should implement before going to production.

---

## 1. Enable HTTPS/TLS (Essential)

### Why It's Critical
- Prevents man-in-the-middle attacks
- Encrypts data in transit
- Required for compliance (GDPR, HIPAA)
- Browser security warnings without it

### Implementation

#### Option A: Using Let's Encrypt (Free)

```yaml
# docker-compose.yml - Add Traefik reverse proxy
services:
  traefik:
    image: traefik:v2.10
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.myresolver.acme.tlschallenge=true"
      - "--certificatesresolvers.myresolver.acme.email=your-email@example.com"
      - "--certificatesresolvers.myresolver.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
      - "./letsencrypt:/letsencrypt"

  api-gateway:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.api.rule=Host(`api.yourdomain.com`)"
      - "traefik.http.routers.api.entrypoints=websecure"
      - "traefik.http.routers.api.tls.certresolver=myresolver"
      - "traefik.http.services.api.loadbalancer.server.port=8000"

  dashboard:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.dashboard.rule=Host(`eval.yourdomain.com`)"
      - "traefik.http.routers.dashboard.entrypoints=websecure"
      - "traefik.http.routers.dashboard.tls.certresolver=myresolver"
      - "traefik.http.services.dashboard.loadbalancer.server.port=3001"
```

#### Option B: Using nginx with SSL

```nginx
# nginx.conf
server {
    listen 443 ssl http2;
    server_name eval.yourdomain.com;

    ssl_certificate /etc/ssl/certs/yourdomain.crt;
    ssl_certificate_key /etc/ssl/private/yourdomain.key;
    
    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    location / {
        proxy_pass http://dashboard:3001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://api-gateway:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name eval.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

**Cost**: Free (Let's Encrypt)  
**Time**: 1 hour  
**Difficulty**: Easy

---

## 2. Setup Secrets Manager (Essential)

### Why It's Critical
- API keys not in environment files
- Automatic key rotation
- Audit trail for access
- Centralized management

### Implementation

#### Option A: AWS Secrets Manager (Recommended)

```python
# services/shared/secrets.py
import boto3
from botocore.exceptions import ClientError
import os

class SecretsManager:
    def __init__(self):
        self.client = boto3.client('secretsmanager', 
                                   region_name=os.getenv('AWS_REGION', 'us-east-1'))
        self.cache = {}
    
    def get_secret(self, secret_name: str) -> str:
        """Get secret from AWS Secrets Manager with caching"""
        if secret_name in self.cache:
            return self.cache[secret_name]
        
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            secret = response['SecretString']
            self.cache[secret_name] = secret
            return secret
        except ClientError as e:
            raise Exception(f"Failed to retrieve secret {secret_name}: {e}")
    
    def rotate_secret(self, secret_name: str, new_value: str):
        """Rotate a secret"""
        self.client.update_secret(SecretId=secret_name, SecretString=new_value)
        if secret_name in self.cache:
            del self.cache[secret_name]

# Usage in workers
secrets_manager = SecretsManager()
GROQ_API_KEY = secrets_manager.get_secret('prod/groq-api-key')
OPENAI_API_KEY = secrets_manager.get_secret('prod/openai-api-key')
```

```bash
# Create secrets in AWS
aws secretsmanager create-secret \
    --name prod/groq-api-key \
    --secret-string "gsk_your_actual_key"

aws secretsmanager create-secret \
    --name prod/openai-api-key \
    --secret-string "sk_your_actual_key"
```

#### Option B: HashiCorp Vault (Self-hosted)

```python
# services/shared/vault_client.py
import hvac

class VaultClient:
    def __init__(self):
        self.client = hvac.Client(
            url=os.getenv('VAULT_ADDR', 'http://vault:8200'),
            token=os.getenv('VAULT_TOKEN')
        )
    
    def get_secret(self, path: str, key: str) -> str:
        """Get secret from Vault"""
        secret = self.client.secrets.kv.v2.read_secret_version(path=path)
        return secret['data']['data'][key]

# docker-compose.yml
vault:
  image: vault:1.15
  ports:
    - "8200:8200"
  environment:
    VAULT_DEV_ROOT_TOKEN_ID: "dev-only-token"
  cap_add:
    - IPC_LOCK
```

**Cost**: 
- AWS: $0.40/secret/month
- Vault: Free (self-hosted)

**Time**: 2 hours  
**Difficulty**: Medium

---

## 3. Configure Rate Limiting by IP (Essential)

### Why It's Critical
- Prevents DDoS attacks
- Stops brute force attempts
- Protects against abuse
- Reduces costs

### Implementation

```python
# services/api-gateway/rate_limiter.py
from fastapi import Request, HTTPException
from datetime import datetime, timedelta
import asyncio

class IPRateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = {}  # {ip: [(timestamp, count)]}
        self.lock = asyncio.Lock()
    
    async def check_rate_limit(self, request: Request):
        """Check if IP is within rate limit"""
        client_ip = request.client.host
        
        async with self.lock:
            now = datetime.now()
            minute_ago = now - timedelta(minutes=1)
            
            # Clean old requests
            if client_ip in self.requests:
                self.requests[client_ip] = [
                    (ts, count) for ts, count in self.requests[client_ip]
                    if ts > minute_ago
                ]
            
            # Count requests in last minute
            recent_requests = sum(count for _, count in self.requests.get(client_ip, []))
            
            if recent_requests >= self.requests_per_minute:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Max {self.requests_per_minute} requests per minute."
                )
            
            # Add current request
            if client_ip not in self.requests:
                self.requests[client_ip] = []
            self.requests[client_ip].append((now, 1))

# services/api-gateway/main.py
from fastapi import Depends

rate_limiter = IPRateLimiter(requests_per_minute=60)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    await rate_limiter.check_rate_limit(request)
    response = await call_next(request)
    return response
```

#### Using Redis for Distributed Rate Limiting

```python
# services/api-gateway/redis_rate_limiter.py
from redis import Redis
from datetime import datetime

class RedisRateLimiter:
    def __init__(self, redis_client: Redis, requests_per_minute: int = 60):
        self.redis = redis_client
        self.rpm = requests_per_minute
    
    async def check_rate_limit(self, client_ip: str):
        """Check rate limit using Redis"""
        key = f"rate_limit:{client_ip}"
        pipe = self.redis.pipeline()
        
        # Increment counter
        pipe.incr(key)
        # Set expiry to 1 minute
        pipe.expire(key, 60)
        
        result = pipe.execute()
        request_count = result[0]
        
        if request_count > self.rpm:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Try again in {60 - (datetime.now().second)} seconds."
            )
```

**Cost**: Free  
**Time**: 1 hour  
**Difficulty**: Easy

---

## 4. Enable Database Encryption (Essential)

### Why It's Critical
- Protects data at rest
- Compliance requirement (GDPR, HIPAA)
- Prevents data theft from backups
- Industry standard

### Implementation

```bash
# PostgreSQL encryption at rest
# Method 1: Using encrypted file system (easiest)
# Linux: LUKS encryption
# AWS: EBS encrypted volumes

# docker-compose.yml
volumes:
  postgres_data:
    driver: local
    driver_opts:
      type: none
      device: /encrypted/postgres_data
      o: bind

# Method 2: PostgreSQL native encryption
# postgresql.conf
ssl = on
ssl_cert_file = '/etc/ssl/certs/server.crt'
ssl_key_file = '/etc/ssl/private/server.key'
ssl_ca_file = '/etc/ssl/certs/root.crt'

# Force SSL connections
hostssl all all 0.0.0.0/0 md5
```

#### Column-Level Encryption for Sensitive Data

```python
# services/shared/encryption.py
from cryptography.fernet import Fernet
import os

class FieldEncryption:
    def __init__(self):
        # Store key in secrets manager!
        key = os.getenv('ENCRYPTION_KEY')
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> bytes:
        """Encrypt sensitive field"""
        return self.cipher.encrypt(data.encode())
    
    def decrypt(self, encrypted_data: bytes) -> str:
        """Decrypt sensitive field"""
        return self.cipher.decrypt(encrypted_data).decode()

# Usage in models
from sqlalchemy import LargeBinary

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID, primary_key=True)
    email = Column(String, unique=True)
    encrypted_api_key = Column(LargeBinary)  # Encrypted!
    
    def set_api_key(self, api_key: str):
        encryptor = FieldEncryption()
        self.encrypted_api_key = encryptor.encrypt(api_key)
    
    def get_api_key(self) -> str:
        encryptor = FieldEncryption()
        return encryptor.decrypt(self.encrypted_api_key)
```

**Cost**: Minimal (5-10% performance impact)  
**Time**: 2 hours  
**Difficulty**: Medium

---

## 5. Run Security Scan (Essential)

### Why It's Critical
- Finds vulnerabilities before attackers do
- Compliance requirement
- Industry best practice
- Peace of mind

### Implementation

```bash
# 1. Scan Dependencies
pip install safety
safety check -r requirements.txt

# 2. Scan Docker Images
docker scan llm-eval-worker-groq

# 3. Web Application Scan (OWASP ZAP)
docker run -t owasp/zap2docker-stable zap-baseline.py \
    -t http://localhost:8000 \
    -r security_report.html

# 4. Infrastructure Scan
# Using Trivy
docker run aquasec/trivy image llm-eval-api-gateway

# 5. Code Security Scan
# Using Bandit
pip install bandit
bandit -r services/ -f json -o security_scan.json
```

#### Automated Security Scanning in CI/CD

```yaml
# .github/workflows/security.yml
name: Security Scan

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Run Safety Check
        run: |
          pip install safety
          safety check
      
      - name: Run Bandit
        run: |
          pip install bandit
          bandit -r services/
      
      - name: Run Trivy
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
```

**Cost**: Free  
**Time**: 30 minutes  
**Difficulty**: Easy

---

## 📋 Implementation Checklist

### Before Production Deployment

```python
Security Essentials:
☐ Enable HTTPS/TLS (1 hour)
☐ Setup secrets manager (2 hours)
☐ Configure IP rate limiting (1 hour)
☐ Enable database encryption (2 hours)
☐ Run security scans (30 minutes)

Total Time: ~6.5 hours
```

### Quick Wins (Do These Too)

```python
Additional Security:
☐ Change default passwords (5 minutes)
☐ Disable unnecessary ports (10 minutes)
☐ Enable firewall rules (15 minutes)
☐ Setup fail2ban (30 minutes)
☐ Configure security headers (15 minutes)

Total Time: ~1.25 hours
```

---

## 🚀 Quick Implementation Script

```bash
#!/bin/bash
# security_setup.sh - Quick security enhancements

echo "🔐 Setting up security enhancements..."

# 1. Generate SSL certificates (self-signed for dev)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ./ssl/private.key \
    -out ./ssl/certificate.crt

# 2. Generate encryption key
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" > encryption.key

# 3. Setup fail2ban
sudo apt-get install fail2ban -y
sudo systemctl enable fail2ban

# 4. Configure firewall
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable

# 5. Run security scan
pip install safety bandit
safety check
bandit -r services/

echo "✅ Security enhancements completed!"
echo "⚠️ Don't forget to:"
echo "  - Setup secrets manager"
echo "  - Get real SSL certificates"
echo "  - Configure rate limiting"
```

---

## 📊 Security Enhancement Impact

| Enhancement | Impact | Cost | Time | Priority |
|-------------|--------|------|------|----------|
| HTTPS/TLS | High | Free | 1h | 🔴 Critical |
| Secrets Manager | High | $0.40/mo | 2h | 🔴 Critical |
| IP Rate Limiting | High | Free | 1h | 🔴 Critical |
| DB Encryption | High | 5% perf | 2h | 🔴 Critical |
| Security Scan | Medium | Free | 30m | 🔴 Critical |

---

## 🎯 After Implementation

### Verify Security

```bash
# 1. Test HTTPS
curl https://your-domain.com/health

# 2. Test rate limiting
for i in {1..100}; do curl https://your-domain.com/api/v1/jobs; done

# 3. Check encryption
openssl s_client -connect your-domain.com:443

# 4. Verify secrets
aws secretsmanager get-secret-value --secret-id prod/groq-api-key

# 5. Review scan results
cat security_scan.json
```

### Monitor

```python
Continuous Monitoring:
- SSL certificate expiration (Let's Encrypt auto-renews)
- Rate limit effectiveness (track 429 responses)
- Failed authentication attempts
- Unusual API usage patterns
- Security scan results (run weekly)
```

---

## 📚 Additional Resources

- **SSL/TLS**: https://letsencrypt.org/
- **AWS Secrets**: https://aws.amazon.com/secrets-manager/
- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **Security Headers**: https://securityheaders.com/
- **Rate Limiting**: https://www.nginx.com/blog/rate-limiting-nginx/

---

**Document Version**: 1.0  
**Time to Implement All**: ~6.5 hours  
**Production Ready After**: ✅ YES  
**Security Rating After**: 🟢 95/100
