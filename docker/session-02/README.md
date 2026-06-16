# Session 02 — Dockerfile & Docker Hub
**Date:** June 16, 2026  
**Environment:** EVE-NG | Ubuntu 24.04 | Docker 29.5.3

---

## What We Did This Session

1. Ran official Nginx container from Docker Hub
2. Explored inside a running container
3. Wrote a custom Dockerfile
4. Built a custom image
5. Ran our own custom container
6. Pushed image to Docker Hub

---

## Step 1 — Run Official Nginx Container

```bash
docker run -d -p 80:80 --name mynginx nginx
docker ps
curl http://localhost
```

**Key flags:**
| Flag | Meaning |
|------|---------|
| `-d` | Run in background (detached) |
| `-p 80:80` | Map host port 80 → container port 80 |
| `--name` | Give container a name |

---

## Step 2 — Explore Inside Container

```bash
docker exec -it mynginx bash

# Inside container
ls /etc/nginx
cat /etc/nginx/nginx.conf
ls /usr/share/nginx/html

exit
```

**Key learning:** Nginx serves files from `/usr/share/nginx/html/` not `/var/www/html/`

---

## Step 3 — Write Dockerfile

```bash
mkdir -p ~/devops-lab/docker/session-02
cd ~/devops-lab/docker/session-02
nano index.html
```

**index.html:**
```html
<!DOCTYPE html>
<html>
<head>
  <title>My DevOps Lab</title>
</head>
<body>
  <h1>Hello from bosamart DevOps Lab!</h1>
  <p>Built with Docker on EVE-NG</p>
</body>
</html>
```

```bash
nano Dockerfile
```

**Dockerfile:**
```dockerfile
FROM nginx:latest
COPY index.html /usr/share/nginx/html/index.html
EXPOSE 80
```

**Dockerfile instructions:**
| Instruction | Meaning |
|-------------|---------|
| `FROM` | Base image to build from |
| `COPY` | Copy file from host into image |
| `EXPOSE` | Document which port the container uses |

---

## Step 4 — Build Custom Image

```bash
# Stop and remove old container first
docker stop mynginx
docker rm mynginx

# Build image from Dockerfile
docker build -t bosamart-nginx:v1 .

# Verify image created
docker images
```

**Output:**
```
IMAGE              ID             DISK USAGE
bosamart-nginx:v1  ad4413396085   238MB
```

---

## Step 5 — Run Custom Image

```bash
docker run -d -p 80:80 --name my-custom-nginx bosamart-nginx:v1
curl http://localhost
```

**Output:** Served our custom HTML page — not default Nginx page ✅

---

## Step 6 — Push to Docker Hub

```bash
# Login to Docker Hub
docker login
# Username: samathbo

# Tag image with Docker Hub username
docker tag bosamart-nginx:v1 samathbo/bosamart-nginx:v1

# Push to Docker Hub
docker push samathbo/bosamart-nginx:v1
```

**Image now live at:** `hub.docker.com/r/samathbo/bosamart-nginx`

Anyone can now pull your image:
```bash
docker pull samathbo/bosamart-nginx:v1
```

---

## Step 7 — Push to GitHub

```bash
cd ~/devops-lab
git add .
git commit -m "Session 02: Dockerfile built and pushed to Docker Hub"
git push
```

---

## Key Commands Reference

```bash
docker run -d -p 80:80 --name mycontainer image:tag   # Run container
docker ps                                               # List running containers
docker ps -a                                            # List all containers
docker exec -it mycontainer bash                        # Enter container
docker stop mycontainer                                 # Stop container
docker rm mycontainer                                   # Remove container
docker build -t imagename:tag .                         # Build image
docker images                                           # List images
docker tag image:tag username/image:tag                 # Tag for Docker Hub
docker push username/image:tag                          # Push to Docker Hub
docker pull username/image:tag                          # Pull from Docker Hub
```

---

## Concepts Learned

| Concept | Explanation |
|---------|-------------|
| **Image** | Blueprint — like a template. Read only |
| **Container** | Running instance of an image |
| **Dockerfile** | Recipe to build a custom image |
| **Docker Hub** | Public registry to store and share images |
| **Port mapping** | `-p host:container` connects outside world to container |
| **docker exec** | Run commands inside a running container |

---

## Docker Hub Info

| Item | Value |
|------|-------|
| Username | samathbo |
| Image | samathbo/bosamart-nginx:v1 |
| URL | hub.docker.com/r/samathbo/bosamart-nginx |

---

## Session 03 Preview — Docker Compose

Next session we will:
- Run multiple containers together with `docker-compose.yml`
- Set up Flask app + Nginx as reverse proxy
- Connect containers using Docker networks
- Prepare for Kubernetes cluster setup
