import asyncio
from playwright.async_api import async_playwright
import re

async def get_somoy_news_stream():
    async with async_playwright() as p:
        # Launching headless browser with Docker-optimized flags
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        print("Navigating to Jagobd Somoy News...")
        stream_url = None

        # Function to intercept network requests
        async def handle_request(request):
            nonlocal stream_url
            if ".m3u8" in request.url:
                stream_url = request.url
                print(f"Intercepted Stream URL: {stream_url}")

        page.on("request", handle_request)

        try:
            await page.goto("https://www.jagobd.com/somoynews", wait_until="domcontentloaded", timeout=60000)

            # Find the iframe that likely contains the player
            iframes = await page.query_selector_all("iframe")
            iframe_url = None
            for ifr in iframes:
                src = await ifr.get_attribute("src")
                if src and "jagobd.com" in src and ("player" in src or "embed" in src):
                    iframe_url = src
                    break

            if iframe_url:
                print(f"Found iframe URL: {iframe_url}")
                
                # We wait for the stream_url to be intercepted while navigating or waiting
                for _ in range(30): # Up to 30 seconds
                    if stream_url:
                        print(f"Success via Interception: {stream_url}")
                        await browser.close()
                        return stream_url
                    await asyncio.sleep(1)

                # Find the frame object as fallback
                frame = None
                for f in page.frames:
                    if iframe_url in f.url:
                        frame = f
                        break
                
                if not frame:
                    # Try to find by index or selector if URL match failed
                    print("Could not find frame by URL, waiting for any frame...")
                    await asyncio.sleep(5) # Wait for frames to load
                    for f in page.frames:
                        if "jagobd.com" in f.url and "embed" in f.url:
                            frame = f
                            break

                if frame:
                    print(f"Accessing frame: {frame.url}")
                    try:
                        # Wait for the selector inside the frame
                        await frame.wait_for_selector("#iikaShgecrnstBtufa", timeout=20000)
                        
                        # Execute the function inside the frame context
                        stream_url = await frame.evaluate("ltgettpHUr()")
                        if stream_url:
                            print(f"Generated Stream URL: {stream_url}")
                            await browser.close()
                            return stream_url
                    except Exception as inner_e:
                        print(f"Frame access error: {inner_e}")
                        # Check frame content
                        f_content = await frame.content()
                        print(f"Frame content length: {len(f_content)}")
                else:
                    print("No suitable frame found.")

            # Fallback if function execution fails
            content = await page.content()
            m3u8_match = re.search(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', content)
            if m3u8_match:
                stream_url = m3u8_match.group(1)
                await browser.close()
                return stream_url

            print("Stream URL (.m3u8) not found.")
            await browser.close()
            return None
                
        except Exception as e:
            print(f"An error occurred: {e}")
            await browser.close()
            return None

if __name__ == "__main__":
    url = asyncio.run(get_somoy_news_stream())
    if url:
        print(f"\nSUCCESS: {url}")
    else:
        print("\nFAILED to extract stream URL.")
