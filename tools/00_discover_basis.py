import re, time, sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36 sap-basis-bot/1.0"
ALLOWED_HOST = "community.sap.com"

# Listing pages (add more if you find good hubs)
LISTING_STARTS = [
    # Basis Technology hub you shared
    "https://community.sap.com/t5/c-khhcw49343/Basis+Technology/pd-p/7bf2eaed-4604-44ae-bad7-d2d2d5c58c54",
    # Blog search page filtered to blogs, query=basis
    "https://community.sap.com/t5/forums/searchpage/tab/message?advanced=false&allow_punctuation=false&filter=location&location=blog-board:learningblog-board&q=basis",
]

MAX_PAGES_PER_SOURCE = 3   # follow pagination shallowly
MAX_LINKS_TOTAL = 80       # cap per run

def get_html(url):
    r = requests.get(url, headers={"User-Agent": UA}, timeout=30)
    r.raise_for_status()
    return r.text

def extract_article_links(base_url, html):
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = urljoin(base_url, a["href"])
        netloc = urlparse(href).netloc.lower()
        if ALLOWED_HOST in netloc and re.search(r"/ba-p/\d+", href):
            links.append(href.split("?")[0])
    # unique preserve order
    seen, uniq = set(), []
    for u in links:
        if u not in seen:
            uniq.append(u); seen.add(u)
    return uniq

def find_next_page(base_url, html):
    soup = BeautifulSoup(html, "html.parser")
    # try rel=next or text "Next" or right chevron
    a = soup.find("a", attrs={"rel":"next"}) or soup.find("a", string=re.compile(r"\bNext\b", re.I))
    if a and a.get("href"):
        return urljoin(base_url, a["href"])
    return None

def main():
    collected = []
    for start in LISTING_STARTS:
        url, pages = start, 0
        while url and pages < MAX_PAGES_PER_SOURCE and len(collected) < MAX_LINKS_TOTAL:
            print(f"[discover] {start} page {pages+1}")
            try:
                html = get_html(url)
            except Exception as e:
                print("  fetch error:", e, file=sys.stderr)
                break
            links = extract_article_links(url, html)
            print(f"  found {len(links)} article links")
            for u in links:
                if len(collected) >= MAX_LINKS_TOTAL: break
                if u not in collected: collected.append(u)
            url = find_next_page(url, html)
            pages += 1
            time.sleep(1)
    with open("data/seeds.txt", "w", encoding="utf-8") as f:
        for u in collected:
            f.write(u + "\n")
    print(f"[discover] wrote {len(collected)} URLs to data/seeds.txt")

if __name__ == "__main__":
    main()
