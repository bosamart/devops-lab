# Session 04 — Kubernetes with k3s
**Date:** June 16, 2026  
**Environment:** EVE-NG | 3x Ubuntu 24.04 | k3s v1.35.5+k3s1

---

## Cluster Architecture

```
k3s-master   192.168.101.10  ← control plane
k3s-worker1  192.168.101.11  ← worker node
k3s-worker2  192.168.101.12  ← worker node
```

---

## Step 1 — Set Hostnames

On each node:
```bash
# On master
sudo hostnamectl set-hostname k3s-master

# On worker1
sudo hostnamectl set-hostname k3s-worker1

# On worker2
sudo hostnamectl set-hostname k3s-worker2
```

Add to `/etc/hosts` on ALL nodes:
```
192.168.101.10  k3s-master
192.168.101.11  k3s-worker1
192.168.101.12  k3s-worker2
```

---

## Step 2 — Install k3s on Master

```bash
curl -sfL https://get.k3s.io | sh -

# Verify running
sudo systemctl status k3s
sudo kubectl get nodes

# Get token for workers
sudo cat /var/lib/rancher/k3s/server/node-token
```

**Output:**
```
NAME         STATUS   ROLES           AGE   VERSION
k3s-master   Ready    control-plane   2m    v1.35.5+k3s1
```

---

## Step 3 — Join Worker Nodes

Run on **each worker node:**
```bash
curl -sfL https://get.k3s.io | \
  K3S_URL=https://192.168.101.10:6443 \
  K3S_TOKEN=<token-from-master> \
  sh -
```

Verify on master:
```bash
sudo kubectl get nodes
```

**Output:**
```
NAME          STATUS   ROLES           AGE     VERSION
k3s-master    Ready    control-plane   4m39s   v1.35.5+k3s1
k3s-worker1   Ready    <none>          57s     v1.35.5+k3s1
k3s-worker2   Ready    <none>          49s     v1.35.5+k3s1
```

---

## Step 4 — Deploy Flask App

```bash
mkdir -p ~/devops-lab/kubernetes/session-04
cd ~/devops-lab/kubernetes/session-04
```

**deployment.yaml (clean version for ArgoCD):**
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

**service.yaml (clean version for ArgoCD):**
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

> **Important:** Always use clean YAML without extra metadata (resourceVersion, uid, etc.)
> when using ArgoCD. Exported kubectl YAML causes sync conflicts.

Apply manually first time:
```bash
sudo kubectl apply -f deployment.yaml
sudo kubectl apply -f service.yaml
```

---

## Step 5 — Verify Pods on All Nodes

```bash
sudo kubectl get pods -o wide
```

**Output:**
```
NAME                         READY   STATUS    NODE
flask-app-xxx   1/1     Running   k3s-worker2
flask-app-xxx   1/1     Running   k3s-worker1
flask-app-xxx   1/1     Running   k3s-master
```

✅ Kubernetes automatically spread pods across all 3 nodes

---

## Step 6 — Test from All Nodes

```bash
curl http://192.168.101.10:31965  # master
curl http://192.168.101.11:31965  # worker1
curl http://192.168.101.12:31965  # worker2
```

All 3 returned the app response ✅

---

## Step 7 — Self-Healing Test

```bash
# Delete a pod
sudo kubectl delete pod <pod-name>

# Watch replacement
sudo kubectl get pods -w
```

**Result:** Kubernetes created a new pod in **1 second** automatically ✅

---

## Step 8 — Scaling

```bash
# Scale up to 6 pods
sudo kubectl scale deployment flask-app --replicas=6

# Scale down to 2 pods
sudo kubectl scale deployment flask-app --replicas=2
```

**Result:** Kubernetes added/removed pods instantly across nodes ✅

---

## Essential kubectl Commands

```bash
kubectl get nodes                              # List all nodes
kubectl get nodes -o wide                      # List nodes with IP info
kubectl get pods                               # List pods
kubectl get pods -o wide                       # List pods with node info
kubectl get pods -w                            # Watch pods in real time
kubectl get pods -A                            # All pods across all namespaces
kubectl get svc                                # List services
kubectl get svc -A                             # All services
kubectl get all -A                             # List everything
kubectl describe pod <name>                    # Pod details
kubectl logs <pod-name>                        # View pod logs
kubectl delete pod <name>                      # Delete a pod
kubectl scale deployment <name> --replicas=N   # Scale
kubectl get deployment                         # List deployments
```

---

## Key Concepts Learned

| Concept | Explanation |
|---------|-------------|
| **Node** | A server in the cluster (master or worker) |
| **Pod** | Smallest unit — one or more containers |
| **Deployment** | Manages pods, ensures desired replicas running |
| **Service** | Exposes pods to network traffic |
| **NodePort** | Exposes service on a port on every node |
| **Replica** | Copy of a pod running in cluster |
| **Self-healing** | Kubernetes auto-replaces crashed pods |
| **Scaling** | Increase/decrease pod count with one command |
| **kubectl** | CLI tool to manage Kubernetes cluster |

---

## Kubernetes vs Docker Compose

| Docker Compose | Kubernetes |
|----------------|------------|
| Runs on 1 machine | Runs across many machines |
| Manual restart if crashes | Auto-restarts crashed containers |
| Manual scaling | Scale with one command |
| Good for development | Good for production |

---

## Notes on Clean YAML for ArgoCD

When you export YAML using `kubectl get ... -o yaml`, it includes extra fields:
- `resourceVersion`
- `uid`
- `creationTimestamp`
- `managedFields`

These cause ArgoCD sync conflicts. Always write clean YAML from scratch when using GitOps.

**Bad (exported from kubectl):**
```yaml
metadata:
  name: flask-app
  resourceVersion: "1375"    ← causes conflict
  uid: 67476303-...          ← causes conflict
```

**Good (clean for ArgoCD):**
```yaml
metadata:
  name: flask-app
  namespace: default
```
