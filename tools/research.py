# ABOUTME: Web research tools
# ABOUTME: Search, fetch, analyze web content with source tracking

from claude_agent_sdk import tool
from typing import Any, Dict, List
import httpx
import json
from datetime import datetime

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

try:
    from ddgs import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    try:
        # Fallback to old package name
        from duckduckgo_search import DDGS
        DDGS_AVAILABLE = True
    except ImportError:
        DDGS_AVAILABLE = False


class ResearchTools:
    def __init__(self, memory_manager, session_id=None):
        self.memory = memory_manager
        self.session_id = session_id
        self.client = httpx.AsyncClient(timeout=30.0)

    def get_tools(self):
        """Return list of research tools"""
        return [
            self._web_search_tool(),
            self._fetch_url_tool(),
            self._analyze_research_tool()
        ]

    def _web_search_tool(self):
        @tool(
            "web_search",
            "Search the web for information using DuckDuckGo. Returns search results with titles, URLs, and snippets.",
            {
                "query": str,
                "max_results": int  # Default 5
            }
        )
        async def web_search(args: Dict[str, Any]) -> Dict[str, Any]:
            query = args["query"]
            max_results = args.get("max_results", 5)

            if not DDGS_AVAILABLE:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"[ERROR] DuckDuckGo search not available\n\n"
                               f"Install: pip install duckduckgo-search\n\n"
                               f"Then search for: {query}"
                    }]
                }

            try:
                # Perform search - using synchronous DDGS
                results = []
                ddgs = DDGS()
                search_results = ddgs.text(query, max_results=max_results)

                # Convert generator to list
                for r in search_results:
                    results.append({
                        "title": r.get("title", "No title"),
                        "url": r.get("href", ""),
                        "snippet": r.get("body", "No description")
                    })

                if not results:
                    return {
                        "content": [{
                            "type": "text",
                            "text": f"[INFO] No results found for: {query}"
                        }]
                    }

                # Format output
                output = f"[OK] Found {len(results)} result(s) for: {query}\n\n"
                for i, r in enumerate(results, 1):
                    output += f"**{i}. {r['title']}**\n"
                    output += f"   URL: {r['url']}\n"
                    output += f"   {r['snippet']}\n\n"

                output += f"\n[TIP] Use fetch_url tool to read full content from any URL above"

                return {
                    "content": [{
                        "type": "text",
                        "text": output
                    }]
                }

            except Exception as e:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"[ERROR] Search failed: {str(e)}\n\n"
                               f"Query: {query}"
                    }]
                }

        return web_search

    def _fetch_url_tool(self):
        @tool(
            "fetch_url",
            "Fetch content from a URL and extract clean text. Returns page content for analysis.",
            {
                "url": str,
                "extract_links": bool  # Whether to extract links
            }
        )
        async def fetch_url(args: Dict[str, Any]) -> Dict[str, Any]:
            url = args["url"]
            extract_links = args.get("extract_links", False)

            try:
                response = await self.client.get(url, follow_redirects=True)
                response.raise_for_status()

                content_type = response.headers.get("content-type", "")

                # Handle HTML content
                if "text/html" in content_type:
                    if not BS4_AVAILABLE:
                        # Fallback to basic extraction
                        text = response.text[:10000]
                        return {
                            "content": [{
                                "type": "text",
                                "text": f"[WARN] BeautifulSoup not installed. Raw HTML preview:\n\n{text}\n\n"
                                       f"Install: pip install beautifulsoup4 lxml"
                            }]
                        }

                    # Parse with BeautifulSoup
                    soup = BeautifulSoup(response.text, 'lxml')

                    # Extract title
                    title = soup.find('title')
                    title_text = title.string if title else "No title"

                    # Remove script and style elements
                    for script in soup(["script", "style", "nav", "footer", "header"]):
                        script.decompose()

                    # Extract main content
                    article = (
                        soup.find('article') or
                        soup.find('main') or
                        soup.find('div', class_='content') or
                        soup.find('div', id='content') or
                        soup.body
                    )

                    if article:
                        text = article.get_text(separator='\n', strip=True)
                    else:
                        text = soup.get_text(separator='\n', strip=True)

                    # Clean up whitespace
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    clean_text = '\n'.join(lines)

                    output = f"[OK] Fetched: {url}\n\n"
                    output += f"**Title:** {title_text}\n\n"
                    output += f"**Content:** ({len(clean_text)} chars)\n\n"
                    output += f"{clean_text[:8000]}\n"  # Limit to 8k chars

                    if len(clean_text) > 8000:
                        output += f"\n... (truncated, {len(clean_text) - 8000} more chars)"

                    # Extract links if requested
                    if extract_links:
                        links = []
                        for a in soup.find_all('a', href=True, limit=20):
                            link_text = a.get_text(strip=True)
                            if link_text and len(link_text) > 0:
                                links.append({
                                    "text": link_text[:100],
                                    "url": a['href']
                                })

                        if links:
                            output += f"\n\n**Links found:** {len(links)}\n"
                            for link in links[:10]:
                                output += f"- [{link['text']}]({link['url']})\n"

                    return {
                        "content": [{
                            "type": "text",
                            "text": output
                        }]
                    }

                # Handle plain text
                elif "text/plain" in content_type:
                    text = response.text[:10000]
                    return {
                        "content": [{
                            "type": "text",
                            "text": f"[OK] Fetched: {url}\n\n{text}"
                        }]
                    }

                # Unsupported content type
                else:
                    return {
                        "content": [{
                            "type": "text",
                            "text": f"[WARN] Unsupported content type: {content_type}"
                        }]
                    }

            except httpx.HTTPError as e:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"[ERROR] Failed to fetch {url}: {str(e)}"
                    }]
                }

        return fetch_url

    def _analyze_research_tool(self):
        @tool(
            "analyze_research",
            "Analyze research findings and save with sources. Use after gathering information from multiple sources.",
            {
                "topic": str,
                "sources": list,  # List of URLs or source descriptions
                "findings": str,   # Analysis text
                "key_insights": list  # List of key insight strings
            }
        )
        async def analyze_research(args: Dict[str, Any]) -> Dict[str, Any]:
            topic = args["topic"]
            sources = args["sources"]
            findings = args["findings"]
            insights = args.get("key_insights", [])

            # Build analysis document
            analysis = f"# Research Analysis: {topic}\n\n"
            analysis += f"**Date:** {datetime.now().isoformat()}\n\n"

            analysis += "## Sources\n\n"
            for i, source in enumerate(sources, 1):
                analysis += f"{i}. {source}\n"

            analysis += "\n## Findings\n\n"
            analysis += findings

            if insights:
                analysis += "\n\n## Key Insights\n\n"
                for insight in insights:
                    analysis += f"- {insight}\n"

            # Save to database
            research_id = await self.memory.save_research(
                query=topic,
                sources=sources,
                analysis=analysis,
                session_id=self.session_id
            )

            return {
                "content": [{
                    "type": "text",
                    "text": f"[OK] Research analysis saved\n"
                           f"ID: {research_id}\n"
                           f"Topic: {topic}\n"
                           f"Sources: {len(sources)}\n"
                           f"Insights: {len(insights)}"
                }]
            }

        return analyze_research

    async def close(self):
        """Clean up resources"""
        await self.client.aclose()
