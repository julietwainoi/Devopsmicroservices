# GitOps at Scale: Managing Microservices with ArgoCD's App of Apps Pattern

When I first deployed microservices to Kubernetes, I had everything in one place — deployments, databases, monitoring — all managed by a single ArgoCD Application. It worked, but as the system grew, troubleshooting became messy. A failed prometheus deployment would show up alongside failed service pods, making it hard to see what actually needed attention.

That's when I discovered the **App of Apps pattern**.

## The Problem with Monolithic Deployments

My initial setup looked like this:

```
repo/
├── argocd-app.yaml  (one Application watching one path)
└── k8s/
    ├── auth-service.yaml
    ├── order-service.yaml
    ├── prometheus.yaml
    ├── grafana.yaml
    └── nginx.yaml
```

One ArgoCD Application. One sync status. One massive resource tree mixing application logic, infrastructure, and monitoring.

When something broke, I had to dig through dozens of resources to find the issue. Worse, I couldn't roll back just monitoring without affecting my services.

## Enter App of Apps

The App of Apps pattern splits your deployment into logical domains, each managed by its own ArgoCD Application. Here's what I built:

```
repo/
├── argocd/
│   ├── parent.yaml          ← Bootstrap once
│   ├── microservices.yaml   ← Watches my-app/ (Helm chart)
│   ├── infra.yaml           ← Watches k8s/ (raw manifests)
│   └── monitoring.yaml      ← Watches monitoring/
├── my-app/                  ← Helm chart for services
├── k8s/                     ← Database, ingress, nginx
└── monitoring/              ← Prometheus, Grafana, exporters
```

**One parent Application** watches the `argocd/` folder. It finds the three child Application manifests and creates them. Each child then watches its own path and manages its own resources.

## How It Works

**Step 1: Create the parent**

```yaml
# argocd/parent.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: root-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/yourorg/yourrepo
    targetRevision: HEAD
    path: argocd
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

**Step 2: Define child Applications**

```yaml
# argocd/microservices.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: microservices
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/yourorg/yourrepo
    targetRevision: HEAD
    path: my-app
    helm:
      valueFiles:
        - values.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: default
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

Repeat for `infra.yaml` and `monitoring.yaml`, pointing to their respective paths.

**Step 3: Bootstrap**

```bash
kubectl apply -f argocd/parent.yaml
```

That's it. ArgoCD syncs the parent, which creates the child Applications, which sync their folders. Everything from here is automated.

## Why This Matters

**Separation of concerns**  
Each Application has its own sync status and health. If Grafana is degraded, I see it instantly without noise from unrelated services.

**Independent rollback**  
Made a bad change to your monitoring config? Roll back just the `monitoring` Application. Your services keep running untouched.

**Cleaner CI/CD**  
My GitHub Actions workflow updates image tags in `my-app/values.yaml`. Only the `microservices` Application syncs — infra and monitoring stay stable.

**Team ownership**  
Different teams can own different Applications. The platform team manages `infra`, the SRE team owns `monitoring`, and product teams control `microservices`.

## The GitOps Flow

Here's how a deployment flows end-to-end:

1. Push code to `auth-service/`
2. CI builds the image, pushes to registry, updates `my-app/values.yaml` with the new tag
3. ArgoCD detects the change in `values.yaml`
4. The `microservices` Application auto-syncs
5. Kubernetes rolls out the new auth-service pod

No manual `kubectl apply`. No drift. Git is the source of truth.

## When Not to Use App of Apps

If your deployment is small — a handful of services, no separate infra or monitoring — one Application is fine. App of Apps adds structure, but that structure has overhead. Use it when the separation actually helps you.

## Lessons Learned

**Keep the parent simple**  
The parent Application should only watch child Application manifests. Don't mix actual workload resources in the `argocd/` folder.

**Use `CreateNamespace=true`**  
Let ArgoCD create namespaces automatically. One less manual step.

**Name things clearly**  
`microservices`, `infra`, `monitoring` are obvious. `app-1`, `app-2`, `app-3` are not.

**Commit the parent to the repo**  
Even though you apply it manually once, keep `argocd/parent.yaml` in version control. Future you will thank you.

## The Bottom Line

ArgoCD's App of Apps pattern turned my messy monolithic deployment into a clean, maintainable system. Each concern lives in its own Application, syncs independently, and fails independently.

If you're managing more than a few services, give it a shot. The upfront structure pays off the first time you need to debug a deployment at 2 AM.

---

**Tech stack:** Kubernetes, ArgoCD, Helm, GitHub Actions  
**Repo structure:** [github.com/julietwainoi/Devopsmicroservices](https://github.com/julietwainoi/Devopsmicroservices)

What's your approach to managing multi-environment Kubernetes deployments? Drop your thoughts below.
