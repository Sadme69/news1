import asyncio
import os
import webbrowser
from scraper import get_somoy_news_stream

async def run_private_test():
    print("--- Starting Private Scraper Test ---")
    url = await get_somoy_news_stream()
    
    if url:
        print(f"\n[+] Success! Stream URL found.")
        
        # Path to the local player
        player_path = os.path.abspath("test_player.html")
        test_url = f"file://{player_path}?url={url}"
        
        print(f"[+] Opening local player: {test_url}")
        webbrowser.open(test_url)
    else:
        print("\n[-] Failed to extract stream URL. Check your connection or site changes.")

if __name__ == "__main__":
    asyncio.run(run_private_test())
