import requests
import json
from datetime import datetime, timedelta

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
    
def getNewsData(key):
    date_from = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d')    
    query = "environmental protection OR climate change OR renewable energy"
    newsURL = (f"https://newsapi.org/v2/everything?q={query} -business&language=en&from={date_from}&sortBy=relevancy&excludeDomains=hbr.org,finance.yahoo.com&apiKey={key}")
    try:
        response = requests.get(newsURL)
        response.raise_for_status()  # Raise an error for bad responses
        news_data = response.json()
        return news_data
    except Exception as e:
        print("Couldn't fetch news data:", e)
        return None
    
def main(AQI_API_KEY, NEWS_API_KEY):
    air_data = getAirPollutionData(loc, AQI_API_KEY)
    if air_data:
        with open('airPollutionData.json', 'w') as AQI_FILE:
            json.dump(air_data, AQI_FILE, indent=2)
    
    news_data = getNewsData(NEWS_API_KEY)
    if news_data:
        with open('newsData.json', 'w') as NEWS_FILE:
            json.dump(news_data, NEWS_FILE, indent=2)
