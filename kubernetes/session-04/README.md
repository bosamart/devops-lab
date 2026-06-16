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
# Create deployment with 3 replicas
sudo kubectl create deployment flask-app \
  --image=samathbo/bosamart-nginx:v1 \
  --replicas=3

# Watch pods come up
sudo kubectl get pods -w

# Expose as NodePort service
sudo kubectl expose deployment flask-app \
  --port=80 \
  --type=NodePort

# Check service
sudo kubectl get svc
```

**Output:**
```
NAME         TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
flask-app    NodePort    10.43.170.122   <none>        80:31965/TCP   0s
```

---

## Step 5 — Verify Pods on All Nodes

```bash
sudo kubectl get pods -o wide
```

**Output:**
```
NAME                         READY   STATUS    NODE
flask-app-6fb75956f5-8l5qg   1/1     Running   k3s-worker2
flask-app-6fb75956f5-9hm8p   1/1     Running   k3s-worker1
flask-app-6fb75956f5-fc7ww   1/1     Running   k3s-master
```

✅ Kubernetes automatically spread pods across all 3 nodes

---

## Step 6 — Test from All Nodes

```bash
curl http://192.168.101.10:31965  # master
curl http://192.168.101.11:31965  # worker1
curl http://192.168.101.12:31965  # worker2
```

All 3 returned the Flask app response ✅

---

## Step 7 — Self-Healing Test

```bash
# Delete a pod
sudo kubectl delete pod flask-app-6fb75956f5-8l5qg

# Watch replacement
sudo kubectl get pods -w
```

**Result:** Kubernetes created a new pod in **1 second** automatically ✅

---

## Step 8 — Scaling

```bash
# Scale up to 6 pods
sudo kubectl scale deployment flask-app --replicas=6
sudo kubectl get pods -o wide

# Scale down to 2 pods
sudo kubectl scale deployment flask-app --replicas=2
sudo kubectl get pods -o wide
```

**Result:** Kubernetes added/removed pods instantly across nodes ✅

---

## Step 9 — Save YAML Configs

```bash
mkdir -p ~/devops-lab/kubernetes/session-04
cd ~/devops-lab/kubernetes/session-04

sudo kubectl get deployment flask-app -o yaml > deployment.yaml
sudo kubectl get svc flask-app -o yaml > service.yaml
```

---

## Essential kubectl Commands

```bash
kubectl get nodes                    # List all nodes
kubectl get pods                     # List pods
kubectl get pods -o wide             # List pods with node info
kubectl get pods -w                  # Watch pods in real time
kubectl get svc                      # List services
kubectl get all                      # List everything
kubectl describe pod <name>          # Pod details
kubectl logs <pod-name>              # View pod logs
kubectl delete pod <name>            # Delete a pod
kubectl scale deployment <name> --replicas=N   # Scale
kubectl get deployment               # List deployments
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

## GitHub Push

```bash
cd ~/devops-lab
git add .
git commit -m "Session 04: k3s cluster + Flask deployment + scaling"
git push
```

**Files saved:**
- `kubernetes/session-04/deployment.yaml`
- `kubernetes/session-04/service.yaml`

---

## Session 05 Preview — GitHub Actions CI/CD

Next session we will:
- Create a GitHub Actions workflow file
- Automatically build Docker image on every git push
- Push new image to Docker Hub automatically
- Complete the CI part of CI/CD pipeline
