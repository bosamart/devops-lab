# Session 06 — ArgoCD GitOps
**Date:** June 17, 2026  
**Environment:** k3s cluster + ArgoCD v3.4.3 + GitHub

---

## What We Built

Complete GitOps pipeline — Git is the single source of truth:

```
git push YAML changes to GitHub
              ↓
ArgoCD detects change automatically
              ↓
Applies changes to k3s cluster
              ↓
Pods scale/update without any kubectl command
```

---

## Architecture

```
GitHub (devops-lab repo)
    kubernetes/session-04/
        ├── deployment.yaml  ← ArgoCD watches this
        └── service.yaml     ← ArgoCD watches this
              ↓
         ArgoCD
              ↓
       k3s cluster
    ├── k3s-master   (192.168.101.10)
    ├── k3s-worker1  (192.168.101.11)
    └── k3s-worker2  (192.168.101.12)
```

---

## Step 1 — Install ArgoCD

```bash
# Create namespace
sudo kubectl create namespace argocd

# Install ArgoCD
sudo kubectl apply -n argocd -f \
  https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Watch pods come up
sudo kubectl get pods -n argocd -w
```

**All pods running:**
```
argocd-application-controller    1/1  Running
argocd-applicationset-controller 1/1  Running
argocd-dex-server                1/1  Running
argocd-notifications-controller  1/1  Running
argocd-redis                     1/1  Running
argocd-repo-server               1/1  Running
argocd-server                    1/1  Running
```

---

## Step 2 — Get Admin Password

```bash
sudo kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d && echo
```

**Credentials:**
```
Username: admin
Password: 8Rg9BiaSDI0BZN7l
```

---

## Step 3 — Expose ArgoCD UI

```bash
sudo kubectl patch svc argocd-server -n argocd \
  -p '{"spec": {"type": "NodePort"}}'

sudo kubectl get svc -n argocd
```

**Access URLs:**
```
HTTP:  http://192.168.101.10:31120
HTTPS: https://192.168.101.10:32611
```

---

## Step 4 — Create ArgoCD Application

In ArgoCD UI → **+ NEW APP**

| Field | Value |
|-------|-------|
| Application Name | `flask-app` |
| Project | `default` |
| Sync Policy | `Automatic` |
| Repository URL | `https://github.com/bosamart/devops-lab` |
| Revision | `HEAD` |
| Path | `kubernetes/session-04` |
| Cluster URL | `https://kubernetes.default.svc` |
| Namespace | `default` |

---

## Step 5 — Clean YAML Files for ArgoCD

**Important:** YAML exported from kubectl contains extra metadata that causes conflicts. Always use clean YAML for ArgoCD.

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flask-app
  namespace: default
spec:
  replicas: 5
  selector:
    matchLabels:
      app: flask-app
  template:
    metadata:
      labels:
        app: flask-app
    spec:
      containers:
      - name: bosamart-nginx
        image: samathbo/bosamart-nginx:v1
        ports:
        - containerPort: 80
```

**service.yaml:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: flask-app
  namespace: default
spec:
  selector:
    app: flask-app
  ports:
  - port: 80
    targetPort: 80
    nodePort: 31965
  type: NodePort
```

---

## Step 6 — Test GitOps Auto-Sync

Change replicas in deployment.yaml:
```bash
nano ~/devops-lab/kubernetes/session-04/deployment.yaml
# Change replicas: 2 → replicas: 5

git add .
git commit -m "Scale to 5 replicas"
git push
```

**Result:** ArgoCD detected change and scaled to 5 pods automatically in seconds — no kubectl command needed ✅

---

## Final Result

```
APP HEALTH:  ✅ Healthy
SYNC STATUS: ✅ Synced
LAST SYNC:   ✅ Sync OK
HEALTHY:     9 resources
OutOfSync:   0
```

**5 pods running:**
```
flask-app-6856767f54-2tvrj   1/1   Running
flask-app-6856767f54-4nnxk   1/1   Running
flask-app-6856767f54-tj2t8   1/1   Running
flask-app-6856767f54-tpk2s   1/1   Running
flask-app-6856767f54-v756n   1/1   Running
```

---

## Key Concepts Learned

| Concept | Explanation |
|---------|-------------|
| **GitOps** | Git is single source of truth for infrastructure |
| **ArgoCD** | Tool that syncs Git repo to Kubernetes cluster |
| **Auto-sync** | ArgoCD detects and applies changes automatically |
| **Sync** | Making cluster match what's defined in Git |
| **OutOfSync** | Cluster state differs from Git definition |
| **Healthy** | All resources running correctly |
| **Self-healing** | ArgoCD restores cluster if someone changes it manually |

---

## Troubleshooting

**Sync Failed — object has been modified:**
- Cause: YAML exported from kubectl has extra metadata
- Fix: Use clean YAML without resourceVersion, uid, etc.
- Also delete manually created resources and let ArgoCD recreate them

```bash
sudo kubectl delete deployment flask-app
sudo kubectl delete svc flask-app
# ArgoCD recreates them cleanly
```

---

## Complete CI/CD Pipeline Summary

```
Developer edits code
        ↓
git push to GitHub
        ↓
GitHub Actions triggers (Session 05)
        ↓
Builds Docker image
        ↓
Pushes to Docker Hub (samathbo/bosamart-flask:latest)
        ↓
ArgoCD detects YAML change (Session 06)
        ↓
Auto-deploys to k3s cluster
        ↓
Pods updated across 3 nodes ✅
```

---

## Session 07 Preview — Prometheus + Grafana Monitoring

Next session we will:
- Deploy Prometheus to collect cluster metrics
- Deploy Grafana for visualization dashboards
- Monitor pod health, CPU, memory across nodes
- Set up alerts for when pods crash or resources are high
