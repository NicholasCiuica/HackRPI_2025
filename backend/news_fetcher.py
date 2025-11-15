import requests
from datetime import datetime

date = datetime.today().strftime('%Y-%m-%d')
newsURL = ('https://newsapi.org/v2/everything?q=environment&from=' + date + '&sortBy=popularity&apiKey=1dbbb7ae82c84c87b25de7fe22658c70')
response = requests.get(newsURL)

# parse response 
news_data = response.json()
articles = news_data.get('articles', [])
