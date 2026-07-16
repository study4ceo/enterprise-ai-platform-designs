# Kubernetes Deployment Files

This directory contains all Kubernetes manifests needed to deploy the AI SRE Stack to a Kubernetes cluster.

## Files Overview

| File | Purpose |
|------|---------|
| `namespace.yaml` | Creates the ai-sre-stack namespace |
| `secrets.yaml` | Stores sensitive credentials (API keys, tokens) |
| `configmap.yaml` | Stores non-sensitive configuration |
| `rbac.yaml` | ServiceAccount, ClusterRole, and RoleBinding |
| `pvc.yaml` | PersistentVolumeClaims for audit logs |
| `deployment.yaml` | Main orchestrator deployment |
| `service.yaml` | Service for metrics/webhooks (optional) |
| `hpa.yaml` | HorizontalPodAutoscaler (optional) |
| `networkpolicy.yaml` | Network policies (optional) |

---

## Quick Start

### Prerequisites

1. **Kubernetes cluster** (1.20+)
   - EKS, AKS, GKE, or self-hosted
   - kubectl configured and connected

2. **Required credentials**:
   - Anthropic API key (required)
   - Cloud provider credentials (AWS/Azure/GCP)
   - Service API keys (Datadog, PagerDuty, Slack, etc.)

3. **Docker image** (build and push):
   ```bash
   docker build -t your-registry/ai-sre-stack:latest .
   docker push your-registry/ai-sre-stack:latest
   ```

---

## Deployment Steps

### Step 1: Create Namespace

```bash
kubectl apply -f namespace.yaml
```

**Verify**:
```bash
kubectl get namespace ai-sre-stack
```

---

### Step 2: Configure Secrets

⚠️ **IMPORTANT**: Never commit actual secrets to git!

**Option A: Manual secrets (for testing)**

Edit `secrets.yaml` and replace placeholder values:
```bash
# Edit the file
nano secrets.yaml

# Apply
kubectl apply -f secrets.yaml
```

**Option B: Sealed Secrets (recommended for production)**

```bash
# Install sealed-secrets controller
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml

# Create and seal secret
kubectl create secret generic ai-sre-secrets \
  --namespace=ai-sre-stack \
  --from-literal=ANTHROPIC_API_KEY=your-actual-key \
  --from-literal=AWS_ACCESS_KEY_ID=your-aws-key \
  --from-literal=AWS_SECRET_ACCESS_KEY=your-aws-secret \
  --from-literal=SLACK_BOT_TOKEN=your-slack-token \
  --dry-run=client -o yaml | \
kubeseal -o yaml > sealed-secrets.yaml

# Apply sealed secret
kubectl apply -f sealed-secrets.yaml
```

**Option C: External Secrets Operator**

See: https://external-secrets.io/

**Option D: Cloud Provider Secrets**

- AWS: Use AWS Secrets Manager + CSI driver
- Azure: Use Azure Key Vault + CSI driver
- GCP: Use Secret Manager + CSI driver

**Verify secrets**:
```bash
kubectl get secrets -n ai-sre-stack
```

---

### Step 3: Configure Settings

Edit `configmap.yaml` to adjust settings:

```bash
nano configmap.yaml
```

Key settings to review:
- `DRY_RUN`: Set to "false" for production
- `AUTO_REMEDIATION`: Set to "true" or "false"
- `OBSERVATION_INTERVAL`: Seconds between cycles (default: 60)
- Security controls: All enabled by default
- MCP server settings: Adjust as needed

Apply:
```bash
kubectl apply -f configmap.yaml
```

**Verify**:
```bash
kubectl get configmap ai-sre-config -n ai-sre-stack -o yaml
```

---

### Step 4: Set Up RBAC

```bash
kubectl apply -f rbac.yaml
```

This creates:
- ServiceAccount: `ai-sre-sa`
- ClusterRole: `ai-sre-role` (read pods, scale deployments, etc.)
- ClusterRoleBinding: Binds role to service account

**Verify**:
```bash
kubectl get serviceaccount ai-sre-sa -n ai-sre-stack
kubectl get clusterrole ai-sre-role
kubectl get clusterrolebinding ai-sre-binding
```

---

### Step 5: Create Storage

