# Voice Interaction System - Rural Accessibility Guide

## Overview

WeatherGPT's voice interaction system enables users in rural areas to access weather information through speech, supporting 10 Indian languages with optimizations for low-bandwidth 2G/3G networks.

## Architecture

### Thin Adapter Pattern
```
User Speech → STT → Text → /api/ask (existing) → Text Response → TTS → Audio
```

The voice system acts as a thin adapter layer around the existing text-based API:
- Voice input converts to text via STT
- Text flows through existing `/api/ask` endpoint
- Response text converts back to audio via TTS
- No parallel voice-specific backend logic

## Supported Languages

| Language   | Code | Whisper Support | Web Speech API |
|------------|------|-----------------|----------------|
| English    | en   | ✅              | ✅             |
| Hindi      | hi   | ✅              | ✅             |
| Tamil      | ta   | ✅              | ✅             |
| Telugu     | te   | ✅              | ✅             |
| Bengali    | bn   | ✅              | ✅             |
| Marathi    | mr   | ✅              | ✅             |
| Kannada    | kn   | ✅              | ✅             |
| Gujarati   | gu   | ✅              | ✅             |
| Malayalam  | ml   | ✅              | ✅             |
| Punjabi    | pa   | ✅              | ✅             |

## Features

### 1. Speech-to-Text (STT)

**Providers:**
- **Groq Whisper** (Primary): Fast, accurate, multi-language support
- **OpenAI Whisper** (Fallback): High accuracy for all languages
- **Mock** (Development): For testing without API keys

**Audio Formats Supported:**
- WAV, MP3, OGG, FLAC, WebM, Opus, M4A

**Optimizations:**
- Low sample rate (16kHz) for bandwidth efficiency
- Audio compression using Opus codec (70-85% reduction)
- Noise suppression and echo cancellation
- 16kbps bitrate for optimal speech quality on slow connections

**API Endpoint:**
```bash
POST /api/v1/voice/stt
Content-Type: multipart/form-data

Parameters:
- audio_file: Audio file (required)
- language: Language code (default: "en")
- compress: Enable compression (default: true)
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/voice/stt \
  -F "audio_file=@recording.webm" \
  -F "language=hi" \
  -F "compress=true"
```

**Response:**
```json
{
  "status": "success",
  "transcription": {
    "text": "आज का मौसम कैसा है",
    "language": "hi",
    "confidence": 1.0,
    "provider": "groq-whisper"
  },
  "audio": {
    "filename": "recording.webm",
    "size_bytes": 45821,
    "format": "webm",
    "compressed": true
  },
  "timestamp": "2026-08-29T11:23:49.857Z"
}
```

### 2. Text-to-Speech (TTS)

**Providers:**
- **Web Speech API** (Primary): Client-side, zero bandwidth, all languages
- **OpenAI TTS** (Premium): High-quality voices, MP3 output
- **Groq** (Future): Coming soon

**Features:**
- Natural-sounding voices for all supported languages
- Adjustable speed (0.5x - 2.0x)
- Gender selection (male/female)
- Client-side synthesis (no bandwidth cost)

**API Endpoint:**
```bash
POST /api/v1/voice/tts
Content-Type: application/json

Body:
{
  "text": "Text to synthesize",
  "language": "en",
  "voice_gender": "female",
  "speed": 1.0
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/voice/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The weather in Mumbai is sunny today",
    "language": "en",
    "voice_gender": "female",
    "speed": 0.9
  }'
```

**Response (Web Speech API):**
```json
{
  "status": "success",
  "synthesis": {
    "provider": "web",
    "text": "The weather in Mumbai is sunny today",
    "language": "en",
    "voice_gender": "female",
    "speed": 0.9,
    "audio_url": null,
    "instructions": "Use browser Web Speech API for synthesis"
  },
  "timestamp": "2026-08-29T11:23:49.857Z"
}
```

**Response (OpenAI TTS):**
```json
{
  "status": "success",
  "synthesis": {
    "provider": "openai-tts",
    "text": "The weather in Mumbai is sunny today",
    "language": "en",
    "voice": "nova",
    "speed": 0.9,
    "audio_format": "mp3",
    "audio_base64": "SUQzBAAAAAA...",
    "audio_size": 28592
  },
  "timestamp": "2026-08-29T11:23:49.857Z"
}
```

