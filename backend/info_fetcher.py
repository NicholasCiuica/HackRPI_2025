import requests
import json
from datetime import datetime, timedelta


openweather_APIkey = "be8ff55134dc777d8aaa03d93bd78662"
news_APIkey = "1dbbb7ae82c84c87b25de7fe22658c70"

#default location if there is no location provided
loc = { 
    "lat": 42.728,
    "lon": -73.687
}

def getAirPollutionData(loc, key):
    AirPollutionURL = (f"https://api.openweathermap.org/data/2.5/air_pollution"
                    f"?lat={loc['lat']}&lon={loc['lon']}&appid={key}")
    try: 
        response = requests.get(AirPollutionURL)
        response.raise_for_status()  # Raise an error for bad responses
        airpollution_data = response.json()
        return airpollution_data
    except Exception as e:
        print("Couldn't fetch airpollution data:", e)
        return None
    
def getNewsData(loc):
    date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d') 
    query = "environmental protection OR climate change OR renewable energy"
    newsURL = (f"https://newsapi.org/v2/everything?q={query}$language=en&from={date}&sortBy=popularity&apiKey={news_APIkey}")
    try:
        response = requests.get(newsURL)
        response.raise_for_status()  # Raise an error for bad responses
        news_data = response.json()
        return news_data
    except Exception as e:
        print("Couldn't fetch news data:", e)
        return None
    
def main():
    air_data = getAirPollutionData(loc, openweather_APIkey)

    news_data = getNewsData(loc)
    if news_data and 'articles' in news_data:
        for article in news_data['articles'][:5]:  # Print top 5 articles
            print(f"Title: {article['title']}")
            print(f"Description: {article['description']}")
            print(f"URL: {article['url']}\n")
    else:
        print("No news data available.")

main();