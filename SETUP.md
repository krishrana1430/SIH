# WeatherGPT Setup Guide

Complete setup and deployment guide for WeatherGPT.

---

## 📋 Table of Contents

1. [Quick Start with Docker](#quick-start-with-docker)
2. [Local Development Setup](#local-development-setup)
3. [Environment Configuration](#environment-configuration)
4. [Production Deployment](#production-deployment)
5. [Troubleshooting](#troubleshooting)

---

## Quick Start with Docker

**Prerequisites:**
- Docker Desktop installed and running
- 4GB RAM minimum
- Groq API key (free from https://console.groq.com)

**Steps:**

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd weather-gpt
   ```

2. **Configure environment**
   ```bash
   cp .env.docker .env
   nano .env  # Add your Groq API key
   ```

3. **Start the application**
   ```bash
   docker-compose up -d
   ```

4. **Verify deployment**
   ```bash
   # Backend health check
   curl http://localhost:8000/health
   
   # Check running services
   docker-compose ps
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

---

## Local Development Setup

### Backend Setup

**Requirements:**
- Python 3.11+ (3.11, 3.12 recommended)
- pip package manager
- Virtual environment support

**Steps:**

1. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Activate virtual environment
   # Windows (Command Prompt):
   venv\Scripts\activate
   # Windows (PowerShell):
   venv\Scripts\Activate.ps1
   # Mac/Linux:
   source venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   nano .env  # Add your API keys
   ```

4. **Start backend server**
   ```bash
   # Development mode with auto-reload
   python start_server.py
   
   # Or with uvicorn directly
   uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
   ```

Backend will run on http://localhost:8000

### Frontend Setup

**Requirements:**
- Node.js 20+ (20 LTS recommended)
- npm 10+ package manager

**Steps:**

1. **Navigate to frontend directory**
   ```bash
   cd frontend/web
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment**
   ```bash
   # Windows (PowerShell):
   Set-Content .env.local "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1"
   # Mac/Linux:
   echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local
   # Or create the file manually with any text editor
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

Frontend will run on http://localhost:3000

---

## Environment Configuration

### Required Variables

```env
# LLM Integration (Required)
LLM_PRIMARY_API_KEY=your-groq-api-key-here
```

Get your Groq API key:
1. Visit https://console.groq.com
2. Sign up for a free account
3. Navigate to API Keys section
4. Create a new API key
5. Copy and paste into .env file

### Optional Variables

```env
# Secondary LLM (Recommended for fallback)
LLM_SECONDARY_API_KEY=your-gemini-api-key-here
LLM_SECONDARY_MODEL=gemini-1.5-flash

# Ollama Local LLM (Optional, for offline capability)
LLM_FALLBACK_BASE_URL=http://ollama:11434/v1
LLM_FALLBACK_MODEL=llama3.2:1b

# Database Configuration
DATABASE_URL=sqlite:///./data/weathergpt.db  # SQLite (default)
# DATABASE_URL=postgresql://user:pass@host:5432/weathergpt  # PostgreSQL

# SMS Alerts (Optional)
SMS_ENABLED=false
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+1234567890

# Voice Features
VOICE_STT_ENABLED=true
VOICE_TTS_ENABLED=true

# API Configuration
API_SECRET_KEY=your-random-secret-key-here
CORS_ORIGINS=["http://localhost:3000"]

# Application Settings
LOG_LEVEL=info
ENVIRONMENT=development
```

### Get Additional API Keys

**Gemini API Key (Optional):**
1. Visit https://aistudio.google.com/app/apikey
2. Sign in with Google account
3. Create API key
4. Add to .env as `LLM_SECONDARY_API_KEY`

**Twilio for SMS (Optional):**
1. Visit https://www.twilio.com/try-twilio
2. Sign up for free trial
3. Get Account SID, Auth Token, and Phone Number
4. Add credentials to .env

---

## Production Deployment

### Docker Compose (Recommended)

**Full stack deployment:**

```bash
# Build and start all services
docker-compose up -d

# Services included:
# - backend (FastAPI)
# - frontend (Next.js)
# - postgres (Database)
```

**Production environment variables:**

```env
ENVIRONMENT=production
LOG_LEVEL=warning
API_SECRET_KEY=<generate-secure-random-key>
DATABASE_URL=postgresql://user:pass@postgres:5432/weathergpt
CORS_ORIGINS=["https://your-domain.com"]
```

### Cloud Deployment Options

#### AWS Deployment
- **ECS/Fargate:** Use docker-compose.yml with ECS
- **Elastic Beanstalk:** Deploy as multi-container application
- **Lambda + API Gateway:** Serverless option for backend

#### GCP Deployment
- **Cloud Run:** Deploy containers directly
- **GKE:** Use Kubernetes for orchestration
- **App Engine:** Deploy as managed service

#### Azure Deployment
- **Container Instances:** Quick container deployment
- **AKS:** Kubernetes-based deployment
- **App Service:** Managed web app hosting

### Security Considerations

**Before deploying to production:**

1. **Change default secrets**
   ```bash
   # Generate secure API secret
   openssl rand -hex 32
   ```

2. **Use environment variables for sensitive data**
   - Never commit .env files to version control
   - Use cloud provider's secret management (AWS Secrets Manager, GCP Secret Manager, Azure Key Vault)

3. **Enable HTTPS**
   - Configure SSL/TLS certificates
   - Use Let's Encrypt for free certificates
   - Set up reverse proxy (nginx/Traefik)

4. **Configure firewall rules**
   - Restrict backend API access
   - Only expose necessary ports
   - Use security groups/network policies

5. **Set up monitoring**
   - Enable application logs
   - Set up health check monitoring
   - Configure alerting for errors

---

## Troubleshooting

### Common Issues

#### 1. Docker daemon not running
**Error:** `Cannot connect to Docker daemon`

**Solution:**
- Ensure Docker Desktop is installed and running
- Check system tray (Windows) or menu bar (Mac) for Docker icon
- Restart Docker Desktop if necessary

#### 2. Port already in use
**Error:** `Port 8000 already in use`

**Solution:**
```bash
# Find process using the port
# Windows (PowerShell):
netstat -ano | findstr :8000
taskkill /PID <process-id> /F

# Mac/Linux:
lsof -ti:8000 | xargs kill -9

# Or change the port in docker-compose.yml
```

#### 3. Invalid API key
**Error:** `Authentication failed` or `Invalid API key`

**Solution:**
- Verify API key is correctly copied to .env file
- Check for extra spaces or newlines
- Regenerate API key from provider console
- Restart services after updating .env

#### 4. Frontend can't connect to backend
**Error:** `Network Error` or `Failed to fetch`

**Solution:**
```bash
# Check backend is running
curl http://localhost:8000/health

# Check CORS configuration in backend
# Ensure frontend URL is in CORS_ORIGINS

# Verify .env.local in frontend/web/
# Windows (PowerShell):
Set-Content frontend/web/.env.local "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1"
# Mac/Linux:
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > frontend/web/.env.local

# Restart frontend
cd frontend/web && npm run dev
```

#### 5. Database connection errors
**Error:** `Could not connect to database`

**Solution:**
```bash
# For SQLite (default), ensure data directory exists
mkdir -p data

# For PostgreSQL, check connection string
# Verify postgres container is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres
```

#### 6. Build failures
**Error:** Build fails during `docker-compose up`

**Solution:**
```bash
# Clean rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d

# Check logs for specific errors
docker-compose logs backend
docker-compose logs frontend
```

#### 7. LLM provider timeouts
**Error:** `Request timeout` or `Provider unavailable`

**Solution:**
- Check internet connectivity
- Verify API key is valid
- Check provider status (https://status.groq.com)
- System will automatically fallback to secondary provider
- Check which tier is being used in logs:
  ```bash
  docker-compose logs backend | grep "tier:"
  ```

### Getting Help

**Check service health:**
```bash
# Backend health
curl http://localhost:8000/health

# Check all services
docker-compose ps

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

**Debug mode:**
```bash
# Enable debug logging
echo "LOG_LEVEL=debug" >> .env
docker-compose restart backend
```

**System requirements check:**
```bash
# Run automated system check
python system_check.py
```

---

## Useful Commands

### Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View logs (all services)
docker-compose logs -f

# View logs (specific service)
docker-compose logs -f backend

# Check service status
docker-compose ps

# Rebuild and restart
docker-compose up -d --build

# Stop and remove all data
docker-compose down -v

# Execute command in container
docker-compose exec backend bash
```

### Development Commands

```bash
# Backend (Python)
pip install -r requirements.txt
python start_server.py
uvicorn backend.api.main:app --reload

# Frontend (Node.js)
cd frontend/web
npm install
npm run dev
npm run build
npm run start

# Database migrations
python manage.py migrate

# Run tests
python -m pytest tests/
npm test
```

---

## Next Steps

After successful setup:

1. **Test the application**
   - Open http://localhost:3000
   - Try asking weather questions
   - Test different languages
   - Try different user roles

2. **Explore the API**
   - Visit http://localhost:8000/docs
   - Try example queries
   - Test different endpoints

3. **Customize configuration**
   - Add SMS credentials for alerts
   - Configure additional LLM providers
   - Adjust role-specific prompts

4. **Deploy to production**
   - Follow production deployment guide
   - Set up monitoring and logging
   - Configure backups

---

## Additional Resources

- **API Documentation:** [docs/API.md](docs/API.md)
- **Quick Start Guide:** [HOW_TO_RUN.md](HOW_TO_RUN.md)
- **Project README:** [README.md](README.md)
- **Interactive API Docs:** http://localhost:8000/docs (when running)

---

**Last Updated:** 2026-08-27
