# Task 2: Scaling Configuration Documentation

## Overview
This document describes the automatic scaling configuration for the PhotoWebApp on OpenShift.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    OpenShift Cluster                         │
│                                                              │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────┐  │
│  │   Frontend   │◄────►│   Backend    │◄────►│  MySQL   │  │
│  │   HPA (1-5)  │      │   HPA (1-5)  │      │  (1)     │  │
│  └──────────────┘      └──────────────┘      └──────────┘  │
│                                                              │
│  Load Balancer → Route → Frontend Service                    │
│  Locust (Cloud) → Backend Service                            │
└─────────────────────────────────────────────────────────────┘
```

## Horizontal Pod Autoscaler (HPA) Configuration

### Frontend HPA (`frontend-hpa`)

| Parameter | Value | Description |
|-----------|-------|-------------|
| **minReplicas** | 1 | Minimum pods running |
| **maxReplicas** | 5 | Maximum pods allowed |
| **Target CPU** | 50% | Average CPU utilization per pod |
| **Scale-up** | +2 pods/30s | Aggressive scaling |
| **Scale-down** | +1 pod/60s | Conservative scaling |

### Backend HPA (`backend-hpa`)

| Parameter | Value | Description |
|-----------|-------|-------------|
| **minReplicas** | 1 | Minimum pods running |
| **maxReplicas** | 5 | Maximum pods allowed |
| **Target CPU** | 50% | Average CPU utilization per pod |
| **Scale-up** | +2 pods/30s | Aggressive scaling |
| **Scale-down** | +1 pod/60s | Conservative scaling |

## Resource Requests and Limits

### Frontend Deployment
```yaml
resources:
  requests:
    cpu: 100m      # 0.1 CPU cores
    memory: 128Mi  # 128 MB
  limits:
    cpu: 200m      # 0.2 CPU cores
    memory: 256Mi  # 256 MB
```

### Backend Deployment
```yaml
resources:
  requests:
    cpu: 100m      # 0.1 CPU cores
    memory: 128Mi  # 128 MB
  limits:
    cpu: 500m      # 0.5 CPU cores
    memory: 512Mi  # 512 MB
```

### MySQL Deployment
```yaml
resources:
  requests:
    cpu: 200m      # 0.2 CPU cores
    memory: 512Mi  # 512 MB
  limits:
    cpu: 500m      # 0.5 CPU cores
    memory: 1Gi    # 1 GB
```

## Scaling Behavior

### Scale-Up (Increasing Replicas)
- **Trigger**: Average CPU > 50% across all pods
- **Rate**: Up to 2 pods added every 30 seconds
- **Stabilization**: No delay (immediate response)
- **Maximum**: 5 replicas total

### Scale-Down (Decreasing Replicas)
- **Trigger**: Average CPU < 50% across all pods
- **Rate**: 1 pod removed every 60 seconds
- **Stabilization**: 60-second window to prevent flapping
- **Minimum**: 1 replica (always running)

## Storage Configuration

### Uploads PVC
- **Access Mode**: `ReadWriteOnce` (RWO)
- **Storage**: 5Gi
- **Note**: For multi-replica file sharing, use `ReadWriteMany` (RWX) with CephFS or NFS

## Deployment Commands

### Apply Configuration
```bash
# Create namespace (if not exists)
oc new-project photowebapp

# Apply secrets and PVCs
oc apply -f openshift/openshift-all.yaml

# Or apply individual components
oc apply -f openshift/hpa.yaml
```

### Verify HPA Status
```bash
# Check HPA status
oc get hpa

# Watch HPA scaling events
oc get hpa -w

# Describe HPA details
oc describe hpa frontend-hpa
oc describe hpa backend-hpa
```

## Monitoring Scaling

### View Replica Counts
```bash
# Frontend replicas
oc get deployment frontend -o jsonpath='{.status.readyReplicas}'

# Backend replicas
oc get deployment backend -o jsonpath='{.status.readyReplicas}'

# All pods
oc get pods -l app=frontend
oc get pods -l app=backend
```

### View HPA Events
```bash
# Recent HPA events
oc get events --field-selector reason=SuccessfulRescale

# HPA events in real-time
oc get events -w | grep "SuccessfulRescale"
```

## Scaling Triggers

### CPU-Based Scaling
The HPA monitors:
1. **Current CPU utilization** per pod
2. **Average utilization** across all replicas
3. **Target utilization** (50%) as threshold

### Formula
```
Desired Replicas = ceil[current replicas × (current CPU / target CPU)]
```

Example:
- Current: 2 replicas
- Current CPU: 80%
- Target CPU: 50%
- Desired: ceil[2 × (80/50)] = ceil[3.2] = 4 replicas

## Cost Considerations

### Resource Usage per Replica
| Component | CPU Request | Memory Request | Daily Cost (est.) |
|-----------|-------------|----------------|-------------------|
| Frontend | 0.1 CPU | 128 MiB | ~$0.05 |
| Backend | 0.1 CPU | 128 MiB | ~$0.05 |
| **Total per replica** | **0.2 CPU** | **256 MiB** | **~$0.10** |

### Maximum Resource Usage (5 replicas)
| Component | CPU Limit | Memory Limit | Daily Cost (est.) |
|-----------|-----------|--------------|-------------------|
| Frontend | 1.0 CPU | 1.25 GiB | ~$0.50 |
| Backend | 2.5 CPU | 2.5 GiB | ~$1.25 |
| **Total** | **3.5 CPU** | **3.75 GiB** | **~$1.75** |

## Troubleshooting

### HPA Not Scaling
```bash
# Check HPA conditions
oc describe hpa frontend-hpa

# Look for:
# - Unable to fetch metrics (check metrics-server)
# - FailedRescale (recent scale failure)
# - FailedGetResourceMetric (missing resource requests)
```

### Pods Not Starting
```bash
# Check pod events
oc describe pod <pod-name>

# Check logs
oc logs <pod-name> -f
```

### Scaling Too Aggressively
Adjust the HPA behavior:
```yaml
behavior:
  scaleUp:
    stabilizationWindowSeconds: 60  # Increase from 0
  scaleDown:
    stabilizationWindowSeconds: 120 # Increase from 60
```

## References

- [OpenShift HPA Documentation](https://docs.openshift.com/container-platform/latest/nodes/autoscaling/autoscaling-scaling-deployments.html)
- [Kubernetes HPA Tutorial](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Metrics Server](https://github.com/kubernetes-sigs/metrics-server)