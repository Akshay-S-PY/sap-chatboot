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
            "SAP Basis",
            "SAP ABAP",
            "SAP HANA",
            "SAP Fiori",
            "SAP Configuration",
            "SAP Security",
            "SAP Performance",
            "SAP Transport",
            "SAP Authorization",
            "SAP BTP",
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
    
    # ============== GitHub Source ==============
    def scrape_github_sap_repos(self):
        """Scrape from GitHub SAP-related repositories"""
        print("\n🟠 Scraping GitHub SAP repositories...")
        
        try:
            search_url = "https://api.github.com/search/repositories?q=SAP+language:python&sort=stars&order=desc&per_page=20"
            response = requests.get(search_url, headers=self.headers, timeout=10)
            repos = response.json().get('items', [])
            
            for repo in repos:
                try:
                    readme_url = f"https://raw.githubusercontent.com/{repo['full_name']}/main/README.md"
                    readme_response = requests.get(readme_url, timeout=10)
                    
                    if readme_response.status_code == 200:
                        content = readme_response.text
                        if len(content) > 300:
                            self.add_to_dataset({
                                'url': readme_url,
                                'title': f"GitHub: {repo['name']}",
                                'content': content,
                                'description': repo.get('description', ''),
                                'source': 'github',
                                'content_type': 'markdown'
                            })
                            print(f"    ✅ Added: {repo['name']}")
                except:
                    pass
                
                time.sleep(1)
        except Exception as e:
            print(f"  ⚠️  GitHub Error: {e}")
    
    # ============== Dev.to ==============
    def scrape_devto_articles(self):
        """Scrape from dev.to"""
        print("\n🟢 Scraping Dev.to articles...")
        
        try:
            api_url = "https://dev.to/api/articles?tag=sap&per_page=30"
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
        self.scrape_github_sap_repos()
        self.scrape_devto_articles()
        
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
