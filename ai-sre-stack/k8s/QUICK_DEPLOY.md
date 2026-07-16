# Kubernetes Quick Deploy Guide

Deploy the AI SRE Stack to Kubernetes in 10 minutes.

---

## Prerequisites (5 minutes)

### 1. Kubernetes Cluster
You need a running Kubernetes cluster:
- **AWS**: EKS
- **Azure**: AKS  
- **Google Cloud**: GKE
- **Local**: Minikube, Kind, Docker Desktop
- **On-premise**: Self-hosted

### 2. Tools Installed
```bash
# Check kubectl
kubectl version --client

# Check cluster connection
kubectl cluster-info
```

### 3. Docker Image
Build and push your image:
```bash
# From project root
cd ..

# Build
docker build -t your-registry/ai-sre-stack:latest .

# Push
docker push your-registry/ai-sre-stack:latest
```

---

## Quick Deploy (5 minutes)

### Option A: Automated Script

```bash
# Make script executable
chmod +x deploy.sh

# Set your image registry
export IMAGE_REGISTRY="your-registry"
export IMAGE_NAME="ai-sre-stack"
export IMAGE_TAG="latest"

# Run deployment script
./deploy.sh
```

The script will guide you through all steps.

---

### Option B: Manual Steps

#### Step 1: Create Namespace
```bash
kubectl apply -f namespace.yaml
```

#### Step 2: Configure Secrets

**⚠️ IMPORTANT**: Replace placeholder values!

```bash
# Edit secrets
nano secrets.yaml

# Apply (or use Sealed Secrets for production)
kubectl apply -f secrets.yaml
```

**Minimum required secret**:
- `ANTHROPIC_API_KEY`

#### Step 3: Apply Configuration
```bash
kubectl apply -f configmap.yaml
kubectl apply -f rbac.yaml
kubectl apply -f pvc.yaml
```

#### Step 4: Update Image in Deployment

Edit `deployment.yaml`:
```yaml
image: your-registry/ai-sre-stack:latest
```

Or use sed:
```bash
sed -i 's|your-registry/ai-sre-stack:latest|myregistry.io/ai-sre-stack:v1.0|g' deployment.yaml
```

#### Step 5: Deploy
```bash
kubectl apply -f deployment.yaml
```

#### Step 6: Verify
```bash
# Check pods
kubectl get pods -n ai-sre-stack

# Check logs
kubectl logs -f deployment/ai-sre-orchestrator -n ai-sre-stack
```

---

## Verification

### Expected Output

```bash
$ kubectl get all -n ai-sre-stack

NAME                                       READY   STATUS    RESTARTS   AGE
pod/ai-sre-orchestrator-xxxxxxxxxx-xxxxx   1/1     Running   0          2m

NAME                                  READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/ai-sre-orchestrator   1/1     1            1           2m
```

### Check Logs

```bash
kubectl logs deployment/ai-sre-orchestrator -n ai-sre-stack
```

**Expected log output**:
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
=== OBSERVE PHASE ===
📊 kubernetes: healthy
```

---

## Common Issues

### ImagePullBackOff

**Problem**: Cannot pull Docker image

**Solution**:
1. Check image name in `deployment.yaml`
2. Verify registry credentials
3. For private registries, create imagePullSecret:

```bash
kubectl create secret docker-registry regcred \
  --docker-server=your-registry \
  --docker-username=your-username \
  --docker-password=your-password \
  -n ai-sre-stack

# Add to deployment.yaml:
# imagePullSecrets:
# - name: regcred
```

---

### CrashLoopBackOff

**Problem**: Pod keeps restarting

**Solution**:
```bash
# Check logs
kubectl logs pod/ai-sre-orchestrator-xxx -n ai-sre-stack

# Common causes:
# - Missing ANTHROPIC_API_KEY
# - Invalid configuration
# - Python import errors
```

---

### PVC Pending

**Problem**: PersistentVolumeClaim stuck in Pending

**Solution**:
```bash
# Check PVC
kubectl describe pvc audit-logs-pvc -n ai-sre-stack

# Common causes:
# - No storage class available
# - Insufficient storage
# - Node selector mismatch

