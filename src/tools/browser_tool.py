"""
Browser tool for making HTTP requests and fetching web content.
"""
import aiohttp
import asyncio
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
import json

class BrowserTool:
    """Tool for making HTTP requests and processing web content."""
    
    def __init__(self, headers: Optional[Dict[str, str]] = None):
        """
        Initialize the browser tool.
        
        Args:
            headers: Optional default headers for requests
        """
        self.headers = headers or {
            'User-Agent': 'Super-Gemini/1.0 (+https://github.com/codedwithlikhon/Super-Gemini)'
        }
        
    async def fetch(self, url: str, method: str = "GET", data: Any = None,
                   timeout: int = 30, parse_html: bool = False) -> Dict[str, Any]:
        """
        Fetch content from a URL.
        
        Args:
            url: The URL to fetch
            method: HTTP method (GET/POST/etc)
            data: Optional data for POST requests
            timeout: Request timeout in seconds
            parse_html: Whether to parse HTML content
            
        Returns:
            Dict containing response data and metadata
        """
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.request(
                    method=method,
                    url=url,
                    data=data,
                    timeout=timeout
                ) as response:
                    
                    content = await response.text()
                    
                    result = {
                        "status": "success",
                        "status_code": response.status,
                        "headers": dict(response.headers),
                        "url": str(response.url)
                    }
                    
                    if parse_html and 'text/html' in response.headers.get('content-type', ''):
                        # Parse HTML
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        # Extract useful elements
                        result.update({
                            "title": soup.title.string if soup.title else None,
                            "text": soup.get_text(),
                            "links": [a.get('href') for a in soup.find_all('a', href=True)],
                            "meta": {
                                tag.get("name", tag.get("property")): tag.get("content")
                                for tag in soup.find_all("meta")
                                if tag.get("name") or tag.get("property")
                            }
                        })
                    else:
                        # Try parsing as JSON
                        try:
                            result["data"] = json.loads(content)
                        except json.JSONDecodeError:
                            result["content"] = content
                            
                    return result
                    
        except asyncio.TimeoutError:
            return {
                "status": "timeout",
                "error": f"Request timed out after {timeout}s",
                "url": url
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "url": url
            }