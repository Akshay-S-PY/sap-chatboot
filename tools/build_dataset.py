# tools/build_dataset.py
import requests
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path
from urllib.parse import urljoin
import re

def setup_directories():
    """Create necessary directories"""
    Path("data").mkdir(exist_ok=True)

def discover_sap_urls():
    """Discover SAP Basis URLs from community portal"""
    print("🔍 Discovering SAP Basis URLs...")
    
    base_urls = [
        "https://community.sap.com/t5/basis-blogs/bd-p/basis_blogs",
        "https://community.sap.com/t5/technology-blogs/bd-p/technology_blogs",
        "https://community.sap.com/search/?ct=blog&q=SAP%20Basis",
        "https://community.sap.com/search/?ct=blog&q=Basis%20Administration",
    ]
    
    all_urls = set()
    
    for base_url in base_urls:
        try:
            response = requests.get(base_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find article links
            links = soup.find_all('a', href=True)
            for link in links:
                href = link.get('href', '')
                if '/ba-p/' in href:
                    full_url = urljoin('https://community.sap.com', href)
                    all_urls.add(full_url.split('?')[0])  # Remove query params
            
            time.sleep(1)  # Be respectful
            
        except Exception as e:
            print(f"❌ Error processing {base_url}: {e}")
    
    urls_list = list(all_urls)
    print(f"✅ Found {len(urls_list)} URLs")
    return urls_list

def scrape_article(url):
    """Scrape individual article content"""
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title_elem = soup.find('title')
        title = title_elem.get_text().strip() if title_elem else "SAP Basis Article"
        
        # Extract content - try multiple selectors
        content_selectors = [
            'article',
            '[role="main"]',
            '.blog-post-content',
            '.article-content',
            'main'
        ]
        
        content = ""
        for selector in content_selectors:
            elements = soup.select(selector)
            for elem in elements:
                text = elem.get_text().strip()
                if len(text) > len(content):
                    content = text
        
        # If no structured content found, get all text
        if not content:
            content = soup.get_text()
        
        # Clean up content
        content = re.sub(r'\s+', ' ', content).strip()
        
        if len(content) > 100:  # Only keep substantial content
            return {
                'url': url,
                'title': title,
                'content': content,
                'source': 'sap_community',
                'timestamp': time.time()
            }
        
    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
    
    return None

def build_dataset():
    """Main function to build the dataset"""
    setup_directories()
    
    # Discover URLs
    urls = discover_sap_urls()
    
    # Scrape articles
    dataset = []
    successful = 0
    
    print("📄 Scraping articles...")
    for i, url in enumerate(urls):
        print(f"  Processing {i+1}/{len(urls)}: {url[:80]}...")
        
        article_data = scrape_article(url)
        if article_data:
            dataset.append(article_data)
            successful += 1
        
        time.sleep(1)  # Be respectful
    
    # Save dataset
    output_file = "data/sap_basis_dataset.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Dataset built: {successful}/{len(urls)} articles saved to {output_file}")
    return dataset

if __name__ == "__main__":
    build_dataset()
