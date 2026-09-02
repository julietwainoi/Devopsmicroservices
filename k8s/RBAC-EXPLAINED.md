# Role vs ClusterRole - Complete Explanation

## Key Difference: Scope

### Role - Namespace Scoped
- **Works only in ONE namespace**
- Like a "room key" - only opens doors in that specific room
- Example: `Role` in namespace "production" can only control resources in "production"

### ClusterRole - Cluster Scoped
- **Works across ALL namespaces** or cluster-level resources
- Like a "master key" - opens doors everywhere
- Can access cluster-wide resources (nodes, persistent volumes, namespaces themselves)

---

## Visual Comparison

```
CLUSTER
├── Namespace: production
│   ├── Pod: user-service (uses Role "config-reader")
│   ├── ConfigMap: app-config ✓ (Role can access this)
│   └── Secret: db-password ✓ (Role can access this)
│
├── Namespace: staging
│   ├── Pod: user-service
│   ├── ConfigMap: app-config ✗ (Role CANNOT access this - different namespace!)
│   └── Secret: db-password ✗ (Role CANNOT access this)
│
└── Cluster Resources
    ├── Node: worker-1 ✗ (Role CANNOT access - not namespaced)
    └── PersistentVolume ✗ (Role CANNOT access - cluster resource)

---

CLUSTER (with ClusterRole)
├── Namespace: production
│   ├── Pod: monitoring (uses ClusterRole "cluster-reader")
│   ├── ConfigMap ✓ (ClusterRole can access)
│   └── Secret ✓ (ClusterRole can access)
│
├── Namespace: staging
│   ├── ConfigMap ✓ (ClusterRole can access)
│   └── Secret ✓ (ClusterRole can access)
│
└── Cluster Resources
    ├── Node: worker-1 ✓ (ClusterRole can access)
    └── PersistentVolume ✓ (ClusterRole can access)
```

---

## When to Use Each

### Use Role when:
✓ Service only needs access to resources in its own namespace
✓ You want to limit blast radius (security best practice)
✓ Your microservices don't need cross-namespace access
✓ **Most common case for microservices**

**Example:**
```yaml
# user-service only needs to read configs in "default" namespace
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: config-reader
  namespace: default  # ← Only works in this namespace
rules:
- apiGroups: [""]
  resources: ["configmaps", "secrets"]
  verbs: ["get", "list"]
```

### Use ClusterRole when:
✓ Monitoring tools need to see all namespaces (Prometheus, Grafana)
✓ CI/CD systems deploying to multiple namespaces
✓ Admin users managing the whole cluster
✓ Need to access cluster-level resources (nodes, PVs, namespaces)

**Example:**
```yaml
# Prometheus needs to monitor ALL namespaces
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: prometheus-reader
  # No namespace field - works everywhere!
rules:
- apiGroups: [""]
  resources: ["pods", "services", "endpoints"]
  verbs: ["get", "list", "watch"]
```

---

## The Logic for Joining a Role to a Service

This is a 3-step chain:

```
Service (Pod) → ServiceAccount → RoleBinding → Role → Permissions
```

### Step-by-Step Logic:

#### 1. **Create ServiceAccount** (Identity for the pod)
Think of this as creating a "user account" for your application.

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: user-service-sa
  namespace: default
```

#### 2. **Create Role** (Define permissions)
This is the "permission list" - what actions are allowed on which resources.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: config-reader
  namespace: default
rules:
- apiGroups: [""]
  resources: ["configmaps", "secrets"]
  verbs: ["get", "list", "watch"]  # ← What you can do
```

#### 3. **Create RoleBinding** (Connect identity to permissions)
This is the "assignment" - giving the ServiceAccount the permissions defined in the Role.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: user-service-binding
  namespace: default
subjects:  # ← WHO gets the permissions
- kind: ServiceAccount
  name: user-service-sa  # ← The identity
  namespace: default
roleRef:   # ← WHAT permissions they get
  kind: Role
  name: config-reader  # ← The permission set
  apiGroup: rbac.authorization.k8s.io
```

#### 4. **Use in Deployment** (Assign identity to pod)
Tell the pod to use this ServiceAccount.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
spec:
  template:
    spec:
      serviceAccountName: user-service-sa  # ← Pod uses this identity
      containers:
      - name: user-service
        image: user-service:latest
```

---

## Real-World Analogy

Think of it like a hotel:

1. **ServiceAccount** = Guest Badge with your name
2. **Role** = List of areas you can access (pool, gym, floor 3)
3. **RoleBinding** = The front desk assigning the badge to you and programming it with access
4. **Pod** = You wearing the badge to access facilities

