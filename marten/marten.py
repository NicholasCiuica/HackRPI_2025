from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from fetcher import getAirPollutionData, getNewsData, loc
from preparer import get_mcp_resources, parse_resources

mcp = FastMCP("marten")

# Constants
AQI_API_KEY = "be8ff55134dc777d8aaa03d93bd78662"
NWS_API_KEY = "1dbbb7ae82c84c87b25de7fe22658c70"

air_data = getAirPollutionData(loc, AQI_API_KEY)
news_data = getNewsData(NWS_API_KEY)

parsed = parse_resources(air_data, news_data, loc)

resources = parsed['resources']
print("Available resources:", resources)

# Get air quality data
air_quality = parsed['data']['air_quality']
print(f"\nAir Quality: {air_quality['air_quality_index']['category']}")
print(f"Location: {air_quality['location']}")

# Get environmental news
news = parsed['data']['environmental_news']
print(f"\nNews articles: {news['total_results']} total")
for article in news['articles'][:3]:
    print(f"  - {article['title']}")
    print(f"    {article['description']}\n")
    
