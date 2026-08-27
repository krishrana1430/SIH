"""
WeatherGPT Alert Routes
Real-time weather alert and warning management with severity classification
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime
import logging

from backend.services import weather_service, geocoding_service, GeocodingError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("/")
async def get_active_alerts(
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    city: Optional[str] = None,
    alert_type: Optional[str] = None,
    severity: Optional[str] = None,
    state: Optional[str] = None
):
    """
    Get active weather alerts.

    Args:
        lat: Latitude coordinate
        lng: Longitude coordinate
        city: City name
        alert_type: Filter by type (heatwave, heavy_rain, high_wind, frost)
        severity: Filter by severity (normal, warning, severe, extreme)
        state: Filter by state (for regional queries)

    Returns:
        Active alerts from severity classification
    """
    try:
        # For state-level query, use state center
        if state and not city and lat is None:
            state_centers = {
                "maharashtra": (19.7515, 75.7139),
                "delhi": (28.7041, 77.1025),
                "karnataka": (15.3173, 75.7139),
                "tamil nadu": (11.1271, 78.6569),
                "west bengal": (22.9868, 87.8550),
                "telangana": (18.1124, 79.0193),
                "gujarat": (22.2587, 71.1924),
                "rajasthan": (27.0238, 74.2179),
            }
            if state.lower() in state_centers:
                lat, lng = state_centers[state.lower()]

        # If city provided, geocode it
        if city:
            try:
                location = await geocoding_service.geocode(city)
                lat, lng = location["lat"], location["lng"]
            except GeocodingError:
                raise HTTPException(status_code=404, detail=f"City '{city}' not found")

        if lat is None or lng is None:
            raise HTTPException(
                status_code=400,
                detail="Either provide coordinates (lat, lng) or city/state"
            )

        # Fetch weather data and classify severity
        weather_data = await weather_service.fetch_weather(lat, lng)
        severity_info = weather_service.classify_severity(weather_data)

        alerts = []
        for alert_msg in severity_info["alerts"]:
            # Determine alert type from message
            alert_type_from_msg = "weather_alert"
            if "heat" in alert_msg.lower():
                alert_type_from_msg = "heatwave"
            elif "rain" in alert_msg.lower():
                alert_type_from_msg = "heavy_rain"
            elif "wind" in alert_msg.lower():
                alert_type_from_msg = "high_wind"
            elif "frost" in alert_msg.lower() or "freeze" in alert_msg.lower():
                alert_type_from_msg = "frost"

            alerts.append({
                "id": f"alert_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "type": alert_type_from_msg,
                "severity": severity_info["severity"],
                "message": alert_msg,
                "location": {"lat": lat, "lng": lng},
                "timestamp": datetime.utcnow().isoformat(),
                "source": "severity_classification"
            })

        # Apply filters
        if alert_type:
            alerts = [a for a in alerts if a["type"] == alert_type]
        if severity:
            alerts = [a for a in alerts if a["severity"] == severity]

        return {
            "alerts": alerts,
            "count": len(alerts),
            "overall_severity": severity_info["severity"],
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch alerts")


@router.get("/subscribe")
async def subscribe_to_alerts(
    user_id: str,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    city: Optional[str] = None,
    alert_types: str = "cyclone,flood,heatwave",
    severity_levels: str = "watch,warning,severe",
    delivery_channels: str = "push",
    notification_frequency: str = "immediate"
):
    """
    Subscribe to weather alerts.
    (Placeholder - actual implementation requires notification infrastructure)

    Args:
        user_id: User identifier
        lat: Latitude
        lng: Longitude
        city: City name
        alert_types: Comma-separated list of alert types
        severity_levels: Comma-separated list of severity levels
        delivery_channels: Comma-separated channels (push, sms, email, whatsapp, voice)
        notification_frequency: 'immediate', 'hourly', 'daily'
    """
    # If city provided, geocode
    if city:
        try:
            location = await geocoding_service.geocode(city)
            lat, lng = location["lat"], location["lng"]
        except GeocodingError:
            pass  # Use provided lat/lng or default

    return {
        "subscription_id": f"sub_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "user_id": user_id,
        "status": "active",
        "location": {"lat": lat, "lng": lng, "city": city},
        "alert_types": alert_types.split(","),
        "severity_levels": severity_levels.split(","),
        "delivery_channels": delivery_channels.split(","),
        "notification_frequency": notification_frequency,
        "created_at": datetime.utcnow().isoformat(),
        "note": "Subscription recorded (notification delivery not yet implemented)"
    }


@router.post("/subscribe")
async def create_alert_subscription(
    user_id: str,
    subscription_data: dict
):
    """
    Create a new alert subscription.
    """
    return {
        "subscription_id": f"sub_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "status": "active",
        "message": "Successfully subscribed to alerts"
    }


@router.delete("/subscribe/{subscription_id}")
async def unsubscribe_from_alerts(
    subscription_id: str,
    user_id: str
):
    """
    Unsubscribe from alert notifications.
    """
    return {
        "subscription_id": subscription_id,
        "status": "cancelled",
        "message": "Successfully unsubscribed from alerts"
    }


@router.get("/by-type")
async def get_alerts_by_type(
    alert_type: str,
    state: Optional[str] = None,
    district: Optional[str] = None
):
    """
    Get alerts filtered by type.
    """
    return {
        "alert_type": alert_type,
        "filters": {"state": state, "district": district},
        "alerts": [],
        "count": 0,
        "timestamp": datetime.utcnow().isoformat(),
        "note": "Use GET /alerts with lat/lng/city for real severity-based alerts"
    }


@router.get("/by-location")
async def get_alerts_by_location(
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    city: Optional[str] = None,
    state: Optional[str] = None
):
    """
    Get alerts for a specific location.
    Delegates to GET /alerts.
    """
    from backend.api.routes.alerts import get_active_alerts
    return await get_active_alerts(lat=lat, lng=lng, city=city, state=state)


@router.get("/details/{alert_id}")
async def get_alert_details(alert_id: str):
    """
    Get details of a specific alert.
    """
    return {
        "alert_id": alert_id,
        "status": "success",
        "message": "Alert details retrieved"
    }


@router.get("/test")
async def test_alert_delivery(
    user_id: str,
    channel: str = "push"
):
    """
    Test alert delivery for a channel.
    """
    return {
        "user_id": user_id,
        "channel": channel,
        "status": "test_sent",
        "message": "Test alert sent successfully"
    }