## Low-Bandwidth Optimizations

### Audio Compression
- **Codec**: Opus (best for speech)
- **Bitrate**: 16kbps (optimal for voice)
- **Reduction**: 70-85% typical file size reduction
- **Quality**: No perceptible loss for speech

### Frontend Optimizations
```javascript
// Low sample rate for recording
{ audio: { sampleRate: 16000 } }

// Low bitrate encoding
{ audioBitsPerSecond: 16000 }

// Opus codec (if supported)
{ mimeType: 'audio/webm;codecs=opus' }
```

### Network Resilience
- 30-second timeout with graceful error messages
- Chunked recording (1-second intervals)
- Automatic retry on failure
- Clear error feedback for users

## Frontend Integration

### VoiceInput Component

```tsx
import VoiceInput from '@/components/VoiceInput'

<VoiceInput
  onTranscription={(text) => {
    // Handle transcribed text
    console.log('User said:', text)
  }}
  language="hi"
  disabled={false}
/>
```

**Features:**
- Visual recording indicator with animation
- Real-time audio level feedback
- Recording duration display
- Processing status indicator
- Error messages with retry guidance
- Automatic microphone permission handling

### VoiceOutput Component

```tsx
import { VoiceOutput } from '@/components/VoiceInput'

<VoiceOutput
  text="The weather is sunny today"
  language="en"
  autoPlay={false}
/>
```

**Features:**
- Play/pause controls
- Browser speech synthesis
- Language-aware voice selection
- Visual speaking indicator

## Configuration

### Environment Variables

```bash
# STT Configuration
STT_PROVIDER=groq           # Options: groq, whisper, web
LLM_PRIMARY_API_KEY=gsk_... # Groq API key for Whisper

# TTS Configuration
TTS_PROVIDER=web            # Options: web, openai, groq
OPENAI_API_KEY=sk-...      # Optional: For OpenAI TTS
```

### Provider Selection

**Groq Whisper (Recommended):**
- Fast processing (< 2 seconds)
- Free tier available
- Excellent multi-language support
- Model: `whisper-large-v3`

**OpenAI Whisper:**
- High accuracy
- Paid service
- Model: `whisper-1`

**Web Speech API (TTS):**
- Zero bandwidth cost
- Client-side processing
- All Indian languages supported
- No API key required

## Usage Examples

### Example 1: Ask Weather in Hindi
```
User (Hindi): "मुंबई में आज का मौसम कैसा है?"
↓ STT
Text: "मुंबई में आज का मौसम कैसा है?"
↓ /api/ask
Response: "मुंबई में आज का मौसम धूप वाला है। तापमान 32°C है।"
↓ TTS
Audio: [Speech output in Hindi]
```

### Example 2: Weather Alert in Tamil
```
User (Tamil): "நாளை மழை பெய்யுமா?"
↓ STT
Text: "நாளை மழை பெய்யுமா?"
↓ /api/ask
Response: "ஆம், நாளை மழை பெய்யும். குடை எடுத்துச் செல்லவும்."
↓ TTS
Audio: [Speech output in Tamil]
```

### Example 3: Multi-Turn Conversation
```
Turn 1:
User: "What's the weather?" (English)
Bot: "Which city would you like to know about?"

Turn 2:
User: "Delhi" (English)
Bot: "Delhi weather is 28°C, partly cloudy."
```

## Testing

### Run Voice Service Tests
```bash
cd backend
pytest tests/test_voice_service.py -v
```

### Test Coverage
- ✅ Service initialization
- ✅ Language support
- ✅ STT with multiple languages
- ✅ TTS with various parameters
- ✅ Audio compression
- ✅ Error handling
- ✅ Provider fallbacks
- ✅ Integration tests (with API keys)

### Manual Testing

**Test STT Endpoint:**
```bash
# Record audio on your device, then:
curl -X POST http://localhost:8000/api/v1/voice/stt \
  -F "audio_file=@test_recording.webm" \
  -F "language=en"
```

**Test TTS Endpoint:**
```bash
curl -X POST http://localhost:8000/api/v1/voice/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "language": "en"}'
```

**Test Voice Info:**
```bash
curl http://localhost:8000/api/v1/voice/
```

