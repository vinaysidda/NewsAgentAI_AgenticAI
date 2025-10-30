import requests
from bs4 import BeautifulSoup

RSS_FEEDS = {
    "BBC": "http://feeds.bbci.co.uk/news/rss.xml",
    "CNN": "http://rss.cnn.com/rss/edition.rss",
    "FOX": "https://moxie.foxnews.com/google-publisher/latest.xml",
    "TheHindu": "https://www.thehindu.com/news/national/feeder/default.rss",
}

def fetch_rss_articles(source: str, limit: int = 10):
    url = RSS_FEEDS[source]
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "xml")
    items = soup.find_all("item")[:limit]
    results = []
    for it in items:
        title = (it.title.text if it.title else "No title").strip()
        link = (it.link.text if it.link else "").strip()
        desc = (it.description.text if it.description else "").strip()
        results.append({"title": title, "url": link, "content": desc})
    return results

# OPTIONAL: direct HTML crawling (respect robots.txt/TOS)
def fetch_html_article(url: str) -> str:
    hdrs = {"User-Agent": "Mozilla/5.0"}
    html = requests.get(url, headers=hdrs, timeout=10).text
    soup = BeautifulSoup(html, "html.parser")
    # crude extraction example:
    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    return "\n".join(paragraphs)


# import requests
# from bs4 import BeautifulSoup

# RSS_FEEDS = {
#     "BBC": "http://feeds.bbci.co.uk/news/rss.xml",
#     "CNN": "http://rss.cnn.com/rss/edition.rss",
#     "FOX": "https://moxie.foxnews.com/google-publisher/latest.xml",
#     "TheHindu": "https://www.thehindu.com/news/national/feeder/default.rss",
# }

# def fetch_rss_articles(source: str, limit: int = 10):
#     url = RSS_FEEDS.get(source)
#     if not url:
#         raise ValueError(f"Unknown source: {source}")

#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
#                       " AppleWebKit/537.36 (KHTML, like Gecko)"
#                       " Chrome/118.0.0.0 Safari/537.36"
#     }

#     r = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
#     r.raise_for_status()

#     soup = BeautifulSoup(r.text, "xml")
#     items = soup.find_all("item")[:limit]

#     results = []
#     for it in items:
#         title = it.title.text if it.title else "No title"
#         link = it.link.text if it.link else ""
#         desc = it.description.text if it.description else ""
#         results.append({"title": title, "url": link, "content": desc})
#     return results
