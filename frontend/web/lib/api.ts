/**
 * WeatherGPT API Client
 * Centralized API calls to backend
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export interface AskResponse {
  query: string;
  intent: {
    place: string;
    language: string;
    intent: string;
    nationwide: boolean;
    confidence: number;
  };
  weather: {
    location: {
      lat: number;
      lng: number;
      timezone: string;
    };
    current: {
      temperature: number;
      apparent_temperature: number;
      humidity: number;
      precipitation: number;
      pressure: number;
      wind_speed: number;
      wind_direction: number;
      weather_code: number;
      time: string;
    };
    forecast: {
      days: Array<{
        date: string;
        temperature_max: number;
        temperature_min: number;
        precipitation_sum: number;
        precipitation_probability: number;
        wind_speed_max: number;
        weather_code: number;
      }>;
    };
    data_source: string;
    timestamp: string;
  };
  severity: {
    severity: string;
    alerts: string[];
    alert_count: number;
  };
  response: string;
  language: string;
  role: string;
  grounding_source: string;
  llm_tier_used: string | null;
  timestamp: string;
}

export interface WeatherData {
  location: {
    lat: number;
    lng: number;
    city?: string;
  };
  current: any;
  forecast?: any;
  data_source: string;
  timestamp: string;
}

/**
 * Main conversational endpoint - ask a weather question
 */
export async function askWeatherQuestion(
  query: string,
  language: string = 'en',
  role: string = 'citizen'
): Promise<AskResponse> {
  const response = await fetch(`${API_BASE}/ask`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query, language, role }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || 'Failed to fetch weather data');
  }

  return response.json();
}

/**
 * Get current weather for coordinates
 */
export async function getCurrentWeather(
  lat: number,
  lng: number
): Promise<WeatherData> {
  const response = await fetch(
    `${API_BASE}/weather/current?lat=${lat}&lng=${lng}`
  );

  if (!response.ok) {
    throw new Error('Failed to fetch current weather');
  }

  return response.json();
}

/**
 * Get current weather for city
 */
export async function getCurrentWeatherByCity(city: string): Promise<WeatherData> {
  const response = await fetch(
    `${API_BASE}/weather/current?city=${encodeURIComponent(city)}`
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch weather for ${city}`);
  }

  return response.json();
}

/**
 * Get 7-day forecast
 */
export async function getDailyForecast(
  lat: number,
  lng: number,
  days: number = 7
): Promise<any> {
  const response = await fetch(
    `${API_BASE}/weather/forecast/daily?lat=${lat}&lng=${lng}&days=${days}`
  );

  if (!response.ok) {
    throw new Error('Failed to fetch forecast');
  }

  return response.json();
}

/**
 * Get weather alerts for location
 */
export async function getWeatherAlerts(
  lat: number,
  lng: number
): Promise<any> {
  const response = await fetch(
    `${API_BASE}/weather/alerts?lat=${lat}&lng=${lng}`
  );

  if (!response.ok) {
    throw new Error('Failed to fetch alerts');
  }

  return response.json();
}

/**
 * Geocode a city name
 */
export async function geocodeCity(city: string): Promise<any> {
  const response = await fetch(
    `${API_BASE}/weather/geocode?city=${encodeURIComponent(city)}`
  );

  if (!response.ok) {
    throw new Error(`Failed to geocode ${city}`);
  }

  return response.json();
}

/**
 * Get API capabilities
 */
export async function getCapabilities(): Promise<any> {
  const response = await fetch(`${API_BASE}/ask/capabilities`);

  if (!response.ok) {
    throw new Error('Failed to fetch capabilities');
  }

  return response.json();
}

/**
 * Get example queries
 */
export async function getExampleQueries(): Promise<any> {
  const response = await fetch(`${API_BASE}/ask/examples`);

  if (!response.ok) {
    throw new Error('Failed to fetch examples');
  }

  return response.json();
}

/**
 * Get service status
 */
export async function getServiceStatus(): Promise<any> {
  const response = await fetch(`${API_BASE}/status`);

  if (!response.ok) {
    throw new Error('Failed to fetch service status');
  }

  return response.json();
}
