"""
Integration module between Marten and the desktop pet
Simplified version that calls functions directly instead of using MCP client/server
"""
import threading
import queue
import sys
import os
import time

# Add backend and marten directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'marten'))

import google.generativeai as genai
from fetcher import getAirPollutionData, getNewsData
from preparer import parse_air_quality_resource, parse_news_resource

GEMINI_API_KEY = "AIzaSyDgjIZ081SovuPrjQ5VdOfoJTgnbsGHDHE"
AQI_API_KEY = "be8ff55134dc777d8aaa03d93bd78662"
NWS_API_KEY = "1dbbb7ae82c84c87b25de7fe22658c70"

genai.configure(api_key=GEMINI_API_KEY)


class MartenIntegration:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')
        self.message_queue = queue.Queue()
        self.thread = None
        self.running = False
        
    def start(self):
        """Start the integration in a background thread"""
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        print("Marten integration started!")
    
    def _run_loop(self):
        """Run the main loop in a separate thread"""
        # Wait a bit before starting to fetch data
        time.sleep(5)
        
        while self.running:
            try:
                self._fetch_and_generate_tip()
                time.sleep(60)  # Fetch new tip every 60 seconds
            except Exception as e:
                print(f"Error in Marten integration: {e}")
                time.sleep(60)  # Wait before retrying
    
    def _fetch_and_generate_tip(self):
        """Fetch news and generate a sustainability tip"""
        try:
            # Get air quality data
            location = {"lat": 42.728, "lon": -73.687}
            air_data = getAirPollutionData(location, AQI_API_KEY)
            
            # Get news
            news_data = getNewsData(NWS_API_KEY)
            
            if not news_data or 'articles' not in news_data:
                print("No news data available")
                return
            
            # Get first article
            articles = news_data.get('articles', [])
            if not articles:
                return
            
            article = articles[0]
            article_title = article.get('title', '')
            article_desc = article.get('description', '')
            
            if not article_title:
                return
            
            # Rate the article sentiment using Gemini
            rating = self._rate_sentiment(article_title, article_desc)
            
            # Parse air quality
            air_quality_str = "No air quality data"
            if air_data:
                air_parsed = parse_air_quality_resource(air_data, location['lat'], location['lon'])
                if 'air_quality_index' in air_parsed:
                    aqi = air_parsed['air_quality_index']
                    air_quality_str = f"AQI: {aqi['value']} ({aqi['category']})"
            
            # Generate a sustainability tip using Gemini
            prompt = f"""Based on this environmental news and air quality data, generate a short, actionable sustainability tip (max 60 characters).

Air Quality: {air_quality_str}

Recent News: {article_title}
{article_desc if article_desc else ''}

Sentiment Rating: {rating}/10 (0=neutral, 10=best)

Generate a friendly, concise tip that relates to this news. Keep it under 60 characters. Focus on what individuals can do."""

            response = self.model.generate_content(prompt)
            tip = response.text.strip()
            
            # Remove quotes if present
            tip = tip.strip('"\'')
            
            # If tip is too long, truncate
            if len(tip) > 80:
                tip = tip[:77] + "..."
            
            # Add to message queue for the pet to display
            self.message_queue.put({
                'type': 'tip',
                'text': tip,
                'rating': rating,
                'article': article_title[:50] + "..." if len(article_title) > 50 else article_title
            })
            
            print(f"Generated tip: {tip} (rating: {rating})")
            
        except Exception as e:
            print(f"Error generating tip: {e}")
            import traceback
            traceback.print_exc()
    
    def _rate_sentiment(self, title: str, description: str) -> int:
        """Rate the sentiment of a news article from 0-10"""
        try:
            prompt = f"""You are a sustainability news sentiment analyzer. Rate this news article on a scale from 0 to 10.

Rating Scale:
0 = Neutral/Informational news
1 = Worst possible news (catastrophic environmental disasters)
2-4 = Bad news (worsening conditions, setbacks)
5 = Slightly negative or mixed
6 = Slightly positive or mixed
7-9 = Good news (positive developments, progress)
10 = Best possible news (major breakthroughs)

Title: {title}
Description: {description if description else 'No description'}

Return ONLY a single number from 0 to 10."""

            response = self.model.generate_content(prompt)
            rating_text = response.text.strip()
            
            # Extract just the number
            import re
            match = re.search(r'\d+', rating_text)
            if match:
                rating = int(match.group())
                return max(0, min(10, rating))
            else:
                return 5  # Default to neutral
        except Exception as e:
            print(f"Error rating sentiment: {e}")
            return 5  # Default to neutral
    
    def get_next_message(self):
        """Get the next message from the queue (non-blocking)"""
        try:
            return self.message_queue.get_nowait()
        except queue.Empty:
            return None
    
    def stop(self):
        """Stop the integration"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)


# Global instance
_marten_integration = None

def get_marten_integration():
    """Get or create the global Marten integration instance"""
    global _marten_integration
    if _marten_integration is None:
        _marten_integration = MartenIntegration()
    return _marten_integration
