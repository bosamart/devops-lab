# Session 07 — Prometheus + Grafana + Node Exporter + Kube State Metrics
**Date:** June 17, 2026  
**Environment:** k3s cluster | monitoring namespace

---

## What We Built

Complete monitoring stack on Kubernetes:

```
k3s cluster (3 nodes)
      ↓
node-exporter (DaemonSet) — collects hardware metrics from every node
      ↓
kube-state-metrics — collects Kubernetes object metrics (pods, deployments)
      ↓
Prometheus (port 9090) — scrapes and stores all metrics
      ↓
Grafana (port 3000) — visualizes metrics as dashboards
```

---

## Files in This Session

```
monitoring/session-07/
├── prometheus.yaml          ← Prometheus deployment + config
├── grafana.yaml             ← Grafana deployment
├── node-exporter.yaml       ← DaemonSet on all nodes
└── kube-state-metrics.yaml  ← Kubernetes object metrics
```

---

## Step 1 — Create Monitoring Namespace

```bash
sudo kubectl create namespace monitoring
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
      - job_name: 'node-exporter'
        static_configs:
          - targets:
            - '192.168.101.10:9100'
            - '192.168.101.11:9100'
            - '192.168.101.12:9100'
      - job_name: 'kube-state-metrics'
        static_configs:
          - targets:
            - 'kube-state-metrics.kube-system.svc.cluster.local:8080'
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
```

---

## Step 4 — Deploy Node Exporter

DaemonSet — automatically runs one pod on **every node** in the cluster.

**node-exporter.yaml:**
```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-exporter
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: node-exporter
  template:
    metadata:
      labels:
        app: node-exporter
    spec:
      hostNetwork: true
      hostPID: true
      containers:
      - name: node-exporter
        image: prom/node-exporter:latest
        ports:
        - containerPort: 9100
          hostPort: 9100
        securityContext:
          privileged: true
        volumeMounts:
        - name: proc
          mountPath: /host/proc
          readOnly: true
        - name: sys
          mountPath: /host/sys
          readOnly: true
      volumes:
      - name: proc
        hostPath:
          path: /proc
      - name: sys
        hostPath:
          path: /sys
```

```bash
sudo kubectl apply -f node-exporter.yaml
sudo kubectl get pods -n monitoring
```

**Result:** 3 node-exporter pods — one per node ✅

---

## Step 5 — Deploy Kube State Metrics

Collects Kubernetes object metrics (pod counts, deployment status, replica counts).

**kube-state-metrics.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kube-state-metrics
  namespace: kube-system
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kube-state-metrics
  template:
    metadata:
      labels:
        app: kube-state-metrics
    spec:
      serviceAccountName: kube-state-metrics
      containers:
      - name: kube-state-metrics
        image: registry.k8s.io/kube-state-metrics/kube-state-metrics:v2.13.0
        ports:
        - containerPort: 8080
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: kube-state-metrics
  namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: kube-state-metrics
rules:
- apiGroups: [""]
  resources: ["nodes","pods","services","endpoints","persistentvolumeclaims","persistentvolumes","namespaces","replicationcontrollers"]
  verbs: ["list","watch"]
- apiGroups: ["apps"]
  resources: ["deployments","replicasets","statefulsets","daemonsets"]
  verbs: ["list","watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: kube-state-metrics
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: kube-state-metrics
subjects:
- kind: ServiceAccount
  name: kube-state-metrics
  namespace: kube-system
---
apiVersion: v1
kind: Service
metadata:
  name: kube-state-metrics
  namespace: kube-system
spec:
  selector:
    app: kube-state-metrics
  ports:
  - port: 8080
    targetPort: 8080
```

```bash
sudo kubectl apply -f kube-state-metrics.yaml
sudo kubectl get pods -n kube-system | grep kube-state
```

---

## Step 6 — Restart Prometheus to Pick Up New Config

```bash
sudo kubectl rollout restart deployment prometheus -n monitoring
sudo kubectl get pods -n monitoring
```

---

## Step 7 — Access Services

| Service | URL | Login |
|---------|-----|-------|
| Grafana | http://192.168.101.10:30300 | admin / admin123 |
| Prometheus | http://192.168.101.10:30090 | - |

---

## Step 8 — Connect Prometheus to Grafana

Connections → Data sources → Add → Prometheus

```
URL: http://prometheus.monitoring.svc.cluster.local:9090
```

Save & test ✅

**Why not localhost?**
Each pod has its own localhost. Use Kubernetes DNS:
```
http://[service-name].[namespace].svc.cluster.local:[port]
```

---

## Step 9 — Import Grafana Dashboard

Dashboards → New → Import → ID: `6417` → Load → Select Prometheus → Import

---

## Final Result

All monitoring pods running:
```
NAME                          READY   STATUS
grafana                       1/1     Running
node-exporter (x3)            1/1     Running  ← one per node
prometheus                    1/1     Running
kube-state-metrics            1/1     Running
```

Grafana dashboard showing real data:
```
Number of Nodes:     3
Pods Running:        25
Pods Pending:        0
Pods Failed:         0
Deployment Replicas: 18
Nodes Unavailable:   0
Containers Running:  27
```

---

## Key Concepts Learned

| Concept | Explanation |
|---------|-------------|
| **Prometheus** | Collects and stores metrics — pulls from targets every 15s |
| **Grafana** | Visualizes metrics as dashboards |
| **node-exporter** | Collects hardware metrics (CPU, memory, disk) from each node |
| **kube-state-metrics** | Collects Kubernetes object metrics (pods, deployments, replicas) |
| **DaemonSet** | Runs one pod on every node automatically |
| **ConfigMap** | Kubernetes way to store config files |
| **ClusterRole** | Permissions to access Kubernetes API resources |
| **ServiceAccount** | Identity for a pod to authenticate with Kubernetes API |

---

## Why Two Exporters?

| Exporter | Collects | Example metrics |
|----------|----------|-----------------|
| node-exporter | Hardware/OS level | CPU%, memory usage, disk I/O |
| kube-state-metrics | Kubernetes objects | Pod count, deployment replicas, node status |

Both are needed for a complete Kubernetes monitoring picture.

---

## Useful Prometheus Queries

```
# CPU usage per node
node_cpu_seconds_total

# Memory usage
node_memory_MemAvailable_bytes

# Pod count
kube_pod_info

# Deployment replicas
kube_deployment_spec_replicas
```
