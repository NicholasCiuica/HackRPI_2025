"""
Test script to verify Marten integration is working
"""
import asyncio
import sys
import os

sys.path.append(os.path.dirname(__file__))

from marten_integration import MartenIntegration

async def test_integration():
    print("=== Testing Marten Integration ===\n")
    
    marten = MartenIntegration()
    
    # Connect to server
    print("1. Connecting to MCP server...")
    await marten._connect_to_server()
    
    if marten.session:
        print("✓ Connected successfully!\n")
    else:
        print("✗ Failed to connect\n")
        return
    
    # Test air quality
    print("2. Testing air quality tool...")
    air = await marten._call_tool("check_air_quality", {
        "latitude": 42.728,
        "longitude": -73.687
    })
    if air:
        print(f"✓ Air quality data received:")
        print(f"  {air[:150]}...\n")
    else:
        print("✗ Failed to get air quality\n")
    
    # Test news
    print("3. Testing news tool...")
    news = await marten._call_tool("get_news", {})
    if news:
        print(f"✓ News data received:")
        lines = news.split('\n')
        for line in lines[:5]:
            print(f"  {line}")
        print("  ...\n")
    else:
        print("✗ Failed to get news\n")
    
    # Test sentiment rating
    print("4. Testing sentiment rating tool...")
    rating = await marten._call_tool("rate_news_sentiment", {
        "title": "Renewable energy capacity reaches new record globally",
        "description": "Solar and wind installations exceeded all projections, marking significant progress in clean energy transition."
    })
    if rating:
        print(f"✓ Sentiment rating: {rating}/10\n")
    else:
        print("✗ Failed to rate sentiment\n")
    
    # Generate a tip
    print("5. Generating sustainability tip...")
    await marten._fetch_and_generate_tip()
    
    message = marten.get_next_message()
    if message:
        print("✓ Tip generated:")
        print(f"  Type: {message['type']}")
        print(f"  Text: {message['text']}")
        print(f"  Rating: {message.get('rating', 'N/A')}/10")
        print(f"  Article: {message.get('article', 'N/A')}\n")
    else:
        print("✗ No tip generated\n")
    
    print("=== All tests complete! ===")
    print("\nYou can now run main.py to see the desktop pet with these tips!")

if __name__ == "__main__":
    asyncio.run(test_integration())
