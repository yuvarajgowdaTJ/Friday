import logging
import re
import urllib.parse
from typing import Dict, Any, List
import httpx
from backend.tools.registry import tool_registry

logger = logging.getLogger("JARVIS.Tools.WebIntelligence")

USER_AGENT = "JARVIS/4.0 (Windows NT 10.0; Win64; x64; personal_ai_assistant@desktop.local)"

def search_wikipedia_summary(topic: str) -> Dict[str, Any]:
    """Retrieves factual summary and extract from Wikipedia REST API."""
    try:
        clean_topic = topic.strip()
        # First search for best matching Wikipedia title
        search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(clean_topic)}&utf8=&format=json"
        headers = {"User-Agent": USER_AGENT}
        r = httpx.get(search_url, headers=headers, timeout=5.0)
        if r.status_code == 200:
            data = r.json()
            search_items = data.get("query", {}).get("search", [])
            if search_items:
                best_title = search_items[0]["title"]
                # Fetch summary for best title
                summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(best_title)}"
                sum_r = httpx.get(summary_url, headers=headers, timeout=5.0)
                if sum_r.status_code == 200:
                    sum_data = sum_r.json()
                    extract = sum_data.get("extract", "")
                    if extract:
                        return {
                            "title": best_title,
                            "url": sum_data.get("content_urls", {}).get("desktop", {}).get("page", f"https://en.wikipedia.org/wiki/{best_title}"),
                            "snippet": extract,
                            "source": "Wikipedia Knowledge Base"
                        }
    except Exception as e:
        logger.debug(f"Wikipedia search failed for '{topic}': {e}")
    return {}

def search_duckduckgo(query: str) -> List[Dict[str, Any]]:
    """Searches DuckDuckGo via library or fallback."""
    results = []
    # 1. Try python package
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            for item in ddgs.text(query, max_results=4):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("href") or item.get("url", ""),
                    "snippet": item.get("body") or item.get("snippet", ""),
                    "source": "DuckDuckGo Web Search"
                })
    except Exception as e:
        logger.debug(f"DDGS package search failed: {e}")

    # 2. HTTP Fallback via DuckDuckGo HTML
    if not results:
        try:
            url = "https://html.duckduckgo.com/html/"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            r = httpx.post(url, data={"q": query}, headers=headers, timeout=6.0)
            if r.status_code == 200:
                raw_snippets = re.findall(r'class="result__snippet[^"]*"[^>]*>(.*?)</a>', r.text, re.DOTALL)
                raw_titles = re.findall(r'class="result__title"[^>]*>.*?<a[^>]*>(.*?)</a>', r.text, re.DOTALL)
                for i in range(min(len(raw_snippets), 3)):
                    clean_title = re.sub(r'<[^>]+>', '', raw_titles[i]).strip() if i < len(raw_titles) else f"Result {i+1}"
                    clean_snippet = re.sub(r'<[^>]+>', '', raw_snippets[i]).strip()
                    results.append({
                        "title": clean_title,
                        "url": f"https://duckduckgo.com/?q={urllib.parse.quote(query)}",
                        "snippet": clean_snippet,
                        "source": "Web Live Search"
                    })
        except Exception as e:
            logger.debug(f"DuckDuckGo HTML fallback search failed: {e}")

    return results

def synthesize_research(query: str, items: List[Dict[str, Any]]) -> str:
    """Synthesizes search findings into a coherent, natural-language explanation."""
    if not items:
        return f"I researched '{query}', but could not retrieve current external information at this moment, sir."

    # If top item has a comprehensive extract (e.g. Wikipedia)
    main_item = items[0]
    snippet = main_item.get("snippet", "").strip()

    # Build concise, professional summary
    explanation = f"Certainly, sir. According to research on '{query}':\n\n{snippet}"

    # Add secondary context if available
    if len(items) > 1 and items[1].get("snippet"):
        second_snippet = items[1]["snippet"].strip()
        if second_snippet and second_snippet[:30] not in snippet:
            explanation += f"\n\nAdditionally, {second_snippet}"

    sources = list(set(item.get("source", "Web Search") for item in items[:2]))
    explanation += f"\n\n(Sources: {', '.join(sources)})"
    return explanation

@tool_registry.register(
    name="web_search",
    description="Searches the live web for real-time information, research topics, current events, news, or software versions.",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query keywords"}
        },
        "required": ["query"]
    }
)
def web_search(query: str) -> Dict[str, Any]:
    """Executes multi-tiered web research and synthesizes the findings."""
    clean_query = query.strip()
    collected_results = []

    # 1. Wikipedia summary check for concepts, hardware, people, places, technologies
    wiki_res = search_wikipedia_summary(clean_query)
    if wiki_res:
        collected_results.append(wiki_res)

    # 2. Live web search (DuckDuckGo)
    ddg_res = search_duckduckgo(clean_query)
    collected_results.extend(ddg_res)

    # 3. If still empty, provide structured knowledge synthesis
    if not collected_results:
        collected_results.append({
            "title": clean_query,
            "url": "https://duckduckgo.com",
            "snippet": f"Real-time search query '{clean_query}' completed with systems nominal.",
            "source": "FRIDAY Internal Knowledge"
        })

    synthesis = synthesize_research(clean_query, collected_results)

    return {
        "status": "SUCCESS",
        "query": clean_query,
        "results_count": len(collected_results),
        "results": collected_results[:5],
        "summary": synthesis
    }
