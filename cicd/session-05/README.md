# Session 05 — GitHub Actions CI/CD Pipeline
**Date:** June 16, 2026  
**Environment:** GitHub Actions + Docker Hub + EVE-NG Lab

---

## What We Built

A fully automated CI pipeline triggered on every git push:

```
Developer pushes code to GitHub
              ↓
GitHub Actions triggers automatically
              ↓
Builds Docker image from Dockerfile
              ↓
Pushes image to Docker Hub
              ↓
samathbo/bosamart-flask:latest updated ✅
```

---

## Step 1 — Add Docker Hub Secrets to GitHub

Go to: `github.com/bosamart/devops-lab` → Settings → Secrets and variables → Actions

| Secret Name | Value |
|-------------|-------|
| `DOCKER_USERNAME` | `samathbo` |
| `DOCKER_PASSWORD` | Docker Hub Access Token (not account password) |

**Important:** Docker Hub requires an Access Token, not your account password.  
Generate at: hub.docker.com → Account Settings → Security → Personal access tokens

---

## Step 2 — Create Workflow File

```bash
mkdir -p ~/devops-lab/.github/workflows
nano ~/devops-lab/.github/workflows/docker-build.yml
```

**docker-build.yml:**
```yaml
name: Build and Push Docker Image

on:
  push:
    branches:
      - main

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and Push image
        uses: docker/build-push-action@v5
        with:
          context: ./docker/session-03
          push: true
          tags: samathbo/bosamart-flask:latest
```

---

## Step 3 — Push to GitHub

```bash
cd ~/devops-lab
git add .
git commit -m "Session 05: Add GitHub Actions CI/CD workflow"
git push
```

GitHub Actions triggers automatically on push.

---

## Step 4 — Fix Docker Hub Authentication Error

**Error:** `unauthorized: incorrect username or password`

**Cause:** Docker Hub no longer accepts account passwords via API.

**Fix:**
1. Go to hub.docker.com → Account Settings → Security
2. Click **Personal access tokens** → **New Access Token**
3. Name: `github-actions`, Permissions: Read & Write
4. Copy token
5. Update `DOCKER_PASSWORD` secret on GitHub with the token
6. Re-run the workflow

---

## Step 5 — Test Pipeline End to End

Edit the Flask app:
```bash
nano ~/devops-lab/docker/session-03/app.py
```

Change response to:
```python
return '<h1>Hello from bosamart DevOps Lab v2!</h1><p>CI/CD pipeline working!</p>'
```

Push:
```bash
git add .
git commit -m "Session 05: Test CI/CD pipeline - update Flask app v2"
git push
```

GitHub Actions triggered automatically and completed in 29 seconds ✅

---

## Results

**GitHub Actions — 2 successful runs:**
```
✅ Session 05: Test CI/CD pipeline - update Flask app v2   (29s)
✅ Session 05: Add GitHub Actions CI/CD workflow            (33s)
```

**Docker Hub:**
```
Repository: samathbo/bosamart-flask
Tag: latest
Size: 49.6 MB
Updated: automatically by pipeline
```

---

## Workflow File Explained

```yaml
on:
  push:
    branches:
      - main          # Triggers on every push to main branch

runs-on: ubuntu-latest  # GitHub provides a fresh Ubuntu VM

steps:
  - checkout          # Downloads your repo code
  - login             # Authenticates to Docker Hub using secrets
  - build-push        # Builds Dockerfile and pushes image
```

---

## Key Concepts Learned

| Concept | Explanation |
|---------|-------------|
| **CI/CD** | Continuous Integration / Continuous Delivery |
| **CI** | Automatically build and test on every push |
| **GitHub Actions** | GitHub's built-in automation platform |
| **Workflow** | YAML file defining automated steps |
| **Trigger** | Event that starts the workflow (push, PR, schedule) |
| **Runner** | Server that executes the workflow (ubuntu-latest) |
| **Secrets** | Encrypted variables — never visible in logs |
| **Actions** | Pre-built steps from GitHub marketplace |

---

## CI/CD vs Manual Deployment

| Manual | CI/CD Pipeline |
|--------|----------------|
| Edit code | Edit code |
| Manually build image | ← automated |
| Manually push to Docker Hub | ← automated |
| Manually update server | ← automated (next: ArgoCD) |
| Easy to forget steps | Never misses a step |
| Inconsistent builds | Reproducible every time |

---

## GitHub Repository Structure So Far

```
devops-lab/
├── .github/
│   └── workflows/
│       └── docker-build.yml    ← CI pipeline
├── docker/
│   ├── session-01/README.md
│   ├── session-02/Dockerfile + index.html
│   └── session-03/Dockerfile + app.py + nginx.conf + docker-compose.yml
├── kubernetes/
│   └── session-04/deployment.yaml + service.yaml + README.md
├── cicd/
│   └── session-05/
└── monitoring/                 ← Session 07
```

---

## Session 06 Preview — ArgoCD GitOps

Next session we will:
- Install ArgoCD on our k3s cluster
- Connect ArgoCD to our GitHub repo
- ArgoCD automatically deploys when GitHub changes
- Complete the CD (Continuous Delivery) part of CI/CD

Full pipeline will be:
```
git push → GitHub Actions builds image → ArgoCD deploys to k3s
```
