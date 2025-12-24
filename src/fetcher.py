import requests
from bs4 import BeautifulSoup


def fetch(url, timeout=10):
    """Pobiera surowy HTML strony."""
    headers = {"User-Agent": "ArticleAgent/1.0 (+https://example.com)"}
    resp = requests.get(url, timeout=timeout, headers=headers)
    resp.raise_for_status()
    return resp.text


def extract_text(html):
    """Ekstrahuje główną treść HTML do tekstu czystego."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "header", "footer", "nav", "aside", "form"]):
        tag.decompose()

    # Preferuj <article> lub <main>, fallback to body
    content = soup.find("article") or soup.find("main") or soup.body
    if content is None:
        return ""
    text = content.get_text(separator="\n")
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return "\n".join(lines)


def fetch_article(url):
    """Zwraca dict: {url, title, text} """
    html = fetch(url)
    soup = BeautifulSoup(html, "html.parser")
    title = None
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    article_text = extract_text(html)
    return {"url": url, "title": title or url, "text": article_text}
