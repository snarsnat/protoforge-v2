"""
ProtoForge Community Tools
Web search, fetch, scraping
"""

import os
import json
from typing import Optional
from langchain_core.tools import BaseTool
from pydantic import Field


class WebSearchTool(BaseTool):
    """Web search tool"""
    
    name: str = "web_search"
    description: str = """Search the web for information.
Returns top results with titles, URLs, and snippets."""
    
    def _run(self, query: str, num_results: int = 5) -> str:
        """Search web"""
        # Try Tavily first
        api_key = os.getenv("TAVILY_API_KEY")
        if api_key:
            try:
                from tavily import TavilyClient
                client = TavilyClient(api_key=api_key)
                results = client.search(query=query, max_results=num_results)
                
                formatted = []
                for r in results.get("results", []):
                    formatted.append({
                        "title": r.get("title", ""),
                        "url": r.get("url", ""),
                        "content": r.get("content", "")[:200]
                    })
                return json.dumps(formatted, indent=2)
            except Exception as e:
                pass
        
        # Fallback: simple search placeholder
        return json.dumps([{
            "title": f"Result for: {query}",
            "url": "https://example.com",
            "content": "Web search requires TAVILY_API_KEY"
        }])


class WebFetchTool(BaseTool):
    """Web page fetch tool"""
    
    name: str = "web_fetch"
    description: str = """Fetch and extract content from a web page.
Returns readable text content."""
    
    def _run(self, url: str, max_chars: int = 4000) -> str:
        """Fetch web page"""
        import requests
        
        # Try Jina AI reader
        jina_key = os.getenv("JINA_API_KEY")
        if jina_key:
            try:
                resp = requests.get(
                    f"https://r.jina.ai/{url}",
                    headers={"Authorization": f"Bearer {jina_key}"},
                    timeout=30
                )
                if resp.status_code == 200:
                    content = resp.text[:max_chars]
                    return f"Content from {url}:\n\n{content}"
            except:
                pass
        
        # Fallback: basic fetch
        try:
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            content = resp.text[:max_chars]
            return f"Fetched from {url}:\n\n{content[:1000]}..."
        except Exception as e:
            return f"Error fetching {url}: {str(e)}"


class ImageSearchTool(BaseTool):
    """Image search tool"""
    
    name: str = "image_search"
    description: str = """Search for images on the web.
Returns image URLs."""
    
    def _run(self, query: str, num_images: int = 5) -> str:
        """Search images"""
        # Placeholder - would use DuckDuckGo or similar
        return json.dumps([{
            "query": query,
            "images": [],
            "note": "Image search requires configuration"
        }])


def get_community_tools() -> list[BaseTool]:
    """Get community tools"""
    return [
        WebSearchTool(),
        WebFetchTool(),
        ImageSearchTool(),
    ]
