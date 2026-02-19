import logging
import os
from dotenv import load_dotenv
import requests

load_dotenv()

logger = logging.getLogger("nova.websearch")

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")


def search_web(query: str, max_results: int = 5) -> dict:
    """
    Search the web for information.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return (default: 5)
    
    Returns:
        {"status": "success", "results": [...], "answer": "..."} on success
        {"status": "error", "message": "..."} on failure
    """
    logger.info(f"🔍 Searching web for: {query}")
    
    try:
        # Try Tavily API first (recommended for AI/LLM apps)
        if TAVILY_API_KEY:
            return _search_tavily(query, max_results)
        
        # Fallback to Serper
        elif SERPER_API_KEY:
            return _search_serper(query, max_results)
        
        else:
            return {
                "status": "error",
                "message": "No web search API configured. Please set TAVILY_API_KEY in .env (get free key at tavily.com) or use SERPER_API_KEY"
            }
    
    except Exception as e:
        logger.error(f"Web search error: {str(e)}")
        return {"status": "error", "message": str(e)}


def _search_tavily(query: str, max_results: int) -> dict:
    """Search using Tavily API (free tier available at tavily.com)."""
    url = "https://api.tavily.com/search"
    
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "max_results": max_results,
        "include_answer": True,
    }
    
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
    
    data = response.json()
    
    results = []
    for result in data.get("results", []):
        results.append({
            "title": result.get("title", ""),
            "url": result.get("url", ""),
            "snippet": result.get("content", ""),
        })
    
    return {
        "status": "success",
        "query": query,
        "answer": data.get("answer", ""),
        "results": results,
        "total_results": len(results)
    }


def _search_serper(query: str, max_results: int) -> dict:
    """Search using Serper API (fallback)."""
    url = "https://google.serper.dev/search"
    
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    
    params = {
        "q": query,
        "num": max_results,
    }
    
    response = requests.get(url, headers=headers, params=params, timeout=10)
    response.raise_for_status()
    
    data = response.json()
    
    results = []
    for item in data.get("organic", [])[:max_results]:
        results.append({
            "title": item.get("title", ""),
            "url": item.get("link", ""),
            "snippet": item.get("snippet", ""),
        })
    
    return {
        "status": "success",
        "query": query,
        "results": results,
        "total_results": len(results)
    }