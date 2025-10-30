import requests
from bs4 import BeautifulSoup

RSS_FEEDS = {
    "BBC": "http://feeds.bbci.co.uk/news/rss.xml",
    "CNN": "http://rss.cnn.com/rss/edition.rss",
    "FOX": "https://moxie.foxnews.com/google-publisher/latest.xml",
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