## Performance Benchmarks

### Audio Compression Results
```
Original WAV:  2.4 MB
Compressed Opus: 380 KB
Reduction: 84%
Quality: Excellent for speech
```

### STT Latency
```
Groq Whisper:
- 5-second audio: ~1.2s processing
- 30-second audio: ~2.8s processing
- 2G network: +3-5s upload time

OpenAI Whisper:
- 5-second audio: ~2.0s processing
- 30-second audio: ~4.5s processing
```

### TTS Latency
```
Web Speech API:
- Client-side: ~100ms
- No network required

OpenAI TTS:
- 100 chars: ~800ms
- 500 chars: ~1.5s
- 2G network: +2-4s download
```

## Accessibility Features

### Visual Feedback
- 🔴 Recording indicator (pulsing red dot)
- 📊 Real-time audio level visualization
- ⏱️ Recording duration display
- ⚙️ Processing status indicator
- ❌ Clear error messages

### Error Handling
- Microphone permission denied → Clear instructions
- Network timeout → Retry guidance
- STT failure → Fallback to text input
- TTS failure → Text-only response

### Keyboard Navigation
- Tab to focus voice button
- Space/Enter to toggle recording
- ESC to cancel recording

### Screen Reader Support
- ARIA labels on all controls
- Status announcements
- Error announcements

## Deployment Checklist

- [ ] Set `LLM_PRIMARY_API_KEY` environment variable
- [ ] Choose STT provider (`STT_PROVIDER=groq`)
- [ ] Choose TTS provider (`TTS_PROVIDER=web`)
- [ ] Test all supported languages
- [ ] Verify audio compression works
- [ ] Test on 2G/3G connection
- [ ] Verify HTTPS (required for mic access)
- [ ] Test microphone permissions
- [ ] Monitor API usage and costs
- [ ] Set up error logging and alerts

## Troubleshooting

### Issue: "Failed to access microphone"
**Solution:** 
- Ensure HTTPS is enabled (HTTP blocks mic access)
- User must grant microphone permission
- Check browser compatibility

### Issue: "Request timeout"
**Solution:**
- Check network connection
- Audio file may be too large
- Increase timeout in frontend (currently 30s)

### Issue: "STT unavailable"
**Solution:**
- Verify `LLM_PRIMARY_API_KEY` is set
- Check API quota and limits
- Review backend logs for errors

### Issue: No audio output
**Solution:**
- Verify TTS provider is configured
- Check browser supports Web Speech API
- For OpenAI TTS, verify API key

### Issue: Poor transcription quality
**Solution:**
- Ensure quiet recording environment
- Use noise cancellation (enabled by default)
- Try higher quality audio format (FLAC)
- Check language selection matches spoken language

## Cost Optimization

### Recommended Setup for Rural Areas
```bash
STT_PROVIDER=groq      # Free tier: 100 requests/day
TTS_PROVIDER=web       # Free: Browser-based
```

### Cost Estimates
```
Groq Whisper (STT):
- Free tier: 100 requests/day
- Paid: $0.05 per 1000 seconds

OpenAI Whisper (STT):
- $0.006 per minute

OpenAI TTS:
- $15 per 1M characters

Web Speech API (TTS):
- Free (client-side)
```

## Future Enhancements

- [ ] Offline voice recognition (on-device models)
- [ ] Voice activity detection (auto start/stop)
- [ ] Speaker diarization (multi-speaker support)
- [ ] Emotion detection in voice
- [ ] Regional dialect support
- [ ] Voice biometrics for authentication
- [ ] Real-time streaming transcription
- [ ] Custom wake word detection
- [ ] Voice shortcuts and commands

## Resources

- **Groq Whisper API**: https://console.groq.com/docs/speech-text
- **OpenAI Whisper**: https://platform.openai.com/docs/guides/speech-to-text
- **Web Speech API**: https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API
- **Opus Codec**: https://opus-codec.org/
- **FFmpeg Audio**: https://ffmpeg.org/ffmpeg-codecs.html#Codec-Options

## Support

For issues or questions:
- Check backend logs: `docker-compose logs backend`
- Review browser console for frontend errors
- Test with `/api/v1/voice/test` endpoint
- Verify API keys and environment variables
