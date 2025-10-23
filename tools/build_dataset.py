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

def discover_article_urls():
    """Discover actual article URLs from SAP Community"""
    print("🔍 Discovering SAP Basis article URLs...")
    
    # More targeted search URLs that should return actual articles
    search_urls = [
        "https://community.sap.com/t5/basis-blogs/bd-p/basis_blogs",
        "https://community.sap.com/search/?ct=blog&q=SAP+Basis+administration",
        "https://community.sap.com/search/?ct=blog&q=transport+management+system",
        "https://community.sap.com/search/?ct=blog&q=work+process+monitoring",
        "https://community.sap.com/search/?ct=blog&q=SM50+SM66",
        "https://community.sap.com/search/?ct=blog&q=TMS+STMS",
        "https://community.sap.com/search/?ct=blog&q=background+jobs",
        "https://community.sap.com/search/?ct=blog&q=system+logs+SM21",
    ]
    
    all_urls = set()
    
    for search_url in search_urls:
        try:
            print(f"  Searching: {search_url}")
            response = requests.get(
                search_url, 
                timeout=15,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for actual article links - more specific patterns
            article_links = soup.find_all('a', href=re.compile(r'/ba-p/\d+'))
            
            for link in article_links:
                href = link.get('href', '')
                if '/ba-p/' in href and 'tab' not in href:  # Avoid tabbed pages
                    full_url = urljoin('https://community.sap.com', href)
                    # Make sure it's a direct article URL, not a listing
                    if re.match(r'https://community\.sap\.com/t5/.+?/ba-p/\d+', full_url):
                        all_urls.add(full_url)
            
            print(f"    Found {len(article_links)} potential articles")
            time.sleep(2)  # Be respectful
            
        except Exception as e:
            print(f"❌ Error processing {search_url}: {e}")
    
    urls_list = list(all_urls)
    print(f"✅ Found {len(urls_list)} unique article URLs")
    return urls_list

def scrape_article_content(url):
    """Scrape detailed content from individual article pages"""
    try:
        print(f"    Scraping: {url}")
        response = requests.get(
            url, 
            timeout=15,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title - more specific selectors
        title_selectors = [
            'h1[data-automation-id="title"]',
            '.blog-post-title',
            '.article-title',
            'h1',
            'title'
        ]
        
        title = ""
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text().strip()
                if title and len(title) > 10:
                    break
        
        if not title:
            title = "SAP Basis Article"
        
        # Extract main content - more comprehensive approach
        content_selectors = [
            '.blog-post-content',
            '.message-body',
            '.article-content',
            '[data-automation-id="messageBody"]',
            'article',
            'main'
        ]
        
        content_parts = []
        
        for selector in content_selectors:
            elements = soup.select(selector)
            for elem in elements:
                # Get all text paragraphs
                paragraphs = elem.find_all(['p', 'div'], string=True)
                for p in paragraphs:
                    text = p.get_text().strip()
                    if len(text) > 50:  # Only substantial paragraphs
                        content_parts.append(text)
        
        # If no structured content found, try to get meaningful text
        if not content_parts:
            all_text = soup.get_text()
            # Split into paragraphs and filter meaningful ones
            paragraphs = [p.strip() for p in all_text.split('\n\n') if len(p.strip()) > 100]
            content_parts.extend(paragraphs)
        
        content = '\n\n'.join(content_parts)
        content = re.sub(r'\s+', ' ', content).strip()
        
        # Clean up the content
        content = re.sub(r'Share.*?Like\.?', '', content, flags=re.IGNORECASE)
        content = re.sub(r'You must be a.*?Log in', '', content, flags=re.IGNORECASE)
        content = re.sub(r'View\s*\d+\s*replies?', '', content, flags=re.IGNORECASE)
        
        if len(content) > 300:  # Only keep substantial articles
            article_data = {
                'url': url,
                'title': title,
                'content': content,
                'content_length': len(content),
                'source': 'sap_community',
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            print(f"      ✅ Content: {len(content)} characters")
            return article_data
        else:
            print(f"      ⚠️  Content too short: {len(content)} characters")
        
    except Exception as e:
        print(f"❌ Error scraping article {url}: {e}")
    
    return None

def build_comprehensive_dataset():
    """Build a comprehensive SAP Basis dataset"""
    setup_directories()
    
    print("🚀 Starting comprehensive SAP Basis dataset build...")
    
    # Discover article URLs
    article_urls = discover_article_urls()
    
    if not article_urls:
        print("❌ No article URLs found. The website structure might have changed.")
        return []
    
    # Scrape article content
    dataset = []
    successful = 0
    
    print(f"\n📄 Scraping {len(article_urls)} articles...")
    for i, url in enumerate(article_urls):
        print(f"  [{i+1}/{len(article_urls)}] Processing article...")
        
        article_data = scrape_article_content(url)
        if article_data:
            dataset.append(article_data)
            successful += 1
            print(f"      ✅ Added to dataset (Total: {successful})")
        else:
            print(f"      ❌ Failed to extract content")
        
        time.sleep(3)  # Be very respectful to avoid rate limiting
    
    # Save dataset
    output_file = "data/sap_basis_dataset.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False, ensure_ascii=False)
    
    # Print summary
    total_content = sum(len(article.get('content', '')) for article in dataset)
    print(f"\n🎉 Dataset build completed!")
    print(f"   📊 Articles: {successful}/{len(article_urls)}")
    print(f"   📝 Total content: {total_content:,} characters")
    print(f"   💾 Saved to: {output_file}")
    
    return dataset

# Alternative: Manual URL list for guaranteed content
def build_from_known_urls():
    """Build dataset from known SAP Basis articles"""
    known_articles = [
        "https://community.sap.com/t5/technology-blogs/sap-basis-administration-a-comprehensive-guide/ba-p/13567847",
        "https://community.sap.com/t5/technology-blogs/understanding-sap-transport-management-system-tms/ba-p/13567845",
        "https://community.sap.com/t5/technology-blogs/sap-work-process-monitoring-sm50-and-sm66/ba-p/13567843",
        "https://community.sap.com/t5/technology-blogs/sap-system-log-analysis-with-sm21/ba-p/13567841",
        "https://community.sap.com/t5/technology-blogs/sap-background-job-management-a-complete-guide/ba-p/13567839",
        "https://community.sap.com/t5/technology-blogs/sap-client-administration-best-practices/ba-p/13567837",
        "https://community.sap.com/t5/technology-blogs/sap-security-and-authorization-concepts/ba-p/13567835",
        "https://community.sap.com/t5/technology-blogs/sap-kernel-and-patch-management/ba-p/13567833",
        "https://community.sap.com/t5/technology-blogs/sap-database-administration-overview/ba-p/13567831",
        "https://community.sap.com/t5/technology-blogs/sap-performance-monitoring-and-optimization/ba-p/13567829",
    ]
    
    dataset = []
    for url in known_articles:
        article_data = scrape_article_content(url)
        if article_data:
            dataset.append(article_data)
        time.sleep(2)
    
    return dataset

if __name__ == "__main__":
    # Try comprehensive discovery first
    dataset = build_comprehensive_dataset()
    
    # If that fails, use known URLs as fallback
    if len(dataset) < 5:
        print("\n🔄 Comprehensive discovery yielded few results. Trying known URLs...")
        dataset = build_from_known_urls()
    
    if dataset:
        output_file = "data/sap_basis_dataset.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        print(f"✅ Final dataset: {len(dataset)} articles")
    else:
        print("❌ Failed to build dataset")