```bash
kubectl apply -f pvc.yaml
```

This creates:
- `audit-logs-pvc`: 10Gi for audit logs
- `runbooks-pvc`: 1Gi for runbooks (optional)

**Verify**:
```bash
kubectl get pvc -n ai-sre-stack
```

---

### Step 6: Update Deployment Image

Edit `deployment.yaml` and set your image:

```yaml
image: your-registry/ai-sre-stack:latest
```

Or use `sed`:
```bash
sed -i 's|your-registry/ai-sre-stack:latest|myregistry.azurecr.io/ai-sre-stack:v1.0|g' deployment.yaml
```

---

### Step 7: Deploy Application

```bash
kubectl apply -f deployment.yaml
```

**Verify deployment**:
```bash
# Check deployment status
kubectl get deployment ai-sre-orchestrator -n ai-sre-stack

# Check pods
kubectl get pods -n ai-sre-stack

# View logs
kubectl logs -f deployment/ai-sre-orchestrator -n ai-sre-stack
```

---

### Step 8: Optional - Create Service

Only needed if exposing metrics or webhooks:

```bash
kubectl apply -f service.yaml
```

---

## Verification

### Check All Resources

```bash
kubectl get all -n ai-sre-stack
```

Expected output:
```
NAME                                       READY   STATUS    RESTARTS   AGE
pod/ai-sre-orchestrator-xxxxxxxxxx-xxxxx   1/1     Running   0          2m

NAME                                  READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/ai-sre-orchestrator   1/1     1            1           2m

NAME                                             DESIRED   CURRENT   READY   AGE
replicaset.apps/ai-sre-orchestrator-xxxxxxxxxx   1         1         1       2m
```

### Check Logs

```bash
# Follow logs
kubectl logs -f deployment/ai-sre-orchestrator -n ai-sre-stack

# Last 100 lines
kubectl logs deployment/ai-sre-orchestrator -n ai-sre-stack --tail=100

# Logs from specific pod
kubectl logs pod/ai-sre-orchestrator-xxx -n ai-sre-stack
```

Expected log output:
```
Initializing AI SRE Stack...
✓ Action whitelist enabled
✓ Rate limiting enabled
✓ Audit logging enabled
✓ Approval workflow enabled
✓ Kubernetes MCP initialized
✓ Slack MCP initialized
Initialized 2/12 MCP servers

============================================================
Starting new SRE cycle...
============================================================
=== OBSERVE PHASE ===
📊 kubernetes: healthy
...
```

### Check Audit Logs

```bash
# Access pod and view audit logs
kubectl exec -it deployment/ai-sre-orchestrator -n ai-sre-stack -- bash
cat /app/logs/audit.jsonl | tail -10
```

---

## Management

### View Status

```bash
# Overall status
kubectl get all -n ai-sre-stack

# Detailed pod info
kubectl describe pod -l app=ai-sre-orchestrator -n ai-sre-stack

# Events
kubectl get events -n ai-sre-stack --sort-by='.lastTimestamp'
```

### Update Configuration

```bash
# Edit ConfigMap
kubectl edit configmap ai-sre-config -n ai-sre-stack

# Restart to pick up changes
kubectl rollout restart deployment/ai-sre-orchestrator -n ai-sre-stack
```

### Update Secrets

```bash
# Edit secrets
kubectl edit secret ai-sre-secrets -n ai-sre-stack

# Restart to pick up changes
kubectl rollout restart deployment/ai-sre-orchestrator -n ai-sre-stack
```

### Scale

```bash
# Scale up (requires leader election implementation)
kubectl scale deployment ai-sre-orchestrator -n ai-sre-stack --replicas=3

# Scale down
kubectl scale deployment ai-sre-orchestrator -n ai-sre-stack --replicas=1
```

### Rolling Update

```bash
# Update image
kubectl set image deployment/ai-sre-orchestrator \
  orchestrator=your-registry/ai-sre-stack:v1.1 \
  -n ai-sre-stack

# Check rollout status
kubectl rollout status deployment/ai-sre-orchestrator -n ai-sre-stack

# Rollback if needed
kubectl rollout undo deployment/ai-sre-orchestrator -n ai-sre-stack
```

---

## Troubleshooting

