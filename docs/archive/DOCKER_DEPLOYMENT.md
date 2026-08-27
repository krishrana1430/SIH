# WeatherGPT Docker Deployment Guide

## Quick Start (5 minutes)

### Prerequisites
- Docker Engine 20.10+ and Docker Compose 2.0+
- At least 2GB free RAM
- Groq API key (free from https://console.groq.com)

### Step 1: Clone and Configure

```bash
cd /home/piyushxdev/SIH/weather-gpt

# Copy environment file
cp .env.docker .env

# Edit .env and add your API keys
nano .env
```

**Required API Keys:**
- `LLM_PRIMARY_API_KEY` - Groq API key
- `LLM_SECONDARY_API_KEY` - Gemini API key (optional but recommended)

### Step 2: Build and Start

```bash
# Build images (first time only, takes 3-5 minutes)
docker-compose build

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

### Step 3: Verify

```bash
# Check backend health
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Step 4: Access

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## Architecture

```
┌─────────────────────────────────────────────┐
│           User Browser                      │
│         http://localhost:3000               │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│  Frontend Container (Next.js)                │
│  Port: 3000                                  │
│  - React UI                                  │
│  - Voice Input/Output                        │
│  - Responsive Design                         │
└──────────────┬───────────────────────────────┘
               │ API Calls
               ▼
┌──────────────────────────────────────────────┐
│  Backend Container (FastAPI)                 │
│  Port: 8000                                  │
│  - Weather API (Open-Meteo)                  │
│  - LLM Integration (Groq/Gemini)             │
│  - Conversation History (SQLite)             │
│  - Voice Service (STT/TTS)                   │
│  - SMS Alerts                                │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│  Data Volume                                 │
│  ./data/weathergpt.db (SQLite)              │
│  - User sessions                             │
│  - Conversation history                      │
│  - Alert history                             │
└──────────────────────────────────────────────┘
```

---

## Common Commands

### Start Services
```bash
# Start in foreground (see logs)
docker-compose up

# Start in background
docker-compose up -d

# Start specific service
docker-compose up -d backend
```

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Rebuild
```bash
# Rebuild specific service
docker-compose build backend

# Rebuild and restart
docker-compose up -d --build

# Force rebuild (no cache)
docker-compose build --no-cache
```

### Database Management
```bash
# Access SQLite database
docker-compose exec backend sqlite3 /app/data/weathergpt.db

# Backup database
docker-compose exec backend cat /app/data/weathergpt.db > backup.db

# View database files
docker-compose exec backend ls -lh /app/data/
```

### Health Checks
```bash
# Check all services
docker-compose ps

# Check backend health
curl http://localhost:8000/health

# Check backend status
curl http://localhost:8000/api/v1/status | jq

# Test API endpoint
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "Weather in Mumbai?", "language": "en", "role": "citizen"}'
```

---

## Configuration Options

### Use PostgreSQL Instead of SQLite

1. Uncomment postgres service in `docker-compose.yml`
2. Update `.env`:
   ```
   DATABASE_URL=postgresql://weathergpt:weathergpt_password@postgres:5432/weathergpt
   ```
3. Restart: `docker-compose up -d`

### Enable Redis Caching

1. Uncomment redis service in `docker-compose.yml`
2. Update `.env`:
   ```
   REDIS_URL=redis://redis:6379
   ```
3. Restart: `docker-compose up -d`

### Enable Ollama (Local LLM)

1. Uncomment ollama service in `docker-compose.yml`
2. Start: `docker-compose up -d ollama`
3. Pull model: `docker-compose exec ollama ollama pull llama3.2:1b`

### Enable SMS Alerts

Update `.env`:
```
SMS_ENABLED=true
SMS_PROVIDER=twilio
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=+1234567890
```

---

## Troubleshooting

### Backend not starting
```bash
# Check logs
docker-compose logs backend

# Common issues:
# - Missing API keys in .env
# - Port 8000 already in use: change port in docker-compose.yml
# - Database permissions: sudo chown -R 1000:1000 ./data
```

### Frontend not connecting to backend
```bash
# Check NEXT_PUBLIC_API_URL in .env
# Should be: http://localhost:8000/api/v1 (from host)
#         or http://backend:8000/api/v1 (from container)

# Restart frontend
docker-compose restart frontend
```

### Database errors
```bash
# Reset database
docker-compose down
rm -rf ./data/weathergpt.db
docker-compose up -d

# The database will be recreated automatically
```

### Out of memory
```bash
# Check Docker resources
docker stats

# Increase Docker memory limit in Docker Desktop settings
# Minimum: 2GB, Recommended: 4GB
```

### Port conflicts
```bash
# Find what's using the port
sudo lsof -i :8000

# Change ports in docker-compose.yml:
ports:
  - "8001:8000"  # Map to different host port
```

---

## Production Deployment

### Security Checklist
- [ ] Change `API_SECRET_KEY` in `.env`
- [ ] Set `API_DEBUG=false`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable HTTPS with reverse proxy (nginx/traefik)
- [ ] Add rate limiting
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Configure backups for database
- [ ] Use secrets management (Docker secrets/Vault)
- [ ] Update CORS origins in backend

### Example nginx Configuration
```nginx
server {
    listen 80;
    server_name weathergpt.example.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Environment-Specific Configs

Create separate compose files:
- `docker-compose.yml` - base configuration
- `docker-compose.dev.yml` - development overrides
- `docker-compose.prod.yml` - production overrides

Use: `docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d`

---

## Monitoring

### View Resource Usage
```bash
docker stats
```

### Check Container Health
```bash
docker-compose ps
docker inspect --format='{{.State.Health.Status}}' weathergpt-backend
```

### Export Logs
```bash
docker-compose logs > logs.txt
```

---

## Backup and Restore

### Backup
```bash
# Stop services
docker-compose down

# Backup data directory
tar -czf weathergpt-backup-$(date +%Y%m%d).tar.gz ./data

# Backup environment
cp .env .env.backup
```

### Restore
```bash
# Extract backup
tar -xzf weathergpt-backup-20260827.tar.gz

# Restore environment
cp .env.backup .env

# Start services
docker-compose up -d
```

---

## Development Mode

For development with hot reload:

```bash
# Use volume mounts (already configured)
docker-compose up

# Backend changes auto-reload
# Frontend changes require: docker-compose restart frontend
```

---

## Support

- **Documentation:** `/docs` in this repository
- **API Docs:** http://localhost:8000/docs
- **Issues:** Check logs with `docker-compose logs`
- **Hackathon:** SIH 2026 Problem Statement 26068

---

**Docker Deployment Complete!** 🐳
