# Session 03 — Docker Compose + Flask + Nginx Reverse Proxy
**Date:** June 16, 2026  
**Environment:** EVE-NG | Ubuntu 24.04 | Docker 29.5.3

---

## What We Built This Session

```
[Browser / curl]
       ↓
[Nginx container - port 80]  ← reverse proxy
       ↓
[Flask app container - port 5000]  ← Python web app
```

Two containers managed together by one `docker-compose.yml` file.  
This is a real production pattern used in most web applications.

---

## Files Created

```
session-03/
├── app.py              ← Python Flask application
├── requirements.txt    ← Python dependencies
├── Dockerfile          ← Build instructions for Flask image
├── nginx.conf          ← Nginx reverse proxy config
└── docker-compose.yml  ← Orchestrate both containers together
```

---

## File Contents

### app.py
```python
from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>Hello from Flask App!</h1><p>Running inside Docker container</p>'

@app.route('/health')
def health():
    return 'OK', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### requirements.txt
```
flask
```

### Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .
EXPOSE 5000
CMD ["python", "app.py"]
```

### nginx.conf
```nginx
server {
    listen 80;

    location / {
        proxy_pass http://flask-app:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### docker-compose.yml
```yaml
services:
  flask-app:
    build: .
    container_name: flask-app
    ports:
      - "5000:5000"

  nginx:
    image: nginx:latest
    container_name: nginx-proxy
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - flask-app
```

---

## Commands Used

```bash
# Start all containers
docker compose up -d

# Check status
docker compose ps

# Test Flask directly
curl http://localhost:5000

# Test through Nginx proxy
curl http://localhost

# Stop all containers
docker compose down

# Restart
docker compose down && docker compose up -d
```

---

## Key Concepts Learned

| Concept | Explanation |
|---------|-------------|
| **Docker Compose** | Tool to define and run multi-container apps |
| **services** | Each container defined as a service in compose file |
| **build: .** | Build image from Dockerfile in current directory |
| **image:** | Use a pre-built image directly |
| **volumes** | Mount host file into container |
| **depends_on** | Start flask-app before nginx |
| **reverse proxy** | Nginx receives request, forwards to Flask internally |
| **proxy_pass** | Nginx directive to forward traffic to another service |

---

## Why Reverse Proxy Matters

Without reverse proxy:
```
User → Flask:5000 directly
```

With Nginx reverse proxy:
```
User → Nginx:80 → Flask:5000
```

Benefits:
- Users only see port 80 (standard HTTP)
- Flask is hidden from outside world
- Nginx handles SSL, caching, load balancing
- This is how every real production app works

---

## Docker Compose vs Manual Docker

| Manual Docker | Docker Compose |
|---------------|----------------|
| `docker run` each container separately | `docker compose up` starts everything |
| Manage each container individually | Manage all containers as one unit |
| Easy to forget steps | Everything defined in one file |
| Hard to share setup | Share `docker-compose.yml` file |

---

## Real Output

```
NAME          IMAGE                  COMMAND           STATUS
flask-app     session-03-flask-app   "python app.py"   Up
nginx-proxy   nginx:latest           "/docker-entry…"  Up
```

```
$ curl http://localhost
<h1>Hello from Flask App!</h1><p>Running inside Docker container</p>
```

---

## GitHub Push

```bash
cd ~/devops-lab
git add .
git commit -m "Session 03: Docker Compose - Flask app + Nginx reverse proxy"
git push
```

**Commit:** 5 files changed — Dockerfile, app.py, docker-compose.yml, nginx.conf, requirements.txt

---

## Session 04 Preview — Kubernetes with k3s

Next session we will:
- Set up 3 Ubuntu VMs in EVE-NG (1 master + 2 workers)
- Install k3s on all 3 nodes
- Join worker nodes to master
- Deploy our Flask app as a Kubernetes deployment
- Scale pods across the cluster
- Learn: pods, deployments, services, kubectl commands