### Pod Not Starting

```bash
# Check pod status
kubectl describe pod -l app=ai-sre-orchestrator -n ai-sre-stack

# Common issues:
# - ImagePullBackOff: Check image name and registry credentials
# - CrashLoopBackOff: Check logs for errors
# - Pending: Check PVC status and node resources
```

### Missing Secrets

```bash
# Verify secrets exist
kubectl get secrets ai-sre-secrets -n ai-sre-stack

# Check secret values (be careful!)
kubectl get secret ai-sre-secrets -n ai-sre-stack -o yaml
```

### Permission Errors

```bash
# Check service account
kubectl get serviceaccount ai-sre-sa -n ai-sre-stack

# Check RBAC bindings
kubectl describe clusterrolebinding ai-sre-binding

# Test permissions
kubectl auth can-i list pods --as=system:serviceaccount:ai-sre-stack:ai-sre-sa
```

### Storage Issues

```bash
# Check PVC status
kubectl get pvc -n ai-sre-stack
kubectl describe pvc audit-logs-pvc -n ai-sre-stack

# Check if bound
# Status should be "Bound", not "Pending"
```

### Network Issues

```bash
# Test connectivity from pod
kubectl exec -it deployment/ai-sre-orchestrator -n ai-sre-stack -- bash

# Inside pod:
curl https://api.anthropic.com
curl https://slack.com
```

---

## Security Best Practices

### 1. Use Sealed Secrets or External Secrets

Don't store secrets in plain YAML files!

### 2. Limit RBAC Permissions

Review and minimize permissions in `rbac.yaml`.

### 3. Enable Network Policies

Apply `networkpolicy.yaml` to restrict traffic.

### 4. Run as Non-Root

Already configured in `deployment.yaml`:
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
```

### 5. Enable Audit Logging

Already enabled via security controls.

### 6. Use Pod Security Standards

```bash
kubectl label namespace ai-sre-stack \
  pod-security.kubernetes.io/enforce=restricted
```

---

## Monitoring

### Prometheus Integration

The deployment includes Prometheus annotations:

```yaml
annotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "8080"
```

### Logs

Forward logs to your logging system:
- Fluentd
- Logstash
- CloudWatch (EKS)
- Stackdriver (GKE)

### Metrics

Expose custom metrics on port 8080 or 9090.

---

## Cleanup

### Delete Everything

```bash
# Delete all resources
kubectl delete -f .

# Or delete namespace (removes everything)
kubectl delete namespace ai-sre-stack
```

### Keep Audit Logs

Before deleting, backup audit logs:

```bash
# Copy logs from pod
kubectl cp ai-sre-stack/ai-sre-orchestrator-xxx:/app/logs ./backup-logs

# Or from PVC
kubectl run busybox --image=busybox -n ai-sre-stack --rm -it -- sh
# Inside container:
cp -r /app/logs /backup
```

---

## Advanced

### Multi-Cluster Deployment

Deploy to multiple clusters:

```bash
# Cluster 1 (production)
kubectl apply -f . --context=prod-cluster

# Cluster 2 (staging)
kubectl apply -f . --context=staging-cluster
```

### Custom Storage Class

Edit `pvc.yaml`:
```yaml
storageClassName: my-custom-storage-class
```

### Resource Quotas

```bash
# Set namespace quotas
kubectl create quota ai-sre-quota \
  --hard=cpu=4,memory=8Gi,pods=10 \
  -n ai-sre-stack
```

---

## Getting Help

- Check logs: `kubectl logs`
- Check events: `kubectl get events`
- Describe resources: `kubectl describe`
- Main docs: `../DEPLOYMENT_GUIDE.md`
- Testing: `../QUICK_TEST_INSTRUCTIONS.md`

---

## Files Summary

```
k8s/
├── namespace.yaml       # Create ai-sre-stack namespace
├── secrets.yaml         # Store API keys and tokens
├── configmap.yaml       # Store configuration
├── rbac.yaml           # ServiceAccount and permissions
├── pvc.yaml            # Storage for audit logs
├── deployment.yaml     # Main application deployment
├── service.yaml        # Service (optional)
└── README.md          # This file
```

---

**You're all set!** Deploy with: `kubectl apply -f k8s/`
