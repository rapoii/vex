---
name: deployment-flow
description: Workflows and best practices for deployment (blue-green, canary, rolling updates, health checks).
argument-hint: "[scope | target]"
metadata:
  origin: VEX
category: workflow
triggers:
  - "deployment strategy"
  - "blue green"
  - "canary release"
  - "deployment-flow"
---

# Deployment Flow

Strategies for deploying applications safely with minimal downtime, including rolling updates, blue-green, and canary deployments.

## When to Activate
- Task involves configuring Kubernetes deployments, ECS services, or CI/CD delivery pipelines.
- Adding health checks to applications.
- Designing zero-downtime deployment architectures.

## How It Works

### Health Checks
Deployments rely on accurate health checks to know when to route traffic to a new instance.

```python
# FastAPI Health Check Example
from fastapi import FastAPI, status

app = FastAPI()

@app.get("/health/liveness", status_code=status.HTTP_200_OK)
def liveness():
    """Checks if the application process is running."""
    return {"status": "alive"}

@app.get("/health/readiness", status_code=status.HTTP_200_OK)
def readiness():
    """Checks if the app is ready to accept traffic (e.g., DB connected)."""
    if not database_is_connected():
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    return {"status": "ready"}
```

### Rolling Updates (Kubernetes)
Replaces old pods with new ones gradually.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1       # How many pods can be created over desired amount
      maxUnavailable: 0 # Ensure no capacity drops during rollout
  template:
    # ... container spec with livenessProbe and readinessProbe ...
```

### Blue-Green Deployment
Maintains two identical environments. Traffic routes to Blue. Deploy to Green, test it, then switch router to Green.

**Mechanism**: Usually handled via Load Balancer rules or Kubernetes Service label selection.
```yaml
# Switch traffic from blue to green by updating the selector
apiVersion: v1
kind: Service
metadata:
  name: my-app-service
spec:
  selector:
    app: my-app
    version: v2.0.0 # Changed from v1.0.0 (blue) to v2.0.0 (green)
```

### Canary Deployment
Routes a small percentage of traffic (e.g., 5%) to the new version to monitor error rates before a full rollout. Often implemented with service meshes (Istio, Linkerd) or AWS API Gateway.

## Verification Steps
1. Test the `/health/readiness` endpoint locally to ensure it returns 200 only when all dependencies are up.
2. In a staging environment, deploy a new version and monitor active connections to ensure zero dropped requests during the rollout.
3. Validate rollback commands: ensure you can revert to the previous version in under 1 minute.

## Common Pitfalls
- **Broken Readiness Probes**: A readiness probe that always returns 200 will cause traffic to be routed to instances that are still booting up.
- **Database Schema Changes**: Blue-green and rolling updates mean two versions of the code run simultaneously. DB changes must be backwards-compatible.
- **Long-lived Connections**: Websockets or long downloads may prevent graceful shutdown. Implement proper `SIGTERM` handling.

## Related Skills
- `migration-workflow`: Ensuring database migrations align with zero-downtime deployment rules.
- `release-workflow`: How artifacts are tagged before deployment.

## Pipeline

**Previous:** [release-workflow](../release-workflow/SKILL.md) — prepare version, changelog, tag, and release artifact
**Next:** [verification-before-completion](../verification-before-completion/SKILL.md) — prove claimed fixes with real evidence before completion