# Fix: Specify storage class in pvc.yaml
# storageClassName: standard  # or gp2, gp3, etc.
```

---

## Management Commands

### View Logs
```bash
# Follow logs
kubectl logs -f deployment/ai-sre-orchestrator -n ai-sre-stack

# Last 100 lines
kubectl logs deployment/ai-sre-orchestrator -n ai-sre-stack --tail=100

# Previous pod (if crashed)
kubectl logs deployment/ai-sre-orchestrator -n ai-sre-stack --previous
```

### Update Configuration
```bash
# Edit ConfigMap
kubectl edit configmap ai-sre-config -n ai-sre-stack

# Restart to apply
kubectl rollout restart deployment/ai-sre-orchestrator -n ai-sre-stack
```

### Update Secrets
```bash
# Edit secrets
kubectl edit secret ai-sre-secrets -n ai-sre-stack

# Restart to apply
kubectl rollout restart deployment/ai-sre-orchestrator -n ai-sre-stack
```

### Scale
```bash
# Scale up (requires leader election)
kubectl scale deployment ai-sre-orchestrator -n ai-sre-stack --replicas=3

# Scale down
kubectl scale deployment ai-sre-orchestrator -n ai-sre-stack --replicas=1
```

### Update Image
```bash
# Set new image
kubectl set image deployment/ai-sre-orchestrator \
  orchestrator=your-registry/ai-sre-stack:v1.1 \
  -n ai-sre-stack

# Check rollout
kubectl rollout status deployment/ai-sre-orchestrator -n ai-sre-stack

# Rollback if needed
kubectl rollout undo deployment/ai-sre-orchestrator -n ai-sre-stack
```

---

## Testing

### Access Pod Shell
```bash
kubectl exec -it deployment/ai-sre-orchestrator -n ai-sre-stack -- bash
```

### View Audit Logs
```bash
kubectl exec deployment/ai-sre-orchestrator -n ai-sre-stack -- cat /app/logs/audit.jsonl | tail -20
```

### Test Connectivity
```bash
kubectl exec -it deployment/ai-sre-orchestrator -n ai-sre-stack -- bash

# Inside pod:
curl https://api.anthropic.com
curl https://slack.com
python -c "import anthropic; print('OK')"
```

---

## Cleanup

### Delete Everything
```bash
# Delete all resources
kubectl delete -f .

# Or delete namespace (removes everything)
kubectl delete namespace ai-sre-stack
```

### Backup Audit Logs First
```bash
# Copy logs before deleting
kubectl cp ai-sre-stack/ai-sre-orchestrator-xxx:/app/logs ./backup-logs
```

---

## Next Steps

After successful deployment:

1. **Monitor logs** for first cycle completion
2. **Verify MCP servers** are initializing correctly
3. **Check audit logs** are being written
4. **Test security controls** are working
5. **Configure monitoring** (Prometheus/Grafana)
6. **Set up alerts** for pod failures
7. **Review** RBAC permissions
8. **Enable** network policies (optional)

---

## Quick Reference

```bash
# Status
kubectl get all -n ai-sre-stack

# Logs
kubectl logs -f deployment/ai-sre-orchestrator -n ai-sre-stack

# Describe
kubectl describe pod -l app=ai-sre-orchestrator -n ai-sre-stack

# Events
kubectl get events -n ai-sre-stack --sort-by='.lastTimestamp'

# Restart
kubectl rollout restart deployment/ai-sre-orchestrator -n ai-sre-stack

# Delete
kubectl delete namespace ai-sre-stack
```

---

## Documentation

- **Full guide**: `README.md` (in this directory)
- **Deployment options**: `../DEPLOYMENT_GUIDE.md`
- **Testing**: `../QUICK_TEST_INSTRUCTIONS.md`
- **Security**: `../SECURITY_HARDENING_GUIDE.md`

---

## Support

**Stuck?** Check:
1. Pod status: `kubectl get pods -n ai-sre-stack`
2. Pod logs: `kubectl logs -f deployment/ai-sre-orchestrator -n ai-sre-stack`
3. Events: `kubectl get events -n ai-sre-stack`
4. Secrets: `kubectl get secrets -n ai-sre-stack`
5. PVCs: `kubectl get pvc -n ai-sre-stack`

---

**Deployment Time**: ~10 minutes  
**Status**: ✅ Production Ready  
**Scale**: Starts with 1 replica, scale as needed
