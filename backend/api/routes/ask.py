"""
WeatherGPT Ask Endpoint
Main conversational entrypoint - implements the three-layer query pipeline
"""

from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import logging
from sqlalchemy.orm import Session

from backend.services import (
    chat_service,
    geocoding_service,
    weather_service,
    llm_service,
    GeocodingError
)
from backend.services.conversation_service import conversation_service
from backend.models.db_config import get_db_dependency

logger = logging.getLogger(__name__)

router = APIRouter()


class AskRequest(BaseModel):
    """Request model for /api/ask endpoint."""
    query: str
    language: str = "en"
    role: str = "citizen"
    location_hint: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None  # Optional session ID in body


class AskResponse(BaseModel):
    """Response model for /api/ask endpoint."""
    query: str
    intent: Dict[str, Any]
    weather: Dict[str, Any]
    severity: Dict[str, Any]
    response: str
    language: str
    role: str
    grounding_source: str
    llm_tier_used: Optional[str]
    timestamp: str


@router.post("/ask", response_model=AskResponse)
async def ask_weather_question(
    request: AskRequest,
    session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    db: Session = Depends(get_db_dependency)
):
    """
    Process a natural language weather query.

    This is the main conversational endpoint implementing the three-layer pipeline:
    1. Intent + Entity Extraction (LLM call #1)
    2. Retrieval (geocode + fetch Open-Meteo data + classify severity)
    3. Grounded Response Generation (LLM call #2)

    Args:
        request: AskRequest with query, language, role
        session_id: User session ID (from X-Session-ID header or request body)
        db: Database session

    Returns:
        AskResponse with weather data, severity, and natural language response

    Example:
        POST /api/v1/ask
        Headers: X-Session-ID: <session-id>
        {
            "query": "Will it rain in Mumbai tomorrow?",
            "language": "en",
            "role": "farmer"
        }
    """
    start_time = datetime.utcnow()

    # Use session_id from header or request body (header takes precedence)
    effective_session_id = session_id or request.session_id or f"anon-{datetime.utcnow().timestamp()}"

    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    if request.role not in ["citizen", "farmer", "pilot", "disaster-manager"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid role. Must be one of: citizen, farmer, pilot, disaster-manager"
        )

    if request.language not in chat_service.get_supported_languages():
        logger.warning(f"Unsupported language '{request.language}', falling back to English")
        request.language = "en"

    try:
        # Step 1: Extract intent + entities (LLM call #1)
        logger.info(f"Processing query: '{request.query}' (role={request.role}, lang={request.language})")
        intent = await chat_service.extract_intent(request.query, request.language)

        # Step 2a: Geocode the place
        if intent.get("nationwide"):
            # For nationwide queries, use India's center coordinates
            lat, lng = 20.5937, 78.9629
            place_info = {
                "lat": lat,
                "lng": lng,
                "place_name": "India",
                "state": "",
                "country": "India",
                "source": "default"
            }
        else:
            place_name = intent.get("place", "Mumbai")
            try:
                place_info = await geocoding_service.geocode(place_name)
                lat, lng = place_info["lat"], place_info["lng"]
            except GeocodingError as e:
                logger.error(f"Geocoding failed: {e}")
                raise HTTPException(status_code=404, detail=f"Location '{place_name}' not found")

        # Step 2b: Fetch weather data from Open-Meteo
        weather_data = await weather_service.fetch_weather(lat, lng)

        # Step 2c: Classify severity
        severity = weather_service.classify_severity(weather_data)

        # Step 3: Generate grounded response (LLM call #2)
        combined_data = {
            **weather_data,
            "severity": severity,
            "place_info": place_info
        }

        response_text = await chat_service.generate_response(
            query=request.query,
            intent=intent,
            weather_data=combined_data,
            role=request.role,
            language=request.language
        )

        # Build response
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()

        logger.info(f"Query processed in {processing_time:.2f}s using LLM tier: {llm_service.last_tier_used}")

        # Save conversation history to database
        try:
            # Save user message
            conversation_service.add_message(
                session_id=effective_session_id,
                role="user",
                content=request.query,
                db=db,
                user_role=request.role,
                user_language=request.language,
                user_location=place_info.get("place_name")
            )

            # Save assistant response
            conversation_service.add_message(
                session_id=effective_session_id,
                role="assistant",
                content=response_text,
                db=db,
                query_metadata=intent,
                weather_data=weather_data,
                llm_tier_used=llm_service.last_tier_used,
                user_role=request.role,
                user_language=request.language,
                user_location=place_info.get("place_name")
            )

            # Update user preferences
            conversation_service.update_user_preferences(
                session_id=effective_session_id,
                db=db,
                language=request.language,
                role=request.role,
                location=place_info.get("place_name")
            )

            logger.info(f"Conversation history saved for session: {effective_session_id}")
        except Exception as e:
            # Don't fail the request if history saving fails
            logger.warning(f"Failed to save conversation history: {e}")

        return AskResponse(
            query=request.query,
            intent=intent,
            weather=weather_data,
            severity=severity,
            response=response_text,
            language=request.language,
            role=request.role,
            grounding_source="Open-Meteo",
            llm_tier_used=llm_service.last_tier_used,
            timestamp=end_time.isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process weather query: {str(e)}"
        )


