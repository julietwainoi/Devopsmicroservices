# ArgoCD RBAC Setup

## Your GitOps Architecture (The Right Way!)

```
┌─────────────────────────────────────────────────────────────┐
│                    DEVELOPER WORKFLOW                        │
└─────────────────────────────────────────────────────────────┘
        │
        │ git push
        ▼
┌─────────────────────────────────────────────────────────────┐
│                      GITHUB REPOSITORY                       │
│  - microservices code                                        │
│  - Dockerfiles                                               │
│  - Helm charts (my-app/)                                     │
│  - K8s manifests (k8s/, monitoring/)                         │
└─────────────────────────────────────────────────────────────┘
        │
        │ webhook trigger
        ▼
┌─────────────────────────────────────────────────────────────┐
│                     GITHUB ACTIONS (CI)                      │
│  ✓ Run tests                                                 │
│  ✓ Build Docker images                                       │
│  ✓ Push to ghcr.io                                           │
│  ✓ Update my-app/values.yaml with new image tags            │
│  ✓ Commit & push updated values.yaml                        │
│                                                              │
│  ✗ NO kubectl access needed                                 │
│  ✗ NO cluster credentials                                   │
└─────────────────────────────────────────────────────────────┘
        │
        │ push to repo
        ▼
┌─────────────────────────────────────────────────────────────┐
│                      GITHUB REPOSITORY                       │
│  (now has updated image tags in values.yaml)                │
└─────────────────────────────────────────────────────────────┘
        │
        │ ArgoCD polls every 3 min (or webhook)
        ▼
┌─────────────────────────────────────────────────────────────┐
│                    ARGOCD (CD - IN CLUSTER)                  │
│  ✓ Watches Git repo                                          │
│  ✓ Detects changes in values.yaml                           │
│  ✓ Syncs state to cluster                                   │
│  ✓ Creates/updates deployments                              │
│  ✓ Self-heals if manual changes                             │
│                                                              │
│  Role: ClusterRole (needs access to all namespaces)         │
└─────────────────────────────────────────────────────────────┘
        │
        │ kubectl apply
        ▼
┌─────────────────────────────────────────────────────────────┐
│                    KUBERNETES CLUSTER                        │
│  Namespace: default                                          │
│    ├── user-service                                          │
│    ├── order-service                                         │
│    ├── payment-service                                       │
│    ├── product-service                                       │
│    └── auth-service                                          │
│                                                              │
│  Namespace: monitoring                                       │
│    ├── Prometheus                                            │
│    ├── Grafana                                               │
│    ├── Loki                                                  │
│    └── Promtail                                              │
│                                                              │
│  Namespace: argocd                                           │
│    └── ArgoCD                                                │
└─────────────────────────────────────────────────────────────┘
```

## Who Needs What Permissions?

### ❌ GitHub Actions: NO Kubernetes Permissions
**Why?** It doesn't interact with the cluster at all.

**What it needs:**
- Git commit/push permissions ✓ (already has)
- Docker registry push ✓ (already has)
- No kubectl, no RBAC needed ✓

### ✅ ArgoCD: ClusterRole (Full Deployment Permissions)
**Why?** It needs to deploy resources across multiple namespaces.

**What it needs:**
- Create/update/delete deployments
- Manage services, configmaps, secrets
- Create namespaces
- Manage RBAC for deployed apps
- Read cluster state

## ArgoCD Permissions Breakdown

### ArgoCD Application Controller (The Deployer)
```yaml
ServiceAccount: argocd-application-controller
Role: ClusterRole (full access)
Purpose: Actually deploys your apps to the cluster

Permissions:
- Create/update/delete deployments, services, etc.
- Manage ConfigMaps and Secrets
- Create namespaces
- Set up RBAC for applications
```

### ArgoCD Server (The UI/API)
```yaml
ServiceAccount: argocd-server
Role: ClusterRole (mostly read-only)
Purpose: Shows you what's deployed in the UI

Permissions:
- Read all resources (for UI display)
- Manage ArgoCD Applications
```

## Your Deployed Applications' Permissions

These are the ServiceAccounts we created earlier:

```yaml
# Each microservice runs with limited Role
user-service → user-service-sa → Role (config-reader)
order-service → order-service-sa → Role (resource-manager)
payment-service → payment-service-sa → Role (config-reader)
product-service → product-service-sa → Role (config-reader)
auth-service → auth-service-sa → Role (config-reader)

# Monitoring uses ClusterRole
prometheus → prometheus-sa → ClusterRole (metrics-reader)
grafana → grafana-sa → ClusterRole (metrics-reader)
```

## Setup Instructions

### Option 1: ArgoCD Already Configured (Most Likely)
ArgoCD typically sets up its own RBAC when installed. Check:

