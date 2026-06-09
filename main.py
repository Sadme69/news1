import os
import sys
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
import uvicorn

from scraper import get_somoy_news_stream

app = FastAPI(title="Stream UI Portal Engine")

# Use a global client for efficiency
client = httpx.AsyncClient()

from urllib.parse import urljoin, quote

@app.get("/proxy")
async def proxy_stream(url: str, request: Request):
    """Proxies the .m3u8 or .ts files to bypass CORS and rewrites playlists."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Referer": "https://www.jagobd.com/"
        }
        
        response = await client.get(url, headers=headers, follow_redirects=True)
        content_type = response.headers.get("Content-Type", "")
        
        # If it's a playlist, we need to rewrite relative URLs
        if ".m3u8" in url or "mpegurl" in content_type.lower():
            text_content = response.text
            base_url = url.rsplit('/', 1)[0] + '/'
            new_lines = []
            
            for line in text_content.splitlines():
                if line and not line.startswith("#"):
                    # This is a URL (playlist or segment)
                    full_url = urljoin(url, line)
                    # Wrap it in our proxy
                    proxied_url = f"{request.base_url}proxy?url={quote(full_url, safe='')}"
                    new_lines.append(proxied_url)
                else:
                    new_lines.append(line)
            
            modified_content = "\n".join(new_lines)
            return StreamingResponse(
                content=iter([modified_content.encode()]),
                media_type="application/vnd.apple.mpegurl",
                headers={"Access-Control-Allow-Origin": "*"}
            )
            
        # For .ts files or other binary data, return as is
        return StreamingResponse(
            content=iter([response.content]),
            media_type=content_type,
            headers={"Access-Control-Allow-Origin": "*"}
        )
    except Exception as e:
        print(f"Proxy Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# CORS Configuration - Keeps communication bridging cleanly
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def home():
    """Fallback entry point displaying current active endpoints."""
    return {
        "status": "online", 
        "message": "Stream View Portal Operational.",
        "endpoints": {
            "Somoy News Live": "/somoy",
            "Somoy News M3U8 URL": "/somoy-url",
            "Sky Sports F1 (Legacy)": "/watch"
        import time

        # Use a global client for efficiency
        client = httpx.AsyncClient()

        # Simple In-Memory Cache
        cache = {
            "url": None,
            "expiry": 0
        }

        async def get_cached_somoy_url():
            """Returns the cached URL if valid, otherwise scrapes a new one."""
            current_time = time.time()
            if cache["url"] and current_time < cache["expiry"]:
                print("Using cached Somoy URL")
                return cache["url"]

            print("Cache expired or empty. Scraping new Somoy URL...")
            url = await get_somoy_news_stream()
            if url:
                cache["url"] = url
                cache["expiry"] = current_time + (15 * 60)  # Cache for 15 minutes
            return url

        @app.get("/somoy-url")
        async def somoy_url():
            """Returns the raw .m3u8 URL for Somoy News."""
            try:
                url = await get_cached_somoy_url()
                if not url:
                    raise HTTPException(status_code=500, detail="Failed to extract Somoy News stream.")
                return {"url": url}
            except Exception as e:
                print(f"Scraper Error: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @app.get("/somoy", response_class=HTMLResponse)
        async def watch_somoy(request: Request):
            """Serves a player for Somoy News using a local proxy to bypass CORS."""
            try:
                url = await get_cached_somoy_url()
                if not url:
                    return HTMLResponse(content=f"<h1>Scraper Error</h1><p>Failed to extract stream URL.</p>", status_code=500)

                # We point the player to our proxy endpoint
                proxy_url = f"{request.base_url}proxy?url={url}"

        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Somoy News Live</title>
            <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
            <style>
                html, body {{ margin: 0; padding: 0; width: 100%; height: 100%; background: #000; overflow: hidden; }}
                video {{ width: 100%; height: 100%; object-fit: contain; }}
            </style>
        </head>
        <body>
            <video id="video" controls autoplay></video>
            <script>
                const video = document.getElementById('video');
                const streamUrl = "{proxy_url}";
                if (Hls.isSupported()) {{
                    const hls = new Hls();
                    hls.loadSource(streamUrl);
                    hls.attachMedia(video);
                }} else if (video.canPlayType('application/vnd.apple.mpegurl')) {{
                    video.src = streamUrl;
                }}
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    except Exception as e:
        return HTMLResponse(content=f"<h1>Server Error</h1><pre>{str(e)}</pre>", status_code=500)

@app.get("/watch", response_class=HTMLResponse)
async def watch_stream():
    """Serves the front-end player template containing our fine-tuned fullscreen iframe."""
    file_path = os.path.join("templates", "player.html")
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404, 
            detail="Missing player.html component inside the templates folder."
        )
        
    with open(file_path, "r", encoding="utf-8") as file:
        return HTMLResponse(content=file.read())

if __name__ == "__main__":
    # Pull dynamic hosting ports assigned natively by Render environment matrices
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)