```
You → Badge → Badge Reader → Access List → Door Opens
Pod → ServiceAccount → RoleBinding → Role → API Access Granted
```

---

## Complete Example: Order Service Needs Database Access

```yaml
# 1. ServiceAccount (Identity)
apiVersion: v1
kind: ServiceAccount
metadata:
  name: order-service-sa
  namespace: default
---
# 2. Role (Permissions needed)
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: db-accessor
  namespace: default
rules:
- apiGroups: [""]
  resources: ["secrets"]
  resourceNames: ["db-password"]  # ← Only this specific secret
  verbs: ["get"]
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["get", "list"]
---
# 3. RoleBinding (Connection)
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: order-service-db-access
  namespace: default
subjects:
- kind: ServiceAccount
  name: order-service-sa  # ← This identity
roleRef:
  kind: Role
  name: db-accessor  # ← Gets these permissions
  apiGroup: rbac.authorization.k8s.io
---
# 4. Deployment (Usage)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
spec:
  template:
    spec:
      serviceAccountName: order-service-sa  # ← Use the identity
      containers:
      - name: order-service
        image: order-service:latest
```

---

## Why This Design?

### Separation of Concerns:
- **ServiceAccount** = WHO (identity)
- **Role** = WHAT (permissions)
- **RoleBinding** = Connects WHO to WHAT

### Benefits:
1. **Reusability**: Multiple services can share the same Role
2. **Flexibility**: Change permissions without touching deployments
3. **Security**: Easy to audit who has what access
4. **Scalability**: One Role can apply to many ServiceAccounts

---

## Common Patterns in Your Microservices

### Pattern 1: One ServiceAccount per Service (Recommended)
```
user-service-sa → config-reader Role
order-service-sa → resource-manager Role
payment-service-sa → config-reader Role
auth-service-sa → pod-reader Role + config-reader Role
```

### Pattern 2: Shared ServiceAccount (Not Recommended)
```
all-services-sa → admin Role  ← Bad! Too much access
```

### Pattern 3: Monitoring (ClusterRole)
```
prometheus-sa → ClusterRole (reads all namespaces)
grafana-sa → ClusterRole (reads metrics everywhere)
```

---

## Testing Your Setup

```bash
# 1. Check if ServiceAccount exists
kubectl get serviceaccount user-service-sa

# 2. Check if Role exists
kubectl get role config-reader

# 3. Check if RoleBinding exists
kubectl get rolebinding user-service-binding

# 4. Test permissions
kubectl auth can-i get configmaps \
  --as=system:serviceaccount:default:user-service-sa

# 5. Test what the ServiceAccount CAN do
kubectl auth can-i --list \
  --as=system:serviceaccount:default:user-service-sa

# 6. Test what the ServiceAccount CANNOT do
kubectl auth can-i delete pods \
  --as=system:serviceaccount:default:user-service-sa
# Should return "no"
```

---

## Security Best Practices

### ✓ DO:
- Use Role instead of ClusterRole when possible
- Create separate ServiceAccounts for each service
- Grant minimum required permissions
- Use `resourceNames` to limit access to specific resources
- Regularly audit permissions

### ✗ DON'T:
- Give ClusterRole when Role is sufficient
- Reuse ServiceAccounts across unrelated services
- Grant wildcard permissions (`verbs: ["*"]`)
- Use `cluster-admin` ClusterRole for services
- Auto-mount tokens if service doesn't need K8s API access

---

## Quick Reference Table

| Aspect | Role | ClusterRole |
|--------|------|-------------|
| **Scope** | Single namespace | Entire cluster |
| **Bound by** | RoleBinding | ClusterRoleBinding |
| **Can access** | Namespaced resources | All resources + cluster resources |
| **Example use** | Microservice config access | Monitoring, admin tools |
| **Security** | More secure (limited) | Less secure (broader) |
| **Most common** | ✓ Yes (for apps) | No (for infrastructure) |

---

## Your Microservices Architecture Decision

For your setup, here's the recommended approach:

```yaml
# Each microservice gets its own ServiceAccount
user-service → user-service-sa → Role (config-reader)
order-service → order-service-sa → Role (resource-manager)
payment-service → payment-service-sa → Role (config-reader)
product-service → product-service-sa → Role (config-reader)
auth-service → auth-service-sa → Role (config-reader + pod-reader)

# Monitoring gets ClusterRole
prometheus → prometheus-sa → ClusterRole (metrics-reader)
grafana → grafana-sa → ClusterRole (metrics-reader)
```

This gives each service only what it needs, nothing more.
