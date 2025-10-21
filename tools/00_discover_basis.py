# tools/00_discover_basis.py
import re, time, sys, random
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from tools.sap_sources import SAP_BASIS_SOURCES

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36 sap-basis-bot/1.0"
ALLOWED_HOSTS = ["community.sap.com", "help.sap.com", "developers.sap.com"]

MAX_PAGES_PER_SOURCE = 5
MAX_LINKS_TOTAL = 200  # Increased for more coverage

def get_html(url):
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=30)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"  HTTP error for {url}: {e}")
        return None

def extract_article_links(base_url, html):
    if not html:
        return []
        
    soup = BeautifulSoup(html, "html.parser")
    links = []
    
    # Multiple patterns for SAP content
    patterns = [
        r"/ba-p/\d+",  # Blog articles
        r"/document/\d+",  # Help documents
        r"/tutorials/",  # Tutorials
        r"/docs/",  # Documentation
    ]
    
    for a in soup.find_all("a", href=True):
        href = urljoin(base_url, a["href"])
        netloc = urlparse(href).netloc.lower()
        
        # Check if domain is allowed
        if not any(host in netloc for host in ALLOWED_HOSTS):
            continue
            
        # Check if it matches any content pattern
        if any(re.search(pattern, href) for pattern in patterns):
            # Clean URL
            clean_url = href.split("?")[0].split("#")[0]
            links.append(clean_url)
    
    # Remove duplicates while preserving order
    seen, uniq = set(), []
    for u in links:
        if u not in seen:
            uniq.append(u)
            seen.add(u)
    return uniq

def find_next_page(base_url, html):
    if not html:
        return None
        
    soup = BeautifulSoup(html, "html.parser")
    
    # Multiple strategies for finding next page
    next_selectors = [
        'a[rel="next"]',
        'a:contains("Next")',
        'a:contains(">")',
        '.pagination-next a',
        '.next-page a',
    ]
    
    for selector in next_selectors:
        try:
            a = soup.select_one(selector)
            if a and a.get("href"):
                return urljoin(base_url, a["href"])
        except:
            continue
            
    return None

def main():
    collected = []
    print(f"Starting discovery with {len(SAP_BASIS_SOURCES)} sources...")
    
    for start_url in SAP_BASIS_SOURCES:
        url, pages = start_url, 0
        print(f"\nProcessing source: {start_url}")
        
        while url and pages < MAX_PAGES_PER_SOURCE and len(collected) < MAX_LINKS_TOTAL:
            print(f"  Page {pages + 1}: {url}")
            
            html = get_html(url)
            if not html:
                break
                
            links = extract_article_links(url, html)
            print(f"    Found {len(links)} article links")
            
            for u in links:
                if len(collected) >= MAX_LINKS_TOTAL:
                    break
                if u not in collected:
                    collected.append(u)
                    print(f"      + {u}")
            
            url = find_next_page(url, html)
            pages += 1
            time.sleep(1 + random.random())  # Be respectful
    
    # Write results
    with open("data/seeds.txt", "w", encoding="utf-8") as f:
        for u in collected:
            f.write(u + "\n")
    
    print(f"\nDiscovery complete: {len(collected)} URLs written to data/seeds.txt")

if __name__ == "__main__":
    main()
