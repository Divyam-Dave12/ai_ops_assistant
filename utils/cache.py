import json
import os
import hashlib

CACHE_FILE = "search_cache.json"

def load_cache():
    """Loads the cache from disk."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_cache(cache_data):
    """Saves the cache to disk."""
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(cache_data, f, indent=4)
    except Exception as e:
        print(f"⚠️ Warning: Failed to save cache: {e}")

def get_cached_result(query):
    """
    Returns the cached result for a query if it exists.
    Normalizes the query (lowercase, stripped) to hit cache more often.
    """
    cache = load_cache()
    key = query.lower().strip()
    return cache.get(key)

def set_cached_result(query, result):
    """Saves a new result to the cache."""
    cache = load_cache()
    key = query.lower().strip()
    cache[key] = result
    save_cache(cache)
    print(f"💾 Cached saved: '{key}' -> '{result}'")