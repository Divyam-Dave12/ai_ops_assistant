import os
import requests
import re
import sys
from ddgs import DDGS
# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv

# Import our new Cache System
from utils.cache import get_cached_result, set_cached_result

load_dotenv()

OMDB_API_KEY = os.getenv("OMDB_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

try:
    from llm.groq_client import llm_client
except ImportError:
    llm_client = None

def clean_movie_title(raw_title):
    """
    Cleans up the movie title to ensure OMDb accepts it.
    """
    if not raw_title: return ""
    
    # 1. Remove the internal prefix
    title = raw_title.replace("Found via search:", "")
    
    # 2. Remove quotes and years like (2014)
    title = re.sub(r"['\"]", "", title)
    title = re.sub(r'\(\d{4}\)', '', title)
    
    # 3. Remove common suffixes that confuse OMDb
    separators = [" - ", " | ", " : ", " Official"]
    for sep in separators:
        if sep in title:
            title = title.split(sep)[0]
            
    return title.strip()
def get_movie_title_from_search(query):
    """
    Finds a movie title using Cache -> Search -> LLM.
    """
    # 1. CHECK CACHE FIRST 💾
    cached_title = get_cached_result(query)
    if cached_title:
        print(f"DEBUG: ⚡ Cache Hit! Using '{cached_title}' for '{query}'")
        return f"Found via search: {cached_title}"

    # 2. If not in cache, Try Real Search
    try:
        print(f"DEBUG: 🔍 Searching DDG for: '{query}'")
        
        with DDGS() as ddgs:
            results = list(ddgs.text(f"movie title {query}", max_results=3))
            
        if not results:
            return "Search failed."

        # 3. Use LLM to refine the result
        final_title = results[0]['title'] # Default fallback
        
        if llm_client:
            snippets = "\n".join([f"- {r['title']}: {r['body']}" for r in results])
            prompt = f"""
            Search Query: "{query}"
            Search Results:
            {snippets}
            
            Identify the specific movie title described. Return ONLY the title.
            """
            extracted = llm_client.generate_text(prompt).strip()
            # Clean up LLM output
            final_title = clean_movie_title(extracted)
        
        # 4. SAVE TO CACHE 💾
        set_cached_result(query, final_title)
        
        return f"Found via search: {final_title}"

    except Exception as e:
        print(f"DEBUG: Search Engine Failed: {e}")
        return "Search failed."

def search_movie_details(movie_title):
    clean_title = clean_movie_title(movie_title)
    print(f"DEBUG: OMDb Request -> t='{clean_title}'") # Verbose log
    
    url = "http://www.omdbapi.com/"
    params = {"apikey": OMDB_API_KEY, "t": clean_title}
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if data.get("Response") == "True":
            return {
                "title": data.get("Title"),
                "year": data.get("Year"),
                "rating": data.get("imdbRating"),
                "plot": data.get("Plot"),
                "director": data.get("Director")
            }
        else:
            # Fallback: Fuzzy search 's' instead of exact 't'
            print(f"DEBUG: OMDb exact match failed for '{clean_title}', trying fuzzy search...")
            params.pop("t")
            params["s"] = clean_title
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get("Response") == "True" and data.get("Search"):
                return {
                    "title": data["Search"][0]["Title"],
                    "year": data["Search"][0]["Year"],
                    "note": "Exact match failed, found closest result."
                }
            return f"Error: Movie '{clean_title}' not found in OMDb."
    except Exception as e:
        return f"API Error: {e}"

def get_youtube_trailer(movie_title):
    if not YOUTUBE_API_KEY: return "Error: YouTube API Key missing."
    clean_title = clean_movie_title(movie_title)
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {"key": YOUTUBE_API_KEY, "q": f"{clean_title} official trailer", "part": "snippet", "type": "video", "maxResults": 1}
    try:
        data = requests.get(url, params=params).json()
        if "items" in data and len(data["items"]) > 0:
            return f"https://www.youtube.com/watch?v={data['items'][0]['id']['videoId']}"
        return "Trailer not found."
    except Exception as e: return f"Error: {e}"

def get_streaming_info(movie_title):
    clean_title = clean_movie_title(movie_title)
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(f"where to watch {clean_title} streaming", max_results=3))
        if not results: return "Streaming info not found."
        return "\n".join([f"{r['title']}: {r['href']}" for r in results])
    except: return "Streaming info unavailable."