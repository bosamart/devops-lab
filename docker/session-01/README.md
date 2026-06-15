# Session 01 - Docker Installation

## Environment
- EVE-NG Ubuntu 24.04
- Docker 29.5.3

## What was done
- Installed Docker using official install script
- Verified Docker running with docker version command
- Created GitHub repo and connected via SSH deploy key

## Commands used
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
docker --version
docker run hello-world
