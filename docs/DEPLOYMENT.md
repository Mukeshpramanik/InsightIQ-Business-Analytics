# InsightIQ — Production Deployment Guide

This guide provides end-to-end instructions for deploying **InsightIQ — Business Intelligence & Predictive Analytics Platform** across local containerized environments, cloud PaaS providers, and dedicated Linux servers.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Prerequisites](#2-prerequisites)
3. [Environment Configuration](#3-environment-configuration)
4. [Deployment Option A: Docker & Docker Compose (Recommended)](#4-deployment-option-a-docker--docker-compose-recommended)
5. [Deployment Option B: Dedicated Linux VPS (Systemd + Nginx + SSL)](#5-deployment-option-b-dedicated-linux-vps-systemd--nginx--ssl)
6. [Deployment Option C: Cloud PaaS (Render / Railway / Vercel)](#6-deployment-option-c-cloud-paas-render--railway--vercel)
7. [Database Persistence, Backup & Restoration](#7-database-persistence-backup--restoration)
8. [Security & Performance Hardening](#8-security--performance-hardening)
9. [Operational Health Checks & Monitoring](#9-operational-health-checks--monitoring)

---

## 1. Architecture Overview

InsightIQ is architected for zero external cloud runtime dependencies:

- **Frontend**: React 18 SPA compiled via Vite into static assets, with route-level code splitting, served via high-performance Nginx with HTTP compression and client-side caching.
- **Backend**: FastAPI REST API running on Python 3.11/3.12 with Uvicorn ASGI workers, background job processing, and formula-injection defenses.
- **Database**: Local SQLite 3 engine running in Write-Ahead Logging (`WAL`) mode with automatic foreign key enforcement and connection concurrency timeouts.
- **Analytics Engine**: In-process Scikit-learn, NumPy, Pandas, and SciPy pipelines for RFM segmentation, Ridge regression forecasting, and descriptive EDA.

```
 Client (Browser)
       │
       ▼
 ┌──────────────┐
 │ Nginx (Port 80)
 └──────┬───────┘
        ├──────────────────────────┐
        │ Static Assets (/assets)  │ Proxy /api/*
        ▼                          ▼
 ┌──────────────┐          ┌───────────────────────┐
 │ Built SPA    │          │ FastAPI API Server    │
 │ (HTML/JS/CSS)│          │ (Uvicorn - Port 8000) │
 └──────────────┘          └───────────┬───────────┘
                                       │
                                       ▼
                           ┌───────────────────────┐
                           │ SQLite Engine (WAL)   │
                           │ /data/insightiq.db    │
                           └───────────────────────┘
```

---

## 2. Prerequisites

### Containerized Deployment:
- Docker Engine 24.0+
- Docker Compose v2.20+

### Bare-Metal / VPS Deployment:
- Python 3.10, 3.11, or 3.12
- Node.js 18.x or 20.x and npm 9+
- Nginx 1.18+
- SQLite 3.35+

---

## 3. Environment Configuration

Copy the template configuration:

```bash
cp .env.example .env
```

### Environment Variables Reference

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `ENVIRONMENT` | `production` | Deployment mode (`development`, `staging`, `production`) |
| `PORT` | `8000` | Backend listening port |
| `HOST` | `0.0.0.0` | Backend bind interface |
| `DATABASE_PATH` | `/data/insightiq.db` | Absolute path to persistent SQLite database |
| `CORS_ORIGINS` | `http://localhost,http://localhost:80` | Comma-separated list of permitted origin URLs |
| `VITE_API_BASE_URL` | `/api` | Base API route used by the React client |

---

## 4. Deployment Option A: Docker & Docker Compose (Recommended)

### 4.1 Launch with Single Command

```bash
# Build and run containers in detached mode
docker compose up -d --build
```

### 4.2 Verify Service Status

```bash
# Check container status and health
docker compose ps

# Inspect backend logs
docker compose logs -f backend

# Inspect frontend logs
docker compose logs -f frontend
```

### 4.3 Access the Platform
- **Application Dashboard**: `http://localhost`
- **Backend API Docs**: `http://localhost:8000/docs`
- **Health Endpoint**: `http://localhost:8000/api/health`

### 4.4 Stopping the Stack

```bash
docker compose down
```
*(Database volume `insightiq_data` is preserved across restarts).*

---

## 5. Deployment Option B: Dedicated Linux VPS (Systemd + Nginx + SSL)

### 5.1 Clone & Prepare Environment

```bash
git clone <repo-url> /var/www/insightiq
cd /var/www/insightiq

# Setup backend Python virtual environment
python3 -m venv backend/venv
source backend/venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt
deactivate

# Build frontend static bundle
cd frontend
npm ci
npm run build
cd ..
```

### 5.2 Configure Systemd Service (`/etc/systemd/system/insightiq.service`)

```ini
[Unit]
Description=InsightIQ FastAPI Backend Service
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/insightiq
Environment="PATH=/var/www/insightiq/backend/venv/bin"
Environment="PYTHONPATH=/var/www/insightiq"
Environment="DATABASE_PATH=/var/www/insightiq/backend/insightiq.db"
Environment="ENVIRONMENT=production"
Environment="CORS_ORIGINS=https://yourdomain.com"
ExecStart=/var/www/insightiq/backend/venv/bin/uvicorn backend.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable insightiq
sudo systemctl start insightiq
sudo systemctl status insightiq
```

### 5.3 Configure Nginx Reverse Proxy (`/etc/nginx/sites-available/insightiq`)

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    client_max_body_size 30M;

    root /var/www/insightiq/frontend/dist;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml image/svg+xml;

    # Hashed static asset caching
    location ~* \.(?:css|js|woff2?|svg|png|jpg|ico)$ {
        expires 1y;
        add_header Cache-Control "public, max-age=31536000, immutable";
    }

    # API reverse proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Single Page App routing
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

Enable site and acquire SSL certificate:

```bash
sudo ln -s /etc/nginx/sites-available/insightiq /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Install Let's Encrypt SSL
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

---

## 6. Deployment Option C: Cloud PaaS (Render / Railway / Vercel)

### Render (Unified Web Service or Split)

1. **Backend Web Service**:
   - Runtime: `Python`
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT --workers 2`
   - Disk: Add a Persistent Disk mounted at `/data`
   - Env Vars: `DATABASE_PATH=/data/insightiq.db`, `ENVIRONMENT=production`, `PYTHONPATH=.`

2. **Frontend Static Site**:
   - Build Command: `npm run build` (Root: `frontend`)
   - Publish Directory: `dist`
   - Rewrite Rule: Source: `/*`, Destination: `/index.html`
   - Env Vars: `VITE_API_BASE_URL=https://<your-backend>.onrender.com/api`

---

## 7. Database Persistence, Backup & Restoration

InsightIQ uses SQLite 3 with Write-Ahead Logging (`WAL`). SQLite provides safe, zero-configuration atomic persistence.

### 7.1 Online Live Backup

Because WAL mode allows concurrent readers during writes, execute atomic live backups using SQLite's backup command:

```bash
# Execute safe live snapshot to backup location
sqlite3 backend/insightiq.db ".backup 'backend/insightiq_backup_$(date +%Y%m%d_%H%M%S).db'"
```

### 7.2 Automated Cron Backup (Daily at 02:00 AM)

```bash
0 2 * * * sqlite3 /var/www/insightiq/backend/insightiq.db ".backup '/var/backups/insightiq/insightiq_$(date +\%Y\%m\%d).db'"
```

### 7.3 Restoring from Backup

```bash
sudo systemctl stop insightiq
cp /var/backups/insightiq/insightiq_20261014.db /var/www/insightiq/backend/insightiq.db
sudo systemctl start insightiq
```

---

## 8. Security & Performance Hardening

### 8.1 Formula Injection Defense
Any CSV upload with leading formula tokens (`=`, `+`, `-`, `@`, `\t`, `\r`) is sanitized with prepended single quotes `'` to neutralize formula injection in exported Excel and CSV spreadsheets.

### 8.2 AST Query Parsing in SQL Lab
User-entered SQL queries are parsed using Python's `sqlglot` engine to guarantee:
- Read-only queries (`SELECT` only).
- Explicit prohibition of DML/DDL (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`).
- Single-statement enforcement (prevents semicolon chaining `; DROP TABLE`).
- Kernel-level SQLite URI mode (`?mode=ro`).

### 8.3 Injected HTTP Security Headers
All responses automatically include:
```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
```

---

## 9. Operational Health Checks & Monitoring

Verify the application health from any terminal or monitoring agent:

```bash
# JSON Health Probe
curl -s http://127.0.0.1:8000/api/health | jq .
```

Expected Response:
```json
{
  "status": "healthy",
  "timestamp": 1770000000.0,
  "database_records": 9994,
  "version": "1.0.0",
  "environment": "production"
}
```
