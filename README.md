# WeatherGPT 🌤️

AI-powered weather forecasting assistant with multilingual support and role-based responses for Smart India Hackathon 2026.

## 🌟 Features

### Multi-Language Support
- **7 Indian Languages**: English, Hindi, Tamil, Telugu, Kannada, Bengali, Marathi
- Real-time language switching
- Natural language processing in user's preferred language

### Role-Based Responses
- **Citizen**: Everyday weather information for daily planning
- **Farmer**: Agricultural insights, crop-relevant forecasts
- **Pilot**: Aviation weather data, visibility, wind conditions
- **Emergency Services**: Critical weather alerts and risk assessment

### Voice Capabilities
- Voice input for hands-free queries
- Text-to-speech responses
- Supports multiple languages

### SMS Alerts
- Weather alert notifications via SMS
- Configurable alert thresholds
- Multi-language SMS support

### Real-Time Weather Data
- Current conditions and forecasts
- 7-day weather predictions
- Hourly updates
- Multiple Indian cities supported

## 🚀 Quick Start with Docker

### Prerequisites
- Docker & Docker Compose installed
- API keys (free):
  - [Groq API Key](https://console.groq.com) (Primary LLM)
  - [Gemini API Key](https://aistudio.google.com/app/apikey) (Fallback)

### Setup

1. **Clone the repository:**
```bash
git clone https://github.com/krishrana1430/SIH.git
cd SIH
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

3. **Start services:**
```bash
docker-compose up -d
```

4. **Access the application:**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🏗️ Architecture

```
WeatherGPT
├── Backend (Python FastAPI)
│   ├── LLM Chain (Groq → Gemini → Ollama)
│   ├── Weather Service (Open-Meteo API)
│   ├── Voice Service (Groq Whisper)
│   └── SMS Service (Twilio/Mock)
├── Frontend (Next.js + React)
│   ├── Chat Interface
│   ├── Weather Dashboard
│   └── Voice Input/Output
└── Database (SQLite)
    └── Conversation History
```

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11)
- **LLM**: Groq, Google Gemini
- **Weather Data**: Open-Meteo API
- **Database**: SQLite
- **Voice**: Groq Whisper (STT), Browser TTS

### Frontend
- **Framework**: Next.js 14
- **UI**: React, TailwindCSS
- **Components**: Shadcn/ui
- **Charts**: Recharts

### Infrastructure
- **Containerization**: Docker, Docker Compose
- **Deployment**: Ready for Kubernetes (config in `infra/k8s/`)

## 📚 Documentation

- [Setup Guide](./SETUP.md) - Detailed setup instructions
- [How to Run](./HOW_TO_RUN.md) - Quick start guide
- [API Documentation](./docs/API.md) - Complete API reference
- [Contributing](./CONTRIBUTING.md) - Contribution guidelines
- [Documentation Index](./DOCUMENTATION_INDEX.md) - All docs

## 🔧 Development

### Local Development (without Docker)

See [LOCAL_DEVELOPMENT.md](./LOCAL_DEVELOPMENT.md) for detailed instructions.

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r ../requirements.txt
python -m uvicorn backend.api.main:app --reload
```

**Frontend:**
```bash
cd frontend/web
npm install
npm run dev
```

### Environment Variables

Key environment variables (see `.env.example` for full list):

```bash
# Primary LLM (Groq - fast, free)
LLM_PRIMARY_API_KEY=your-groq-key
LLM_PRIMARY_MODEL=openai/gpt-oss-20b

# Secondary LLM (Gemini - fallback)
LLM_SECONDARY_API_KEY=your-gemini-key
LLM_SECONDARY_MODEL=gemini-2.0-flash

# API Configuration
API_SECRET_KEY=your-secret-key
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## 🧪 Testing

```bash
# Backend tests
python test_api.py
python test_llm.py

# Frontend tests
cd frontend/web
npm test
```

## 📱 Features in Detail

### Intelligent Weather Queries
- Natural language understanding
- Context-aware responses
- Historical data analysis
- Weather trend predictions

### Multi-City Support
- Major Indian cities pre-configured
- Custom location search
- Geolocation support

### Accessibility
- Screen reader compatible
- Keyboard navigation
- High contrast mode
- Voice interface

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

## 📄 License

This project is developed for Smart India Hackathon 2026.

## 👥 Team

SIH 2026 Team - WeatherGPT

## 🙏 Acknowledgments

- **Open-Meteo**: Free weather API
- **Groq**: Fast LLM inference
- **Google Gemini**: AI capabilities
- **Smart India Hackathon**: Opportunity and platform

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check [Documentation Index](./DOCUMENTATION_INDEX.md)

---

Built with ❤️ for Smart India Hackathon 2026
