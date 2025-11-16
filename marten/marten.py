from typing import Any
import httpx
import os
import sys
import re
import google.generativeai as genai
from mcp.server.fastmcp import FastMCP

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from fetcher import getAirPollutionData, getNewsData, loc
from preparer import get_mcp_resources, parse_resources, parse_air_quality_resource, parse_news_resource

# Initialize MCP server
mcp = FastMCP("marten")

# Get API keys from environment variables (with fallback for testing)
AQI_API_KEY = os.getenv("OPENWEATHER_API_KEY", "be8ff55134dc777d8aaa03d93bd78662")
NWS_API_KEY = os.getenv("NEWS_API_KEY", "1dbbb7ae82c84c87b25de7fe22658c70")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDgjIZ081SovuPrjQ5VdOfoJTgnbsGHDHE")

# Fetch initial data
air_data = getAirPollutionData(loc, AQI_API_KEY)
news_data = getNewsData(NWS_API_KEY)
parsed = parse_resources(air_data, news_data, loc)


# ============================================================================
# MCP Resources
# ============================================================================

@mcp.resource("environment://air-quality/{lat}/{lon}")
async def get_air_quality(lat: float, lon: float) -> str:
    """Get current air quality data for a specific location"""
    location = {"lat": lat, "lon": lon}
    air_data = getAirPollutionData(location, AQI_API_KEY)
    
    if not air_data:
        return "Unable to fetch air quality data"
    
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
    
    result = parse_news_resource(news_data)
    
    if "error" in result:
        return result["error"]
    
    article = result['article']
    
    output = f"Environmental News (randomly selected from {result['selected_from']} articles):\n\n"  
    output += f"   Source: {article['source']}\n"
    output += f"   {article['description']}\n"
    output += f"   URL: {article['url']}\n\n"
    
    return output


# ============================================================================
# MCP Tools
# ============================================================================

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


@mcp.tool()
async def rate_news_sentiment(title: str, description: str) -> int:
    """Rate the environmental sustainability sentiment of a news article from 0-10
    
    Rating Scale:
    0 = Neutral/Informational news with no clear positive or negative environmental impact
    1 = Worst possible news (catastrophic environmental disasters, massive emissions increases)
    2-4 = Bad news (worsening conditions, negative developments, setbacks)
    5 = Slightly negative or mixed with more negative than positive
    6 = Slightly positive or mixed with more positive than negative
    7-9 = Good news (positive developments, progress, declining emissions)
    10 = Best possible news (major breakthroughs, dramatic improvements)
    
    Args:
        title: The news article title
        description: Brief description of the article
    
    Returns:
        A rating from 0 to 10
    """
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""You are a sustainability news sentiment analyzer. Your task is to rate news articles about environmental sustainability on a scale from 0 to 10.

Rating Scale:
0 = Neutral/Informational news with no clear positive or negative environmental impact
1 = Worst possible news (catastrophic environmental disasters, massive emissions increases, major policy failures)
2-4 = Bad news (worsening conditions, negative developments, setbacks)
5 = Slightly negative or mixed with more negative than positive
6 = Slightly positive or mixed with more positive than negative
7-9 = Good news (positive developments, progress, declining emissions, successful initiatives)
10 = Best possible news (major breakthroughs, dramatic improvements, transformative solutions)

Focus on the actual environmental impact and trajectory for sustainability, not just the tone of writing.

Examples:
"Emissions could already be declining" → 8
"Arctic ice reaches record low" → 2
"New climate policy under debate" → 0
"Renewable energy surpasses fossil fuels globally" → 9
"Minor improvements in recycling rates" → 6

Input:
Title: {title}
Description: {description}

Output format: Return ONLY a single number from 0 to 10, nothing else."""

    try:
        response = model.generate_content(prompt)
        rating_text = response.text.strip()
        
        # Extract just the number
        match = re.search(r'\d+', rating_text)
        if match:
            rating = int(match.group())
            # Ensure rating is within bounds
            return max(0, min(10, rating))
        else:
            return 0  # Default to neutral if can't parse
    except Exception as e:
        print(f"Error rating sentiment: {e}")
        return 0


# # ============================================================================
# # Test Output (when run directly)
# # ============================================================================

# if __name__ == "__main__":
#     resources = parsed['resources']
#     print("Available resources:", resources)

#     # Get air quality data
#     if "error" not in parsed['data']['air_quality']:
#         air_quality = parsed['data']['air_quality']
#         print(f"\nAir Quality: {air_quality['air_quality_index']['category']}")
#         print(f"Location: {air_quality['location']}")
#         if 'pollutants' in air_quality:
#             print(f"PM2.5: {air_quality['pollutants']['pm2_5']} μg/m³")

#     # Get environmental news
#     if "error" not in parsed['data']['environmental_news']:
#         news = parsed['data']['environmental_news']
#         print(f"\nNews articles: {news['total_results']} total")
#         for article in news['articles'][:3]:
#             print(f"  - {article['title']}")
#             if article['description']:
#                 print(f"    {article['description'][:100]}...\n")


# ============================================================================
# Run MCP Server
# ============================================================================

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
