# Kubernetes RBAC Guide

## Overview
This guide explains how to create and use Roles, ServiceAccounts, and Users in Kubernetes.

## Components

### 1. ServiceAccount (for Pods)
ServiceAccounts are used by pods to authenticate with the Kubernetes API.

**Create:**
```bash
kubectl create serviceaccount my-service-sa
```

**Use in Pod:**
```yaml
spec:
  serviceAccountName: my-service-sa
```

### 2. Role (Namespace-scoped permissions)
Defines what actions can be performed on which resources.

**Create:**
```bash
kubectl create role pod-reader --verb=get,list,watch --resource=pods
```

### 3. RoleBinding (Connect ServiceAccount to Role)
Links a ServiceAccount to a Role.

**Create:**
```bash
kubectl create rolebinding my-binding --role=pod-reader --serviceaccount=default:my-service-sa
```

### 4. ClusterRole & ClusterRoleBinding (Cluster-wide)
Same as Role/RoleBinding but applies across all namespaces.

## Apply the RBAC Configuration

```bash
# 1. Create ServiceAccounts
kubectl apply -f k8s/rbac-serviceaccounts.yaml

# 2. Create Roles
kubectl apply -f k8s/rbac-roles.yaml

# 3. Create RoleBindings
kubectl apply -f k8s/rbac-rolebindings.yaml

# 4. Create ClusterRoles (optional)
kubectl apply -f k8s/rbac-clusterroles.yaml

# 5. Verify
kubectl get serviceaccounts
kubectl get roles
kubectl get rolebindings
```

## Using ServiceAccount in Your Application

### Method 1: In Deployment YAML
```yaml
spec:
  serviceAccountName: user-service-sa
  automountServiceAccountToken: true
```

### Method 2: Access from within Pod
The token is automatically mounted at:
```
/var/run/secrets/kubernetes.io/serviceaccount/token
```

### Method 3: In Python (for your microservices)
```python
from kubernetes import client, config

# Load in-cluster config (uses service account)
config.load_incluster_config()

# Create API client
v1 = client.CoreV1Api()

# Now you can make API calls based on your role permissions
pods = v1.list_namespaced_pod(namespace="default")
```

## Creating Human Users (for kubectl access)

Kubernetes doesn't have User objects. Instead, you create certificates or tokens:

### Method 1: Certificate-based User
```bash
# 1. Generate private key
openssl genrsa -out user.key 2048

# 2. Create certificate signing request
openssl req -new -key user.key -out user.csr -subj "/CN=myuser/O=mygroup"

# 3. Create CertificateSigningRequest in K8s
cat <<EOF | kubectl apply -f -
apiVersion: certificates.k8s.io/v1
kind: CertificateSigningRequest
metadata:
  name: myuser
spec:
  request: $(cat user.csr | base64 | tr -d '\n')
  signerName: kubernetes.io/kube-apiserver-client
  usages:
  - client auth
EOF

# 4. Approve the CSR
kubectl certificate approve myuser

# 5. Get the certificate
kubectl get csr myuser -o jsonpath='{.status.certificate}' | base64 -d > user.crt

# 6. Create kubeconfig
kubectl config set-credentials myuser --client-certificate=user.crt --client-key=user.key
kubectl config set-context myuser-context --cluster=kind-kind --user=myuser
```

### Method 2: ServiceAccount Token (for external apps)
```bash
# Create a service account
kubectl create serviceaccount external-app-sa

# Create token (Kubernetes 1.24+)
kubectl create token external-app-sa --duration=87600h

# Or create a secret with token (older method)
kubectl apply -f - <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: external-app-sa-token
  annotations:
    kubernetes.io/service-account.name: external-app-sa
type: kubernetes.io/service-account-token
EOF

# Get the token
kubectl get secret external-app-sa-token -o jsonpath='{.data.token}' | base64 -d
```

## Common Permission Patterns

### Read-only access
```yaml
rules:
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["get", "list", "watch"]
```

### Full access to specific resource
```yaml
rules:
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["*"]
```

### Access to specific resource name
```yaml
rules:
- apiGroups: [""]
  resources: ["secrets"]
  resourceNames: ["my-secret"]
  verbs: ["get"]
```

## Testing Permissions

```bash
# Check if service account can perform action
kubectl auth can-i get pods --as=system:serviceaccount:default:user-service-sa

# Check all permissions
kubectl auth can-i --list --as=system:serviceaccount:default:user-service-sa
```

## Security Best Practices

1. **Principle of Least Privilege**: Give only necessary permissions
2. **Separate ServiceAccounts**: Don't reuse ServiceAccounts across services
3. **Avoid ClusterAdmin**: Use specific roles instead
4. **Regular Audits**: Review permissions periodically
5. **Disable Token Automount**: If not needed, set `automountServiceAccountToken: false`

## Troubleshooting

```bash
# View service account details
kubectl describe serviceaccount user-service-sa

# View role details
kubectl describe role config-reader

# View rolebinding details
kubectl describe rolebinding user-service-config-reader

# Check service account token
kubectl get secret $(kubectl get sa user-service-sa -o jsonpath='{.secrets[0].name}') -o yaml
```
