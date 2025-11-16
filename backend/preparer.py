from datetime import datetime
from typing import Dict, Any, Optional, List

AQI_CATEGORIES = {
    1: "Good",
    2: "Fair", 
    3: "Moderate",
    4: "Poor",
    5: "Very Poor"
}

def get_mcp_resources() -> List[Dict[str, str]]:
    # MCP resource templates
    return [
        {
            "uriTemplate": "environment://air-quality/{lat}/{lon}",
            "name": "air-quality",
            "title": "Air Quality Data",
            "description": "Get current air quality index and pollutant levels for any location",
            "mimeType": "application/json"
        },
        {
            "uriTemplate": "environment://news/latest",
            "name": "environmental-news",
            "title": "Environmental News",
            "description": "Get recent environmental news from the past 30 days",
            "mimeType": "application/json"
        }
    ]


def parse_air_quality_resource(air_data: Optional[Dict[str, Any]], 
                                lat: float, 
                                lon: float) -> Dict[str, Any]:
    #parse air quality into resource format
    if not air_data or 'list' not in air_data:
        return {
            "uri": f"environment://air-quality/{lat}/{lon}",
            "error": "No air quality data available"
        }
    
    try:
        latest = air_data['list'][0]
        aqi_value = latest['main']['aqi']
        components = latest['components']
        
        return {
            "uri": f"environment://air-quality/{lat}/{lon}",
            "location": {
                "latitude": lat,
                "longitude": lon
            },
            "timestamp": latest['dt'],
            "air_quality_index": {
                "value": aqi_value,
                "category": AQI_CATEGORIES.get(aqi_value, "Unknown")
            },
            "pollutants": {
                "co": components.get('co'),
                "no2": components.get('no2'),
                "o3": components.get('o3'),
                "pm2_5": components.get('pm2_5'),
                "pm10": components.get('pm10')
            }
        }
    except (KeyError, IndexError) as e:
        return {
            "uri": f"environment://air-quality/{lat}/{lon}",
            "error": f"Error parsing air quality data: {e}"
        }


def parse_news_resource(news_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    # parse news into resource format
    if not news_data or 'articles' not in news_data:
        return {
            "uri": "environment://news/latest",
            "error": "No news data available"
        }
    
    try:
        articles = []
        for article in news_data['articles'][:5]:
            articles.append({
                "title": article.get('title'),
                "description": article.get('description'),
                "source": article.get('source', {}).get('name'),
                "published_at": article.get('publishedAt'),
                "url": article.get('url')
            })
        
        return {
            "uri": "environment://news/latest",
            "total_results": news_data.get('totalResults'),
            "articles": articles
        }
    except Exception as e:
        return {
            "uri": "environment://news/latest",
            "error": f"Error parsing news data: {e}"
        }


def parse_resources(air_data: Optional[Dict[str, Any]], 
                    news_data: Optional[Dict[str, Any]],
                    location: Dict[str, float]) -> Dict[str, Any]:

    return {
        "resources": get_mcp_resources(),
        "data": {
            "air_quality": parse_air_quality_resource(
                air_data, 
                location['lat'], 
                location['lon']
            ),
            "environmental_news": parse_news_resource(news_data)
        }
    }