```bash
# Check if ArgoCD already has permissions
kubectl get clusterrole | grep argocd
kubectl get clusterrolebinding | grep argocd

# If you see argocd-application-controller and argocd-server, you're good!
```

### Option 2: Manual Setup (If Needed)
```bash
# Only apply if ArgoCD doesn't have permissions
kubectl apply -f k8s/rbac-argocd.yaml
```

## Verify ArgoCD Permissions

```bash
# Check if ArgoCD can deploy
kubectl auth can-i create deployments \
  --as=system:serviceaccount:argocd:argocd-application-controller

# Check if ArgoCD can manage all namespaces
kubectl auth can-i create namespace \
  --as=system:serviceaccount:argocd:argocd-application-controller

# List all permissions
kubectl auth can-i --list \
  --as=system:serviceaccount:argocd:argocd-application-controller
```

## Your Complete RBAC Setup

```
┌────────────────────────────────────────────────────────┐
│ GITHUB ACTIONS                                         │
│ Role: NONE                                             │
│ Why: Doesn't touch cluster                            │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│ ARGOCD APPLICATION CONTROLLER                          │
│ Role: ClusterRole (full deployment access)            │
│ Why: Deploys to default, monitoring, other namespaces │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│ ARGOCD SERVER                                          │
│ Role: ClusterRole (read-only + ArgoCD management)     │
│ Why: Shows resources in UI                            │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│ YOUR MICROSERVICES (deployed by ArgoCD)               │
│ user-service-sa     → Role (config-reader)            │
│ order-service-sa    → Role (resource-manager)         │
│ payment-service-sa  → Role (config-reader)            │
│ product-service-sa  → Role (config-reader)            │
│ auth-service-sa     → Role (config+pod reader)        │
│                                                        │
│ Why: Each service has minimal permissions needed      │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│ MONITORING STACK (deployed by ArgoCD)                 │
│ prometheus-sa → ClusterRole (cluster metrics reader)  │
│ grafana-sa    → ClusterRole (cluster metrics reader)  │
│                                                        │
│ Why: Needs to monitor ALL namespaces                  │
└────────────────────────────────────────────────────────┘
```

## Benefits of This Architecture

### ✅ Security
- No cluster credentials in GitHub
- ArgoCD runs inside cluster (more secure)
- Audit trail in Git

### ✅ Separation of Concerns
- GitHub Actions = Build & Test (CI)
- ArgoCD = Deploy (CD)
- Clean separation

### ✅ GitOps Principles
- Git is single source of truth
- Declarative configuration
- Easy rollback (just revert Git commit)

### ✅ Self-Healing
- ArgoCD automatically fixes manual changes
- Keeps cluster in sync with Git

## Common Mistakes to Avoid

### ❌ DON'T: Give GitHub Actions kubectl access
```yaml
# BAD - Don't do this!
- name: Deploy with kubectl
  run: kubectl apply -f k8s/
```
**Why?** Breaks GitOps, needs cluster credentials in GitHub

### ✅ DO: Let ArgoCD handle deployment
```yaml
# GOOD - What you're already doing
- name: Update values.yaml
  run: sed -i "s|image:.*|image: new-tag|" values.yaml
- name: Commit changes
  run: git commit && git push
```
**Why?** ArgoCD detects change and deploys automatically

## Troubleshooting

### ArgoCD App Shows "OutOfSync"
```bash
# Check what ArgoCD sees
kubectl get application -n argocd

# Force sync
kubectl patch application microservices -n argocd \
  --type merge -p '{"operation":{"sync":{}}}'
```

### ArgoCD Can't Create Resources
```bash
# Check permissions
kubectl auth can-i create deployments \
  --as=system:serviceaccount:argocd:argocd-application-controller \
  --namespace default

# If "no", apply RBAC
kubectl apply -f k8s/rbac-argocd.yaml
```

### Your Apps Can't Access ConfigMaps
```bash
# Check app ServiceAccount permissions
kubectl auth can-i get configmaps \
  --as=system:serviceaccount:default:user-service-sa

# If "no", apply app RBAC
kubectl apply -f k8s/rbac-serviceaccounts.yaml
kubectl apply -f k8s/rbac-roles.yaml
kubectl apply -f k8s/rbac-rolebindings.yaml
```

## Summary

**Your current setup is perfect GitOps!**

- ✓ GitHub Actions builds images and updates Git
- ✓ ArgoCD watches Git and deploys to cluster
- ✓ No cluster credentials needed in GitHub
- ✓ Git is the single source of truth

**The only RBAC you need:**
1. ArgoCD → ClusterRole (to deploy everything)
2. Your microservices → Role (minimal permissions)
3. Monitoring → ClusterRole (to monitor everything)

**You do NOT need:**
- ❌ GitHub Actions RBAC (it doesn't touch the cluster)
