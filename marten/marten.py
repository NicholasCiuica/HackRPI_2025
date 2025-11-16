from typing import Any
import httpx
import os
import sys
from mcp.server.fastmcp import FastMCP

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from fetcher import getAirPollutionData, getNewsData, loc
from preparer import get_mcp_resources, parse_resources

mcp = FastMCP("marten")

air_data = getAirPollutionData(loc, AQI_API_KEY)
news_data = getNewsData(NWS_API_KEY)

# Parse resources
parsed = parse_resources(air_data, news_data, loc)

@mcp.resource("environment://air-quality/{lat}/{lon}")
async def get_air_quality(lat: float, lon: float) -> str:
    """Get current air quality data for a specific location"""
    location = {"lat": lat, "lon": lon}
    air_data = getAirPollutionData(location, AQI_API_KEY)
    
    if not air_data:
        return "Unable to fetch air quality data"
    
    from preparer import parse_air_quality_resource
    result = parse_air_quality_resource(air_data, lat, lon)
    
    if "error" in result:
        return result["error"]
    
    aqi = result['air_quality_index']
    pollutants = result['pollutants']
    
    return f"""Air Quality for ({lat}, {lon}):
Status: {aqi['category']} (AQI: {aqi['value']})
Pollutants:
  - CO: {pollutants['co']} μg/m³
  - NO2: {pollutants['no2']} μg/m³
  - O3: {pollutants['o3']} μg/m³
  - PM2.5: {pollutants['pm2_5']} μg/m³
  - PM10: {pollutants['pm10']} μg/m³"""

@mcp.resource("environment://news/latest")
async def get_environmental_news() -> str:
    """Get latest environmental news"""
    news_data = getNewsData(NWS_API_KEY)
    
    if not news_data:
        return "Unable to fetch news data"
    
    from preparer import parse_news_resource
    result = parse_news_resource(news_data)
    
    if "error" in result:
        return result["error"]
    
    output = f"Latest Environmental News ({result['total_results']} articles):\n\n"
    
    for i, article in enumerate(result['articles'], 1):
        output += f"{i}. {article['title']}\n"
        output += f"   Source: {article['source']}\n"
        output += f"   {article['description']}\n"
        output += f"   URL: {article['url']}\n\n"
    
    return output

@mcp.tool()
async def check_air_quality(latitude: float, longitude: float) -> str:
    """Check air quality for any location by coordinates
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
    """
    return await get_air_quality(latitude, longitude)

@mcp.tool()
async def get_news() -> str:
    """Get the latest environmental news articles"""
    return await get_environmental_news()

if __name__ == "__main__":
    # Test output
    resources = parsed['resources']
    print("Available resources:", resources)

    # Get air quality data
    if "error" not in parsed['data']['air_quality']:
        air_quality = parsed['data']['air_quality']
        print(f"\nAir Quality: {air_quality['air_quality_index']['category']}")
        print(f"Location: {air_quality['location']}")
        if 'pollutants' in air_quality:
            print(f"PM2.5: {air_quality['pollutants']['pm2_5']} μg/m³")

    # Get environmental news
    if "error" not in parsed['data']['environmental_news']:
        news = parsed['data']['environmental_news']
        print(f"\nNews articles: {news['total_results']} total")
        for article in news['articles'][:3]:
            print(f"  - {article['title']}")
            if article['description']:
                print(f"    {article['description'][:100]}...\n")
    
