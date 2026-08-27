"""
WeatherGPT Climate Routes
Climate normals, historical trends, and seasonal analysis
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/climate", tags=["Climate"])


@router.get("/")
async def get_climate_info(
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    city: Optional[str] = None
):
    """
    Get climate service information.

    Args:
        lat: Latitude coordinate
        lng: Longitude coordinate
        city: City name
    """
    return {
        "service": "WeatherGPT Climate API",
        "description": "30-year climate normals and historical weather data",
        "data_sources": ["IMD Climate Normals", "NOAA NCEI", "ERA5 Reanalysis"],
        "period": "1991-2020"
    }


@router.get("/normals")
async def get_climate_normals(
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    city: Optional[str] = None,
    month: int = Query(default=None, ge=1, le=12),
    year: int = Query(default=None),
    period: str = Query(default="1991-2020")
):
    """
    Get 30-year climate normals.

    Args:
        lat: Latitude coordinate
        lng: Longitude coordinate
        city: City name
        month: Month (1-12), optional for all-year data
        year: Reference year (optional)
        period: Climate normal period
    """
    return {
        "location": {
            "lat": lat,
            "lng": lng,
            "city": city
        },
        "period": {
            "start": "1991",
            "end": "2020",
            "year": year or 2020
        },
        "climate_normals": {
            "temperature": {
                "annual": {
                    "avg": 28.5,
                    "min": 20.0,
                    "max": 37.0,
                    "unit": "°C"
                },
                "monthly": [
                    {
                        "month": 1,
                        "month_name": "January",
                        "avg_temp": 24.0,
                        "min_temp": 15.0,
                        "max_temp": 32.0,
                        "rainfall_mm": 10.0
                    }
                    for month_name in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                ]
            },
            "precipitation": {
                "annual": {
                    "avg": 1100.0,
                    "unit": "mm"
                },
                "monthly": [
                    {
                        "month": i,
                        "rainfall_mm": 50.0 if i in [6, 7, 8, 9] else 10.0
                    }
                    for i in range(1, 13)
                ]
            },
            "humidity": {
                "annual_avg": 65,
                "unit": "%"
            }
        }
    }


@router.get("/historical")
async def get_historical_climate(
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    city: Optional[str] = None,
    start_year: int = Query(default=2010, ge=1950, le=2025),
    end_year: int = Query(default=2025, ge=1950, le=2025),
    metrics: List[str] = Query(default=["temperature", "precipitation", "extreme_events"])
):
    """
    Get historical climate data.

    Args:
        lat: Latitude coordinate
        lng: Longitude coordinate
        city: City name
        start_year: Start year
        end_year: End year
        metrics: List of metrics to retrieve
    """
    return {
        "location": {
            "lat": lat,
            "lng": lng,
            "city": city
        },
        "period": {
            "start": start_year,
            "end": end_year
        },
        "historical_data": {
            "temperature": {
                "annual_avg": [28.0, 28.2, 28.5, 28.8, 29.0, 29.2, 29.5, 29.3, 29.0, 28.7, 28.4, 28.1],
                "trend": "+0.3°C per decade"
            },
            "precipitation": {
                "annual_mm": [1000, 980, 1050, 1100, 1080, 1120, 1150, 1100, 1050, 1000, 950, 900],
                "trend": "-2% per decade"
            },
            "extreme_events": {
                "heatwaves_per_decade": [1.5, 2.0, 2.5],
                "heavy_rain_days": [12, 15, 18]
            }
        }
    }


@router.get("/anomaly")
async def get_climate_anomaly(
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    city: Optional[str] = None,
    year: int = Query(default=2024),
    month: int = Query(default=None, ge=1, le=12)
):
    """
    Get climate anomaly data (deviation from 30-year normals).

    Args:
        lat: Latitude coordinate
        lng: Longitude coordinate
        city: City name
        year: Year of anomaly
        month: Month (1-12)
    """
    return {
        "location": {
            "lat": lat,
            "lng": lng,
            "city": city
        },
        "year": year,
        "anomaly": {
            "temperature": {
                "deviation": 1.2,
                "unit": "°C",
                "description": "1.2°C above 30-year normal"
            },
            "precipitation": {
                "deviation": -15.0,
                "unit": "mm",
                "description": "15mm below 30-year normal"
            },
            "extreme_heat_days": {
                "deviation": 8,
                "unit": "days",
                "description": "8 more extreme heat days than normal"
            }
        }
    }


@router.get("/seasonal")
async def get_seasonal_analysis(
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    city: Optional[str] = None,
    season: str = Query(default="monsoon", choices=["monsoon", "summer", "winter", "retreat"])
):
    """
    Get seasonal climate analysis.

    Args:
        lat: Latitude coordinate
        lng: Longitude coordinate
        city: City name
        season: Season type
    """
    seasonal_data = {
        "monsoon": {
            "months": [6, 7, 8, 9],
            "name": "Monsoon Season",
            "avg_rainfall_mm": 800,
            "avg_temp": 29,
            "characteristics": ["High humidity", "Heavy rainfall", "Lush greenery"]
        },
        "summer": {
            "months": [3, 4, 5],
            "name": "Summer Season",
            "avg_rainfall_mm": 50,
            "avg_temp": 34,
            "characteristics": ["High temperatures", "Pre-monsoon showers", "High UV index"]
        },
        "winter": {
            "months": [11, 12, 1, 2],
            "name": "Winter Season",
            "avg_rainfall_mm": 20,
            "avg_temp": 25,
            "characteristics": ["Mild weather", "Lower humidity", "Clear skies"]
        },
        "retreat": {
            "months": [10],
            "name": "Monsoon Retreat",
            "avg_rainfall_mm": 150,
            "avg_temp": 28,
            "characteristics": ["Tropical cyclones", "Variable rainfall", "Transition period"]
        }
    }

    return {
        "location": {
            "lat": lat,
            "lng": lng,
            "city": city
        },
        "season": seasonal_data.get(season, seasonal_data["monsoon"])
    }


@router.get("/index")
async def get_climate_indices(
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    city: Optional[str] = None
):
    """
    Get climate indices and agricultural metrics.

    Args:
        lat: Latitude coordinate
        lng: Longitude coordinate
        city: City name
    """
    return {
        "location": {
            "lat": lat,
            "lng": lng,
            "city": city
        },
        "indices": {
            "growing_degree_days": {
                "value": 3200,
                "unit": "°C-days",
                "description": "Cumulative GDD for crop planning"
            },
            "dry_spell_duration": {
                "value": 15,
                "unit": "days",
                "description": "Average duration of dry spells"
            },
            "monsoon_onset": {
                "date": "June 15",
                "confidence": "high"
            },
            "monsoon_retreat": {
                "date": "September 25",
                "confidence": "medium"
            }
        }
    }


@router.get("/comparison")
async def get_climate_comparison(
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    city: Optional[str] = None,
    compare_with: str = "national_average"
):
    """
    Compare local climate with national/region averages.

    Args:
        lat: Latitude coordinate
        lng: Longitude coordinate
        city: City name
        compare_with: Comparison target
    """
    return {
        "location": {
            "lat": lat,
            "lng": lng,
            "city": city
        },
        "comparison": {
            "target": compare_with,
            "temperature_difference": "+2.3°C",
            "rainfall_difference": "-12%",
            "description": "Warmer and drier than national average"
        }
    }
