"""
Integration module between Marten and the desktop pet
MCP CLIENT that connects to the Marten MCP server
"""
import threading
import queue
import os
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import google.generativeai as genai

GEMINI_API_KEY = "AIzaSyDgjIZ081SovuPrjQ5VdOfoJTgnbsGHDHE"
genai.configure(api_key=GEMINI_API_KEY)


class MartenIntegration:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.message_queue = queue.Queue()
        self.thread = None
        self.running = False
        self.loop = None
        
    def start(self):
        """Start the MCP client integration in a background thread"""
        self.running = True
        self.thread = threading.Thread(target=self._run_thread, daemon=True)
        self.thread.start()
        print("Marten MCP client integration started!")
    
    def _run_thread(self):
        """Run the asyncio event loop in a separate thread"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._run_loop())
    
    async def _run_loop(self):
        """Main async loop that connects to MCP server and fetches tips"""
        # Wait a bit before starting
        await asyncio.sleep(5)
        
        while self.running:
            try:
                await self._fetch_and_generate_tip()
                await asyncio.sleep(60)  # Fetch new tip every 60 seconds
            except Exception as e:
                print(f"Error in Marten MCP integration: {e}")
                import traceback
                traceback.print_exc()
                await asyncio.sleep(60)
    
    async def _fetch_and_generate_tip(self):
        """Connect to MCP server and fetch data to generate sustainability tips"""
        # Path to the marten server
        server_script = os.path.join(os.path.dirname(__file__), 'marten', 'marten.py')
        
        # Server parameters for stdio connection
        server_params = StdioServerParameters(
            command="python",
            args=[server_script],
            env=None
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()
                
                # Location for Troy, NY
                location = {"lat": 42.728, "lon": -73.687}
                
                # Call the MCP server tools
                try:
                    # Get news using the MCP tool
                    news_result = await session.call_tool("get_news", arguments={})
                    news_content = news_result.content[0].text if news_result.content else ""
                    
                    print(f"DEBUG: News content received:\n{news_content[:500]}")  # Debug output
                    
                    # Parse the first article from news
                    # Format is: "1. Title\n   Source: ...\n   Description\n   URL: ..."
                    article_title = ""
                    article_desc = ""
                    if news_content:
                        lines = news_content.split('\n')
                        for i, line in enumerate(lines):
                            # Look for numbered article (e.g., "1. Title")
                            if line.strip() and line[0].isdigit() and '. ' in line:
                                article_title = line.split('. ', 1)[1].strip()
                                # Description is usually 2 lines down (after Source line)
                                if i + 2 < len(lines):
                                    desc_line = lines[i + 2].strip()
                                    if desc_line and not desc_line.startswith('URL:'):
                                        article_desc = desc_line
                                break
                    
                    if not article_title:
                        print("No news article found")
                        return
                    
                    # Rate the sentiment using the MCP tool
                    rating_result = await session.call_tool(
                        "rate_news_sentiment",
                        arguments={
                            "title": article_title,
                            "description": article_desc
                        }
                    )
                    rating_text = rating_result.content[0].text if rating_result.content else "5"
                    
                    # Extract the rating number
                    import re
                    match = re.search(r'\d+', rating_text)
                    rating = int(match.group()) if match else 5
                    rating = max(0, min(10, rating))
                    
                    print(f"DEBUG: Sentiment rating: {rating}/10 (raw response: {rating_text})")
                    
                    # Get air quality using the MCP tool
                    air_result = await session.call_tool(
                        "check_air_quality",
                        arguments={
                            "lat": location['lat'],
                            "lon": location['lon']
                        }
                    )
                    air_content = air_result.content[0].text if air_result.content else "No air quality data"
                    
                    print(f"DEBUG: Air quality content received:\n{air_content[:300]}")
                    
                    # Extract AQI from air quality response
                    air_quality_str = "No air quality data"
                    aqi_match = re.search(r'AQI:\s*(\d+)', air_content)
                    category_match = re.search(r'Status:\s*([^\n]+)', air_content)
                    if aqi_match and category_match:
                        air_quality_str = f"AQI: {aqi_match.group(1)} ({category_match.group(1).strip()})"
                    
                    print(f"DEBUG: Parsed air quality: {air_quality_str}")
                    
                    # Generate sustainability tip using Gemini
                    prompt = f"""Based on this environmental news and air quality data, generate a short, actionable sustainability tip (max 60 characters).

Air Quality: {air_quality_str}

Recent News: {article_title}
{article_desc if article_desc else ''}

Sentiment Rating: {rating}/10 (0=neutral, 10=best)

Generate a friendly, concise tip that relates to this news. Keep it under 60 characters. Focus on what individuals can do."""

                    response = self.model.generate_content(prompt)
                    tip = response.text.strip().strip('"\'')
                    
                    # Truncate if too long
                    if len(tip) > 80:
                        tip = tip[:77] + "..."
                    
                    # Create article blurb (short summary, max 100 chars)
                    article_blurb = article_desc[:100] + "..." if len(article_desc) > 100 else article_desc
                    if not article_blurb:
                        article_blurb = article_title[:80] + "..." if len(article_title) > 80 else article_title
                    
                    # Format the message with tip and article info
                    formatted_message = f"Here's a tip:\n{tip}\n\n{article_blurb}"
                    
                    # Add to message queue for the pet to display
                    self.message_queue.put({
                        'type': 'tip',
                        'text': formatted_message,
                        'rating': rating,
                        'article': article_title[:50] + "..." if len(article_title) > 50 else article_title
                    })
                    
                    print(f"✓ MCP Client: Generated tip from server: {tip} (rating: {rating})")
                    
                except Exception as e:
                    print(f"Error calling MCP server tools: {e}")
                    import traceback
                    traceback.print_exc()
    
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
