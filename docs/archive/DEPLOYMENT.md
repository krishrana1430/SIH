# WeatherGPT Deployment Guide

## Quick Start

```bash
# 1. Clone and enter directory
cd weather-gpt

# 2. Copy environment template
cp .env.example .env

# 3. Add your API keys (edit .env)
#    - LLM_PRIMARY_API_KEY (Groq or Gemini)
#    - LLM_SECONDARY_API_KEY (backup provider)

# 4. Start all services
docker-compose up -d

# 5. Verify deployment
curl http://localhost:8000/health
# Expected: {"status": "healthy", ...}
```

---

## Architecture Overview

```
┌──────────────────┐
│   Frontend       │  Next.js 14 (Port 3000)
│   (PWA)          │  TypeScript + Tailwind CSS
└────────┬─────────┘
         │ HTTPS
┌────────▼─────────┐
│  API Gateway    │  FastAPI (Port 8000)
│  /api/v1/*      │  CORS, Rate Limiting, Routing
└────────┬─────────┘
         │
┌────────▼──────────────────────────────────────┐
│  LLM Query Engine (Three-tier fallback)       │
│                                                │
│  Tier A: Groq (cloud, free)                   │
│  Tier B: Gemini (cloud, free)                 │
│  Tier C: Ollama (local, offline)              │
│                                                │
│  Step 1: Intent Extraction (JSON output)       │
│  Step 2: Grounded Response Generation         │
└────────┬──────────────────┬────────────────────┘
         │                  │
         ▼                  ▼
┌──────────────────┐   ┌─────────────────┐
│ Open-Meteo API   │   │  Nominatim      │
│ (live weather)   │   │  (geocoding)    │
└──────────────────┘   └─────────────────┘
```

---

## Environment Variables

Required variables in `.env`:

| Variable | Required | Description |
|----------|----------|-------------|
| `LLM_PRIMARY_API_KEY` | **Yes** | Groq or Gemini API key |
| `LLM_PRIMARY_BASE_URL` | No | Groq default: `https://api.groq.com/openai/v1` |
| `LLM_PRIMARY_MODEL` | No | Default: `llama-3.1-70b-versatile` |
| `LLM_SECONDARY_API_KEY` | No | Backup LLM key (Gemini) |
| `LLM_SECONDARY_BASE_URL` | No | Default: `https://generativelanguage.googleapis.com/v1beta/openai/` |
| `LLM_SECONDARY_MODEL` | No | Default: `gemini-1.5-flash` |
| `LLM_FALLBACK_BASE_URL` | No | Default: `http://ollama:11434/v1` |
| `DATABASE_URL` | No | PostgreSQL connection string |
| `REDIS_URL` | No | Redis connection string |

> **Note:** At minimum, configure `LLM_PRIMARY_API_KEY` for basic functionality. Secondary and fallback tiers are optional but recommended for demo resilience.

---

## Docker Deployment

### Full Docker Compose (Recommended)

```bash
docker-compose up -d
```

This starts:
- **backend** — FastAPI app (port 8000)
- **postgres** — TimescaleDB (port 5432)
- **redis** — Cache (port 6379)
- **frontend** — Next.js app (port 3000)

### Simplified (Backend Only)

```bash
docker-compose -f docker-compose.simplified.yml up -d
```

Starts only backend + database (useful when developing frontend locally).

### Local Development Mode

```bash
# Backend with hot reload
uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000

# Or with Docker:
docker-compose -f docker-compose.local.yml up
```

---

## Kubernetes Deployment

For production scaling, use Kubernetes. See `infra/k8s/` for manifests.

### Quick K8s Setup

```bash
# Create namespace
kubectl apply -f infra/k8s/namespace.yaml

# Apply other manifests
kubectl apply -f infra/k8s/
```

### K8s Components
- **Deployment** — Backend app with horizontal auto-scaling
- **Service** — Load balancer for API access
- **ConfigMap** — Non-secret configuration
- **Secret** — API keys (use your own)
- **Ingress** — HTTPS routing with TLS
- **PostgreSQL StatefulSet** — Persistent database

### Kubernetes → Docker Compose Mapping

| K8s Resource | Docker Compose Service |
|---|---|
| `backend-deployment.yaml` | `backend` |
| `postgres-statefulset.yaml` | `postgres` |
| `redis-deployment.yaml` | `redis` |
| `frontend-deployment.yaml` | `frontend` |
| `ingress.yaml` | `nginx-proxy` (manual) |

---

## Production Considerations

### 1. LLM Rate Limits

| Provider | Free Tier | Rate Limit | Cost |
|----------|-----------|------------|------|
| Groq | Yes (1000 req/day) | 30 req/min | Free |
| Gemini | Yes | 15 req/min | Free |
| Ollama | Local | Unlimited | Free |

**Mitigation:** Implement Redis caching for repeated queries (~5 second cached responses for same location+query).

### 2. API Key Management

```bash
# Generate a secure key
openssl rand -hex 32

# For production, use a secrets manager:
# AWS Secrets Manager, GCP Secret Manager, or HashiCorp Vault
```

