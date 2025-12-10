# tools/build_dataset.py
"""
Enhanced SAP Dataset Builder
Scrapes from multiple free sources:
- SAP Community blogs
- GitHub SAP repositories
- SAP official documentation
- Dev.to & tech blogs
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path
from urllib.parse import urljoin, quote
import re
from datetime import datetime
import hashlib

class SAPDatasetBuilder:
    def __init__(self):
        self.dataset = []
        self.seen_urls = set()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
    
    def setup_directories(self):
        """Create necessary directories"""
        Path("data").mkdir(exist_ok=True)
        Path("data/raw").mkdir(exist_ok=True)
    
    # ============== SAP Community Source ==============
    def scrape_sap_community(self):
        """Scrape from SAP Community blogs"""
        print("\n🔵 Scraping SAP Community blogs...")
        
        search_queries = [
            # Core admin/dev topics
            "SAP Basis",
            "SAP ABAP",
            "SAP HANA",
            "SAP BW",
            "SAP Fiori",
            "SAP UI5",
            "SAP BTP",
            "SAP CPI",
            # Security / performance / transports
            "SAP Security",
            "SAP Authorization",
            "SAP Roles",
            "SAP GRC",
            "SAP Performance",
            "SAP Transport",
            # Cloud and integration
            "SAP Integration Suite",
            "SAP Cloud",
            "SAP Datasphere",
            "SAP Analytics Cloud",
            # Developer workflows
            "SAP CDS",
            "SAP OData",
            "SAP RAP",
        ]
        
        for query in search_queries:
            try:
                search_url = f"https://community.sap.com/search/?q={quote(query)}&ct=blog"
                print(f"  🔍 Searching: {query}")
                
                response = requests.get(search_url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find article links
                for link in soup.find_all('a', href=re.compile(r'/ba-p/\d+')):
                    href = link.get('href', '')
                    if '/ba-p/' in href:
                        full_url = urljoin('https://community.sap.com', href)
                        if full_url not in self.seen_urls:
                            self.seen_urls.add(full_url)
                            self.scrape_article(full_url, 'sap_community')
                
                time.sleep(2)
            except Exception as e:
                print(f"    ⚠️  Error: {e}")

    # ============== SAP Community RSS (broader) ==============
    def scrape_sap_community_rss(self):
        """Pull recent posts via SAP Community RSS feed"""
        print("\n🔵 Scraping SAP Community RSS feed...")
        feed_url = "https://blogs.sap.com/feed/"
        try:
            resp = requests.get(feed_url, headers=self.headers, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, 'xml')
            items = soup.find_all('item')[:100]
            for item in items:
                title = item.title.get_text(strip=True)
                link = item.link.get_text(strip=True)
                content = item.description.get_text(strip=True) if item.description else ''
                content = re.sub(r'<[^>]+>', ' ', content)
                content = re.sub(r'\s+', ' ', content).strip()
                if len(content) > 300:
                    self.add_to_dataset({
                        'url': link,
                        'title': title,
                        'content': content[:15000],
                        'source': 'sap_community_rss'
                    })
                    print(f"    ✅ Added: {title[:60]}")
                time.sleep(0.2)
        except Exception as e:
            print(f"  ⚠️  SAP RSS error: {e}")
    
    # ============== GitHub Source ==============
    def scrape_github_sap_repos(self):
        """Scrape from GitHub SAP-related repositories"""
        print("\n🟠 Scraping GitHub SAP repositories...")

        queries = [
            "SAP language:python",
            "SAP language:typescript",
            "SAP language:javascript",
            "SAP language:java",
            "ABAP SAP",
        ]

        for q in queries:
            try:
                search_url = f"https://api.github.com/search/repositories?q={quote(q)}&sort=stars&order=desc&per_page=30"
                response = requests.get(search_url, headers=self.headers, timeout=10)
                repos = response.json().get('items', [])

                for repo in repos:
                    try:
                        # Try common default branches
                        for branch in ["main", "master"]:
                            readme_url = f"https://raw.githubusercontent.com/{repo['full_name']}/{branch}/README.md"
                            readme_response = requests.get(readme_url, timeout=10)
                            if readme_response.status_code == 200:
                                content = readme_response.text
                                if len(content) > 300:
                                    self.add_to_dataset({
                                        'url': readme_url,
                                        'title': f"GitHub: {repo['name']}",
                                        'content': content[:15000],
                                        'description': repo.get('description', ''),
                                        'source': 'github',
                                        'content_type': 'markdown'
                                    })
                                    print(f"    ✅ Added: {repo['name']}")
                                    break
                    except Exception:
                        pass

                    time.sleep(0.6)
            except Exception as e:
                print(f"  ⚠️  GitHub Error for query '{q}': {e}")
            time.sleep(1.5)
    
    # ============== Dev.to ==============
    def scrape_devto_articles(self):
        """Scrape from dev.to"""
        print("\n🟢 Scraping Dev.to articles...")
        
        try:
            api_url = "https://dev.to/api/articles?tag=sap&per_page=100"
            response = requests.get(api_url, headers=self.headers, timeout=10)
            articles = response.json()
            
            for article in articles:
                if article['readable_publish_date']:
                    content = article.get('body_markdown', '') or article.get('description', '')
                    self.add_to_dataset({
                        'url': article['url'],
                        'title': article['title'],
                        'content': content,
                        'author': article['user']['name'],
                        'source': 'devto',
                        'published': article['published_at']
                    })
                    print(f"    ✅ Added: {article['title'][:50]}")
                
                time.sleep(0.5)
        except Exception as e:
            print(f"  ⚠️  Error: {e}")

    # ============== Medium ==============
    def scrape_medium_tag(self):
        """Scrape Medium articles tagged sap via RSS (public)"""
        print("\n🟣 Scraping Medium tag: sap ...")
        feed_url = "https://medium.com/feed/tag/sap"
        try:
            resp = requests.get(feed_url, headers=self.headers, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, 'xml')
            items = soup.find_all('item')[:50]
            for item in items:
                title = item.title.get_text(strip=True)
                link = item.link.get_text(strip=True)
                content = item.find('content:encoded')
                content_text = content.get_text(strip=True) if content else ''
                # Basic cleanup
                content_text = re.sub(r'<[^>]+>', ' ', content_text)
                content_text = re.sub(r'\s+', ' ', content_text).strip()
                if len(content_text) > 300:
                    self.add_to_dataset({
                        'url': link,
                        'title': title,
                        'content': content_text[:15000],
                        'source': 'medium'
                    })
                    print(f"    ✅ Added: {title[:60]}")
                time.sleep(0.3)
        except Exception as e:
            print(f"  ⚠️  Medium scrape error: {e}")

    # ============== SAP Developers Tutorials ==============
    def scrape_sap_developers_tutorials(self):
        """Scrape tutorial listings from developers.sap.com/tutorials"""
        print("\n🟡 Scraping SAP Developers tutorials...")
        base = "https://developers.sap.com"
        listing_urls = [
            f"{base}/tutorial-navigator.html?tag=software-product-function:technology-platform/sap-btp",
            f"{base}/tutorial-navigator.html?tag=software-product-function:analytics/sap-analytics-cloud",
            f"{base}/tutorial-navigator.html?tag=software-product-function:app-development/sapui5",
            f"{base}/tutorial-navigator.html?tag=software-product-function:database/sap-hana",
        ]
        for url in listing_urls:
            try:
                resp = requests.get(url, headers=self.headers, timeout=12)
                if resp.status_code != 200:
                    continue
                soup = BeautifulSoup(resp.content, 'html.parser')
                for a in soup.find_all('a', href=re.compile(r"/tutorials/[^\s]+\.html")):
                    href = a.get('href')
                    full = urljoin(base, href)
                    if full not in self.seen_urls:
                        self.seen_urls.add(full)
                        self.scrape_tutorial(full)
                time.sleep(1)
            except Exception as e:
                print(f"  ⚠️  Tutorials listing error: {e}")

    def scrape_tutorial(self, url):
        try:
            resp = requests.get(url, headers=self.headers, timeout=12)
            if resp.status_code != 200:
                return False
            soup = BeautifulSoup(resp.content, 'html.parser')
            title = soup.find('h1')
            title = title.get_text(strip=True) if title else "SAP Tutorial"
            content_el = soup.find('main') or soup.find('article') or soup.find('body')
            content = content_el.get_text(separator=' ', strip=True) if content_el else ''
            content = re.sub(r'\s+', ' ', content)[:20000]
            if len(content) > 300:
                self.add_to_dataset({
                    'url': url,
                    'title': title,
                    'content': content,
                    'source': 'sap_developers'
                })
                print(f"    ✅ Added tutorial: {title[:60]}")
                return True
        except Exception as e:
            print(f"    ⚠️  Tutorial error: {e}")
        return False
    
    def scrape_article(self, url, source):
        """Scrape article with structured parsing"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.find('h1')
            if title:
                title = title.get_text().strip()
            else:
                title = "SAP Article"
            
            # Extract content
            content_elem = soup.find(['article', 'div'], class_=re.compile('content|post|message', re.I))
            if content_elem:
                content = content_elem.get_text()
            else:
                body = soup.find(['body', 'main'])
                content = body.get_text() if body else ""
            
            # Clean content
            content = re.sub(r'\s+', ' ', content).strip()
            
            if len(content) > 300:
                self.add_to_dataset({
                    'url': url,
                    'title': title,
                    'content': content[:10000],
                    'source': source
                })
                print(f"    ✅ Added: {title[:40]}")
                return True
        except Exception as e:
            print(f"    ⚠️  Error: {e}")
        
        return False
    
    def add_to_dataset(self, article_data):
        """Add article to dataset with deduplication"""
        content_hash = hashlib.md5(
            article_data.get('content', '').encode()
        ).hexdigest()[:8]
        
        article_data['id'] = content_hash
        article_data['timestamp'] = datetime.now().isoformat()
        
        self.dataset.append(article_data)
    
    def build(self):
        """Build comprehensive dataset"""
        print("🚀 Starting comprehensive SAP dataset build...")
        self.setup_directories()
        
        self.scrape_sap_community()
        self.scrape_sap_community_rss()
        self.scrape_github_sap_repos()
        self.scrape_devto_articles()
        self.scrape_medium_tag()
        self.scrape_sap_developers_tutorials()
        
        # Save dataset
        output_file = "data/sap_dataset.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.dataset, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Dataset build completed!")
        print(f"   📊 Total documents: {len(self.dataset)}")
        print(f"   💾 Saved to: {output_file}")
        
        return self.dataset

if __name__ == "__main__":
    builder = SAPDatasetBuilder()
    dataset = builder.build()