@router.get("/ask/capabilities")
async def get_ask_capabilities():
    """
    Get capabilities of the /ask endpoint.

    Returns:
        Dict with supported languages, roles, and features
    """
    return {
        "supported_languages": chat_service.get_supported_languages(),
        "language_names": chat_service.get_language_names(),
        "supported_roles": chat_service.get_roles(),
        "features": [
            "Natural language query understanding",
            "Intent + entity extraction",
            "Live Open-Meteo data grounding",
            "Role-aware response generation",
            "Multilingual support (10 Indian languages)",
            "Severity classification",
            "Three-tier LLM provider fallback"
        ],
        "llm_tiers": llm_service.get_tier_info(),
        "data_source": "Open-Meteo API",
        "geocoding_source": "Nominatim (OpenStreetMap)"
    }


@router.get("/ask/examples")
async def get_example_queries():
    """
    Get example queries that work well with the /ask endpoint.

    Returns:
        Dict with example queries by category
    """
    return {
        "examples": {
            "current_weather": [
                "What's the weather like in Mumbai?",
                "Current temperature in Delhi",
                "How's the weather in Bangalore today?",
                "Is it raining in Chennai right now?"
            ],
            "forecast": [
                "Will it rain in Hyderabad tomorrow?",
                "What's the forecast for Pune this weekend?",
                "Weather prediction for Kolkata next week",
                "How hot will it be in Jaipur tomorrow?"
            ],
            "alerts": [
                "Any weather warnings for Mumbai?",
                "Are there storm alerts in my area?",
                "Is there a heat wave warning?",
                "Check for weather alerts in Chennai"
            ],
            "role_specific": {
                "farmer": [
                    "Should I irrigate my fields today in Nashik?",
                    "Is it good weather for planting in Aurangabad?",
                    "What's the rainfall forecast for my crops?"
                ],
                "pilot": [
                    "Flight weather briefing for Mumbai airport",
                    "What's the visibility and wind in Delhi?",
                    "Are there any weather hazards for flying today?"
                ],
                "disaster_manager": [
                    "Weather situation report for coastal Karnataka",
                    "Heavy rain risk assessment for Maharashtra",
                    "Emergency weather briefing for Tamil Nadu"
                ]
            },
            "multilingual": [
                "मुंबई में मौसम कैसा है? (Hindi)",
                "சென்னையில் மழை பெய்யுமா? (Tamil)",
                "ముంబై లో వాతావరణం ఎలా ఉంది? (Telugu)",
                "কলকাতায় আবহাওয়া কেমন? (Bengali)"
            ]
        }
    }
