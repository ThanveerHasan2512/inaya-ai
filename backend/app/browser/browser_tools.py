import webbrowser
import urllib.parse
from typing import Dict, Any


def open_website(url: str) -> Dict[str, Any]:
    """
    Safely opens an approved web address in the user's default browser.
    """
    clean_url = url.strip()
    if not clean_url.startswith("http://") and not clean_url.startswith("https://"):
        clean_url = "https://" + clean_url

    try:
        parsed = urllib.parse.urlparse(clean_url)
        if not parsed.netloc:
            return {
                "success": False,
                "action": "open_website",
                "error": f"Invalid URL: '{url}'",
                "verification_status": "failed",
            }

        opened = webbrowser.open(clean_url)
        return {
            "success": True,
            "action": "open_website",
            "url": clean_url,
            "domain": parsed.netloc,
            "verification_status": "verified" if opened else "unverified",
            "details": f"Navigated browser to '{clean_url}'.",
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "action": "open_website", "error": str(exc), "verification_status": "failed"}


def search_web(query: str) -> Dict[str, Any]:
    """
    Opens a web search for the user's query in the browser.
    """
    encoded_query = urllib.parse.quote_plus(query.strip())
    search_url = f"https://www.google.com/search?q={encoded_query}"
    res = open_website(search_url)
    res["action"] = "search_web"
    res["query"] = query
    res["details"] = f"Opened web search for '{query}' in browser."
    return res
