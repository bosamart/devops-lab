# Session 07 — Prometheus + Grafana Monitoring
**Date:** June 17, 2026  
**Environment:** k3s cluster | monitoring namespace

---

## What We Built

Monitoring stack deployed on Kubernetes:

```
k3s cluster
      ↓
Prometheus (port 9090) — scrapes metrics from pods and nodes
      ↓
Grafana (port 3000) — visualizes metrics as dashboards
```

---

## Step 1 — Create Monitoring Namespace

```bash
sudo kubectl create namespace monitoring
sudo kubectl get namespaces
```

---

## Step 2 — Deploy Prometheus

**prometheus.yaml:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
      - job_name: 'kubernetes-nodes'
        kubernetes_sd_configs:
          - role: node
      - job_name: 'kubernetes-pods'
        kubernetes_sd_configs:
          - role: pod
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:latest
        ports:
        - containerPort: 9090
        volumeMounts:
        - name: config
          mountPath: /etc/prometheus
      volumes:
      - name: config
        configMap:
          name: prometheus-config
---
apiVersion: v1
kind: Service
metadata:
  name: prometheus
  namespace: monitoring
spec:
  selector:
    app: prometheus
  ports:
  - port: 9090
    targetPort: 9090
    nodePort: 30090
  type: NodePort
```

```bash
sudo kubectl apply -f prometheus.yaml
sudo kubectl get pods -n monitoring -w
```

**Result:** Prometheus running in 24 seconds ✅

---

## Step 3 — Deploy Grafana

**grafana.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
      - name: grafana
        image: grafana/grafana:latest
        ports:
        - containerPort: 3000
        env:
        - name: GF_SECURITY_ADMIN_PASSWORD
          value: "admin123"
---
apiVersion: v1
kind: Service
metadata:
  name: grafana
  namespace: monitoring
spec:
  selector:
    app: grafana
  ports:
  - port: 3000
    targetPort: 3000
    nodePort: 30300
  type: NodePort
```

```bash
sudo kubectl apply -f grafana.yaml
sudo kubectl get pods -n monitoring
```

**Result:** Both pods running ✅
```
prometheus-7d5d5859b5-7bk5w   1/1   Running
grafana-85f97d9846-rzb9t      1/1   Running
```

---

## Step 4 — Access Services

| Service | URL |
|---------|-----|
| Grafana UI | http://192.168.101.10:30300 |
| Prometheus UI | http://192.168.101.10:30090 |

**Grafana login:**
```
Username: admin
Password: admin123
```

---

## Step 5 — Connect Prometheus to Grafana

Connections → Data sources → Add data source → Prometheus

```
URL: http://prometheus.monitoring.svc.cluster.local:9090
```

Click **Save & test** ✅

**Why not localhost?**
Each pod has its own localhost. Kubernetes DNS provides service discovery:
```
http://[service].[namespace].svc.cluster.local:[port]
```
This works from any pod inside the cluster.

---

## Step 6 — Import Kubernetes Dashboard

Dashboards → New → Import → ID: `6417` → Load → Import

Dashboard: **Kubernetes Cluster (Prometheus)**

Sections available:
- Cluster Health (CPU, Memory, Disk, Pod usage)
- Deployments
- Nodes
- Pods Running/Pending/Failed
- Containers

---

## Key Concepts Learned

| Concept | Explanation |
|---------|-------------|
| **Prometheus** | Collects and stores metrics from services |
| **Grafana** | Visualizes metrics as dashboards and charts |
| **Scrape** | Prometheus pulls metrics from targets every 15s |
| **ConfigMap** | Kubernetes way to store config files |
| **Service DNS** | `service.namespace.svc.cluster.local` |
| **NodePort** | Exposes service on every node's IP |
| **Dashboard ID** | Pre-built Grafana dashboards from grafana.com |

---

## Useful Dashboard IDs

| ID | Dashboard |
|----|-----------|
| 6417 | Kubernetes Cluster monitoring |
| 3662 | Prometheus self monitoring |
| 1860 | Node Exporter full metrics |
| 9614 | Nginx monitoring |

---

## Next Step — Add Node Exporter

To get full metrics (CPU, memory per node), install node-exporter:

```bash
# Deploy node-exporter as DaemonSet
# Runs on every node automatically
sudo kubectl apply -f https://raw.githubusercontent.com/prometheus/node_exporter/master/examples/k8s/daemonset.yaml
```

This will populate the N/A panels with real data.

---

## Complete Lab Summary

```
devops-lab/
├── .github/workflows/docker-build.yml  ← CI pipeline
├── docker/
│   ├── session-01/  Docker install
│   ├── session-02/  Dockerfile + Docker Hub
│   └── session-03/  Flask + Nginx + Compose
├── kubernetes/
│   └── session-04/  k3s cluster + deployments
├── cicd/
│   ├── session-05/  GitHub Actions
│   └── session-06/  ArgoCD GitOps
└── monitoring/
    └── session-07/  Prometheus + Grafana ← TODAY
```

---

## Full CI/CD + Monitoring Pipeline

```
git push code
      ↓
GitHub Actions → builds Docker image → Docker Hub
      ↓
ArgoCD → detects change → deploys to k3s
      ↓
Prometheus → scrapes metrics from pods
      ↓
Grafana → visualizes on dashboard
```

**This is a production-grade DevOps stack. ✅**
