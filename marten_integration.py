"""
Integration module between Marten MCP client and the desktop pet
"""
import asyncio
import threading
import queue
import sys
import os

# Add marten directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'marten'))

import google.generativeai as genai
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

GEMINI_API_KEY = "AIzaSyDgjIZ081SovuPrjQ5VdOfoJTgnbsGHDHE"
genai.configure(api_key=GEMINI_API_KEY)


class MartenIntegration:
    def __init__(self):
        self.session = None
        self.model = genai.GenerativeModel('gemini-pro')
        self.message_queue = queue.Queue()
        self.loop = None
        self.thread = None
        self.running = False
        
    def start(self):
        """Start the MCP client in a background thread"""
        self.running = True
        self.thread = threading.Thread(target=self._run_async_loop, daemon=True)
        self.thread.start()
    
    def _run_async_loop(self):
        """Run the async event loop in a separate thread"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._main())
    
    async def _main(self):
        """Main async function that runs in the background"""
        try:
            # Connect to MCP server
            await self._connect_to_server()
            
            # Periodically fetch news and generate tips
            while self.running:
                await self._fetch_and_generate_tip()
                await asyncio.sleep(60)  # Fetch new tip every 60 seconds
                
        except Exception as e:
            print(f"Error in Marten integration: {e}")
    
    async def _connect_to_server(self):
        """Connect to the MCP server"""
        try:
            server_params = StdioServerParameters(
                command="python",
                args=[os.path.join(os.path.dirname(__file__), "marten", "marten.py")],
                env=None
            )
            
            stdio_transport = await stdio_client(server_params)
            self.session = ClientSession(stdio_transport[0], stdio_transport[1])
            await self.session.initialize()
            print("Connected to Marten MCP server")
        except Exception as e:
            print(f"Could not connect to MCP server: {e}")
    
    async def _call_tool(self, tool_name: str, arguments: dict) -> str:
        """Call a tool on the MCP server"""
        if not self.session:
            return None
        
        try:
            result = await self.session.call_tool(tool_name, arguments)
            if result.content:
                return result.content[0].text
            return None
        except Exception as e:
            print(f"Error calling tool {tool_name}: {e}")
            return None
    
    async def _fetch_and_generate_tip(self):
        """Fetch news and generate a sustainability tip"""
        try:
            # Get air quality data
            air_quality = await self._call_tool("check_air_quality", {
                "latitude": 42.728,
                "longitude": -73.687
            })
            
            # Get news
            news = await self._call_tool("get_news", {})
            
            if not news:
                return
            
            # Extract first article for tip generation
            # Parse news text to get first article
            lines = news.split('\n')
            article_title = ""
            article_desc = ""
            
            for i, line in enumerate(lines):
                if line.strip().startswith('1.'):
                    article_title = line.strip()[3:].strip()
                    # Look for description in next few lines
                    for j in range(i+1, min(i+5, len(lines))):
                        if lines[j].strip() and not lines[j].strip().startswith('Source:') and not lines[j].strip().startswith('URL:'):
                            article_desc = lines[j].strip()
                            break
                    break
            
            # Rate the article sentiment
            rating = None
            if article_title and article_desc:
                rating_result = await self._call_tool("rate_news_sentiment", {
                    "title": article_title,
                    "description": article_desc
                })
                if rating_result:
                    try:
                        rating = int(rating_result.strip())
                    except:
                        rating = None
            
            # Generate a sustainability tip using Gemini
            prompt = f"""Based on this environmental news and air quality data, generate a short, actionable sustainability tip (max 60 characters).

Air Quality: {air_quality[:200] if air_quality else 'No data'}

Recent News: {article_title}
{article_desc}

Sentiment Rating: {rating}/10 (0=neutral, 10=best)

Generate a friendly, concise tip that relates to this news. Keep it under 60 characters. Focus on what individuals can do."""

            response = self.model.generate_content(prompt)
            tip = response.text.strip()
            
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
            
        except Exception as e:
            print(f"Error generating tip: {e}")
    
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