### 3. Caching Strategy

Enable Redis caching for:
- **Weather data:** Cache for 5 minutes (weather doesn't change rapidly)
- **Intent extraction:** Cache for 30 minutes (same query → same intent)
- **Geocoding:** Cache indefinitely (city coordinates don't change)

```python
# Example Redis key patterns
weather:{lat}:{lng}:current
intent:{query_hash}
geocode:{normalized_city_name}
```

### 4. Monitoring & Observability

The system logs which LLM tier served each request:
```bash
# View logs to see tier usage
docker-compose logs backend | grep "tier:"

# Example output:
# INFO - ✓ LLM call successful (tier: primary)
# WARNING - Primary LLM tier failed: ...
# INFO - ✓ LLM call successful (tier: secondary)
```

**Recommended production monitoring:**
- Prometheus metrics endpoint (`/metrics`)
- Grafana dashboard for request latency & tier usage
- Sentry for error tracking
- Health check endpoint (`/health`)

### 5. SSL/TLS

In production, always use HTTPS. Configure via:
- **Docker:** Use nginx-proxy or Traefik as reverse proxy
- **K8s:** Ingress with TLS termination
- **Cloud:** Use provider's load balancer (AWS ALB, GCP Load Balancer)

### 6. Database Security

- Change default PostgreSQL password
- Enable SSL connections
- Restrict network access (use security groups / VPC)
- Regular backups (WAL-G or cloud provider snapshots)

---

## Scaling

### Horizontal Scaling (Stateless Backend)

The backend has no in-process session state — it's stateless and horizontally scalable:

```yaml
# docker-compose.yml
replicas: 3  # Scale backend

# K8s
kubectl scale deployment weathergpt-backend --replicas=3
```

### Database Scaling

- **Read replicas:** Add read replicas for high-read workloads
- **Connection pooling:** Use PgBouncer between app and Postgres
- **TimescaleDB:** Automatic partitioning for time-series data

---

## Deployment Checklist

**Before first deploy:**
- [ ] Get API keys from Groq and/or Gemini
- [ ] Copy `.env.example` → `.env` and fill in keys
- [ ] Set `API_SECRET_KEY` to a secure random value
- [ ] (Optional) Configure Ollama for offline fallback

**After deploy:**
- [ ] `curl http://localhost:8000/health` → `{"status": "healthy"}`
- [ ] `curl -X POST http://localhost:8000/api/v1/ask -d '{"query":"Weather in Mumbai?"}'`
- [ ] Check logs: `docker-compose logs backend`
- [ ] Verify LLM tier usage in logs
- [ ] Test fallback by invalidating primary key

**For production:**
- [ ] Remove `--reload` from uvicorn command
- [ ] Use gunicorn with multiple workers
- [ ] Enable HTTPS (nginx/Traefik)
- [ ] Set up SSL certificates (Let's Encrypt)
- [ ] Configure firewall rules
- [ ] Set up monitoring (Prometheus + Grafana)
- [ ] Set up alerting (Alertmanager or equivalent)

---

## Troubleshooting

### Backend fails to start

```bash
# Check if .env is configured
cat .env | grep LLM_

# Test backend directly (without Docker)
pip install -r requirements.txt
uvicorn backend.api.main:app --reload --port 8000
```

### LLM provider errors

```bash
# Check if API key is valid
curl -H "Authorization: Bearer $LLM_PRIMARY_API_KEY" \
  https://api.groq.com/openai/v1/models

# Check tier configuration
curl http://localhost:8000/api/v1/status | jq '.integrations.llm'
```

### Frontend can't connect to API

```bash
# Check if backend is running
curl http://localhost:8000/health

# Check CORS (should allow localhost:3000)
curl -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -X OPTIONS http://localhost:8000/api/v1/ask
```

### Weather data errors

```bash
# Check if Open-Meteo is accessible
curl "https://api.open-meteo.com/v1/forecast?latitude=19.076&longitude=72.8777&current=temperature_2m"
```

---

## Demo Script

For hackathon judging:

1. **Start services:**
   ```bash
   docker-compose up -d
   ```

2. **Show architecture:**
   ```
   http://localhost:8000/docs  # Interactive API docs
   http://localhost:3000       # Web frontend
   ```

3. **Demonstrate provider fallback:**
   - Make a query, note `"llm_tier_used": "primary"`
   - Invalidate primary key in `.env`, restart backend
   - Make same query → `"llm_tier_used": "secondary"`

4. **Demonstrate role-aware output:**
   - Ask: "Weather in Mumbai?"
   - Switch role to "Farmer" → get agricultural-focused response
   - Switch role to "Pilot" → get aviation briefing

5. **Demonstrate severity alerts:**
   - Query a location with extreme weather (check /alerts)
   - Show color-coded alert banner in UI

6. **Demonstrate multilingual:**
   - Ask in Hindi: "मुंबई में मौसम कैसा है?"
   - Response comes back in Hindi

---
