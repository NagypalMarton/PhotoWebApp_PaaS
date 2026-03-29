# Task 2: Scalable Web Application on OpenShift

This directory contains the configuration and documentation for Task 2 - automatic scaling of the PhotoWebApp on OpenShift.

## Quick Start

### Prerequisites
- OpenShift CLI (`oc`) installed and authenticated
- Project `photowebapp` created
- Metrics Server enabled in cluster

### Deployment
```bash
# Set project
oc project photowebapp

# Apply all configurations (including HPA)
oc apply -f openshift/openshift-all.yaml

# Apply Locust for load testing
oc apply -f locust/locust-openshift.yaml
```

### Running Load Test
```bash
# Get Locust URL
export LOCUST_URL=$(oc get route locust -o jsonpath='{.spec.host}')
echo "Locust UI: https://$LOCUST_URL"

# Or use automated test script
./openshift/task2-test-script.sh
```

## Documentation

| File | Description |
|------|-------------|
| `openshift-all.yaml` | Complete OpenShift configuration with HPA |
| `task2-scaling-config.md` | Detailed scaling configuration |
| `task2-load-test-guide.md` | Step-by-step load testing guide |
| `task2-proof-template.md` | Template for proof of scaling |
| `task2-test-script.sh` | Automated test script |

## Scaling Configuration

### Frontend HPA
- **Min Replicas:** 1
- **Max Replicas:** 5
- **Target CPU:** 50%
- **Scale-up:** +2 pods/30s (no stabilization)
- **Scale-down:** +1 pod/60s (60s stabilization)

### Backend HPA
- **Min Replicas:** 1
- **Max Replicas:** 5
- **Target CPU:** 50%
- **Scale-up:** +2 pods/30s (no stabilization)
- **Scale-down:** +1 pod/60s (60s stabilization)

## Load Test Parameters

| Parameter | Value |
|-----------|-------|
| Users | 20-50 |
| Spawn Rate | 5 users/s |
| Duration | 5-10 minutes |
| Host | http://backend:5001 |

## Test Results Template

See `task2-proof-template.md` for a complete template to document your test results.

## Storage Notes

### Current Configuration
- **Uploads PVC:** ReadWriteOnce (RWO)
- **Limitation:** Files uploaded to one replica won't be accessible from other replicas

### Solution (Optional)
To enable shared file access across all replicas:
1. Use a storage class with ReadWriteMany (RWX) support (CephFS, NFS)
2. Update `uploads-pvc` in `openshift-all.yaml`:
```yaml
accessModes:
  - ReadWriteMany
```

## Monitoring Commands

```bash
# Watch HPA scaling
oc get hpa -w

# Watch pod scaling
oc get pods -l app=frontend -w
oc get pods -l app=backend -w

# Check HPA events
oc get events --field-selector reason=SuccessfulRescale

# View resource usage
oc top pods -l app=frontend
oc top pods -l app=backend
```

## Troubleshooting

### HPA Not Scaling
```bash
# Check HPA conditions
oc describe hpa frontend-hpa

# Check if metrics-server is running
oc get pods -n openshift-monitoring | grep metrics-server
```

### Locust Cannot Connect
```bash
# Check Locust pod
oc get pod -l app=locust

# Check Locust logs
oc logs -l app=locust
```

## Success Criteria

- [ ] Frontend scales from 1 → 5 replicas under load
- [ ] Backend scales from 1 → 5 replicas under load
- [ ] Both scale back down to 1 replica after load stops
- [ ] All API endpoints respond within 2 seconds
- [ ] Error rate < 1%
- [ ] No data corruption or loss

## References

- [OpenShift HPA Documentation](https://docs.openshift.com/container-platform/latest/nodes/autoscaling/autoscaling-scaling-deployments.html)
- [Kubernetes HPA Tutorial](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Locust Documentation](https://docs.locust.io/)