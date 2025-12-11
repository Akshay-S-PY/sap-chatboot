# tools/build_dataset.py
"""
Enhanced SAP Dataset Builder v2.0
Scrapes from multiple free sources with focus on SAP Basis administration:
- SAP Community blogs
- SAP Help Portal (help.sap.com)
- SAP Wiki
- GitHub SAP repositories
- SAP Developers tutorials
- Dev.to & tech blogs
- StackOverflow
- SAP Notes (public summaries)
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
        self.seen_content_hashes = set()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        # SAP Basis Transaction Codes for targeted scraping
        self.sap_tcodes = [
            "SM50", "SM51", "SM21", "SM37", "SM36", "SM12", "SM13",
            "ST22", "ST02", "ST03", "ST04", "ST05", "ST06", "ST07",
            "SU01", "SU10", "SU53", "SUIM", "PFCG",
            "SE01", "SE09", "SE10", "SE11", "SE16", "SE37", "SE38", "SE80",
            "STMS", "SPAM", "SAINT",
            "RZ10", "RZ11", "RZ12", "RZ20", "RZ70",
            "SICF", "SMICM", "ICM",
            "AL08", "AL11", "AL05",
            "DB02", "DB13", "DB16",
            "SMLG", "SM66", "SM04",
            "SNOTE", "SUM", "SPS",
        ]
        
        # SAP Basis Topics for comprehensive coverage
        self.sap_basis_topics = [
            # Core Basis Administration
            "SAP Basis administration",
            "SAP system monitoring",
            "SAP performance tuning",
            "SAP memory management",
            "SAP work process",
            "SAP background jobs",
            "SAP transport management",
            "SAP client copy",
            "SAP system refresh",
            
            # User & Security
            "SAP user administration",
            "SAP role authorization",
            "SAP security audit",
            "SAP password policy",
            "SAP SSO single sign on",
            "SAP GRC access control",
            
            # Database & Storage
            "SAP HANA administration",
            "SAP database backup",
            "SAP archiving",
            "SAP table maintenance",
            "SAP data dictionary",
            
            # System Configuration
            "SAP profile parameters",
            "SAP instance configuration",
            "SAP RFC connection",
            "SAP system landscape",
            "SAP solution manager",
            
            # Troubleshooting
            "SAP dump analysis",
            "SAP short dump",
            "SAP system log",
            "SAP trace analysis",
            "SAP lock entry",
            "SAP update error",
            
            # Installation & Upgrade
            "SAP installation guide",
            "SAP upgrade procedure",
            "SAP kernel update",
            "SAP support package",
            "SAP note implementation",
            
            # Cloud & Modern
            "SAP BTP administration",
            "SAP Cloud Connector",
            "SAP Fiori administration",
            "SAP Gateway configuration",
            "S/4HANA migration",
        ]
    
    def setup_directories(self):
        """Create necessary directories"""
        Path("data").mkdir(exist_ok=True)
        Path("data/raw").mkdir(exist_ok=True)
    
    # ============== SAP Help Portal ==============
    def scrape_sap_help_portal(self):
        """Scrape from SAP Help Portal (help.sap.com) - Official documentation"""
        print("\n📘 Scraping SAP Help Portal...")
        
        # SAP Help Portal search URLs for Basis topics
        help_searches = [
            # Basis Administration
            "https://help.sap.com/docs/search?q=basis%20administration&locale=en-US&product=SAP_NETWEAVER",
            "https://help.sap.com/docs/search?q=system%20administration&locale=en-US&product=SAP_NETWEAVER",
            "https://help.sap.com/docs/search?q=transaction%20code&locale=en-US&product=SAP_NETWEAVER",
            "https://help.sap.com/docs/search?q=monitoring&locale=en-US&product=SAP_NETWEAVER",
            "https://help.sap.com/docs/search?q=performance&locale=en-US&product=SAP_NETWEAVER",
            # HANA
            "https://help.sap.com/docs/search?q=administration&locale=en-US&product=SAP_HANA_PLATFORM",
            "https://help.sap.com/docs/search?q=backup%20recovery&locale=en-US&product=SAP_HANA_PLATFORM",
            # S/4HANA
            "https://help.sap.com/docs/search?q=basis&locale=en-US&product=SAP_S4HANA_ON-PREMISE",
        ]
        
        for search_url in help_searches:
            try:
                print(f"  🔍 Searching: {search_url[:80]}...")
                response = requests.get(search_url, headers=self.headers, timeout=15)
                if response.status_code != 200:
                    continue
                    
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find documentation links
                for link in soup.find_all('a', href=re.compile(r'help\.sap\.com/docs/')):
                    href = link.get('href', '')
                    if href and href not in self.seen_urls:
                        full_url = href if href.startswith('http') else f"https://help.sap.com{href}"
                        self.seen_urls.add(full_url)
                        self.scrape_help_page(full_url)
                
                time.sleep(2)
            except Exception as e:
                print(f"    ⚠️  Error: {e}")
    
    def scrape_help_page(self, url):
        """Scrape individual SAP Help page"""
        try:
            response = requests.get(url, headers=self.headers, timeout=12)
            if response.status_code != 200:
                return False
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get title
            title = soup.find('h1') or soup.find('title')
            title = title.get_text(strip=True) if title else "SAP Help Document"
            
            # Get main content
            content_elem = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile('content', re.I))
            if content_elem:
                content = content_elem.get_text(separator=' ', strip=True)
            else:
                content = soup.get_text(separator=' ', strip=True)
            
            content = re.sub(r'\s+', ' ', content).strip()
            
            if len(content) > 500:
                self.add_to_dataset({
                    'url': url,
                    'title': f"SAP Help: {title}",
                    'content': content[:20000],
                    'source': 'sap_help_portal',
                    'content_type': 'documentation'
                })
                print(f"    ✅ Added: {title[:50]}")
                return True
        except Exception as e:
            print(f"    ⚠️  Help page error: {e}")
        return False

    # ============== SAP Wiki ==============
    def scrape_sap_wiki(self):
        """Scrape from SAP Wiki (wiki.scn.sap.com) - Community knowledge base"""
        print("\n📚 Scraping SAP Wiki...")
        
        # SAP Wiki URLs for transaction codes and Basis topics
        wiki_searches = []
        
        # Add transaction code searches
        for tcode in self.sap_tcodes[:20]:  # Top 20 tcodes
            wiki_searches.append(f"https://wiki.scn.sap.com/wiki/dosearchsite.action?queryString={tcode}")
        
        # Add topic searches
        for topic in ["Basis", "Administration", "Transport", "Authorization", "Performance"]:
            wiki_searches.append(f"https://wiki.scn.sap.com/wiki/dosearchsite.action?queryString=SAP+{topic}")
        
        for search_url in wiki_searches:
            try:
                print(f"  🔍 Wiki search...")
                response = requests.get(search_url, headers=self.headers, timeout=12)
                if response.status_code != 200:
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                for link in soup.find_all('a', href=re.compile(r'/wiki/display/')):
                    href = link.get('href', '')
                    full_url = urljoin('https://wiki.scn.sap.com', href)
                    if full_url not in self.seen_urls:
                        self.seen_urls.add(full_url)
                        self.scrape_wiki_page(full_url)
                
                time.sleep(1.5)
            except Exception as e:
                print(f"    ⚠️  Wiki error: {e}")
    
    def scrape_wiki_page(self, url):
        """Scrape individual wiki page"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                return False
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title = soup.find('h1', id='title-text') or soup.find('h1')
            title = title.get_text(strip=True) if title else "SAP Wiki Article"
            
            content_elem = soup.find('div', class_='wiki-content') or soup.find('main')
            content = content_elem.get_text(separator=' ', strip=True) if content_elem else ''
            content = re.sub(r'\s+', ' ', content).strip()
            
            if len(content) > 400:
                self.add_to_dataset({
                    'url': url,
                    'title': title,
                    'content': content[:15000],
                    'source': 'sap_wiki'
                })
                print(f"    ✅ Added wiki: {title[:50]}")
                return True
        except Exception as e:
            pass
        return False

    # ============== SAP Blogs - Transaction Code Focus ==============
    def scrape_sap_tcode_blogs(self):
        """Scrape blogs specifically about SAP transaction codes"""
        print("\n🔧 Scraping SAP Transaction Code content...")
        
        for tcode in self.sap_tcodes:
            try:
                # Search SAP Community for transaction code
                search_url = f"https://community.sap.com/search/?q={tcode}&ct=blog"
                print(f"  🔍 Transaction: {tcode}")
                
                response = requests.get(search_url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                for link in soup.find_all('a', href=re.compile(r'/ba-p/\d+')):
                    href = link.get('href', '')
                    if '/ba-p/' in href:
                        full_url = urljoin('https://community.sap.com', href)
                        if full_url not in self.seen_urls:
                            self.seen_urls.add(full_url)
                            self.scrape_article(full_url, 'sap_community_tcode')
                
                time.sleep(1.5)
            except Exception as e:
                print(f"    ⚠️  Error: {e}")

    # ============== SAP Community Source ==============
    def scrape_sap_community(self):
        """Scrape from SAP Community blogs with Basis focus"""
        print("\n🔵 Scraping SAP Community blogs...")
        
        # Combine general and Basis-specific queries
        search_queries = self.sap_basis_topics + [
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

    # ============== SAP Learning Hub / OpenSAP ==============
    def scrape_opensap_courses(self):
        """Scrape course descriptions from openSAP"""
        print("\n🎓 Scraping openSAP course info...")
        
        try:
            # openSAP courses page
            response = requests.get("https://open.sap.com/courses", headers=self.headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                for course in soup.find_all('div', class_=re.compile('course', re.I)):
                    try:
                        title_elem = course.find(['h2', 'h3', 'a'])
                        title = title_elem.get_text(strip=True) if title_elem else None
                        
                        desc_elem = course.find('p') or course.find('div', class_=re.compile('desc', re.I))
                        desc = desc_elem.get_text(strip=True) if desc_elem else ''
                        
                        link_elem = course.find('a', href=True)
                        link = link_elem.get('href', '') if link_elem else ''
                        if link and not link.startswith('http'):
                            link = f"https://open.sap.com{link}"
                        
                        if title and len(desc) > 100:
                            self.add_to_dataset({
                                'url': link or 'https://open.sap.com/courses',
                                'title': f"openSAP: {title}",
                                'content': desc[:5000],
                                'source': 'opensap'
                            })
                            print(f"    ✅ Added course: {title[:50]}")
                    except Exception:
                        pass
        except Exception as e:
            print(f"  ⚠️  openSAP error: {e}")

    # ============== GitHub Source ==============
    def scrape_github_sap_repos(self):
        """Scrape from GitHub SAP-related repositories"""
        print("\n🟠 Scraping GitHub SAP repositories...")

        queries = [
            "SAP Basis",
            "SAP ABAP",
            "SAP HANA admin",
            "SAP security",
            "SAP transport",
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
                                        'url': repo['html_url'],
                                        'title': f"GitHub: {repo['name']}",
                                        'content': content[:15000],
                                        'description': repo.get('description', ''),
                                        'source': 'github',
                                        'content_type': 'markdown',
                                        'stars': repo.get('stargazers_count', 0)
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
        
        tags = ["sap", "abap", "hana", "sapui5", "fiori"]
        
        for tag in tags:
            try:
                api_url = f"https://dev.to/api/articles?tag={tag}&per_page=100"
                response = requests.get(api_url, headers=self.headers, timeout=10)
                articles = response.json()
                
                for article in articles:
                    if article.get('readable_publish_date'):
                        # Fetch full article content
                        try:
                            article_resp = requests.get(f"https://dev.to/api/articles/{article['id']}", timeout=10)
                            full_article = article_resp.json()
                            content = full_article.get('body_markdown', '') or full_article.get('body_html', '') or article.get('description', '')
                        except:
                            content = article.get('description', '')
                        
                        if len(content) > 200:
                            self.add_to_dataset({
                                'url': article['url'],
                                'title': article['title'],
                                'content': content[:15000],
                                'author': article['user']['name'],
                                'source': 'devto',
                                'published': article['published_at'],
                                'tags': article.get('tag_list', [])
                            })
                            print(f"    ✅ Added: {article['title'][:50]}")
                    
                    time.sleep(0.3)
            except Exception as e:
                print(f"  ⚠️  Dev.to Error for tag '{tag}': {e}")
            time.sleep(1)

    # ============== Medium ==============
    def scrape_medium_tag(self):
        """Scrape Medium articles tagged sap via RSS (public)"""
        print("\n🟣 Scraping Medium SAP articles...")
        
        tags = ["sap", "sap-hana", "abap", "sap-fiori"]
        
        for tag in tags:
            feed_url = f"https://medium.com/feed/tag/{tag}"
            try:
                resp = requests.get(feed_url, headers=self.headers, timeout=10)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.content, 'xml')
                items = soup.find_all('item')[:30]
                
                for item in items:
                    title = item.title.get_text(strip=True) if item.title else ''
                    link = item.link.get_text(strip=True) if item.link else ''
                    content = ''
                    if item.find('content:encoded'):
                        content = item.find('content:encoded').get_text(strip=True)
                    elif item.description:
                        content = item.description.get_text(strip=True)
                    
                    content = re.sub(r'<[^>]+>', ' ', content)
                    content = re.sub(r'\s+', ' ', content).strip()
                    
                    if len(content) > 300 and link not in self.seen_urls:
                        self.seen_urls.add(link)
                        self.add_to_dataset({
                            'url': link,
                            'title': title,
                            'content': content[:12000],
                            'source': 'medium'
                        })
                        print(f"    ✅ Added: {title[:50]}")
                    time.sleep(0.2)
            except Exception as e:
                print(f"  ⚠️  Medium error for tag '{tag}': {e}")

    # ============== StackOverflow ==============
    def fetch_stackoverflow_answer(self, answer_id):
        """Fetch accepted answer text by ID"""
        if not answer_id:
            return ""
        try:
            api = (
                f"https://api.stackexchange.com/2.3/answers/{answer_id}"
                "?order=desc&sort=activity&site=stackoverflow&filter=withbody"
            )
            resp = requests.get(api, headers=self.headers, timeout=10)
            items = resp.json().get('items', [])
            if items:
                html_body = items[0].get('body', '')
                text = BeautifulSoup(html_body, 'html.parser').get_text(" ", strip=True)
                return re.sub(r'\s+', ' ', text)
        except Exception as e:
            print(f"    ⚠️  StackOverflow answer fetch error: {e}")
        return ""

    def scrape_stackoverflow(self):
        """Scrape top StackOverflow SAP-tagged Q&A (free API, no key)"""
        print("\n🔴 Scraping StackOverflow Q&A...")
        tags = [
            "sap",
            "sap-basis",
            "sapui5",
            "sap-fiori",
            "abap",
            "sap-gateway",
            "sap-cloud-platform",
            "sap-btp",
            "sap-hana",
            "odata",
            "sap-netweaver",
        ]
        for tag in tags:
            try:
                api_url = (
                    "https://api.stackexchange.com/2.3/search/advanced"
                    f"?order=desc&sort=votes&tagged={quote(tag)}&site=stackoverflow"
                    "&pagesize=30&filter=withbody"
                )
                print(f"  🔍 Tag: {tag}")
                resp = requests.get(api_url, headers=self.headers, timeout=10)
                resp.raise_for_status()
                questions = resp.json().get('items', [])
                for q in questions:
                    link = q.get('link', '')
                    if not link or link in self.seen_urls:
                        continue
                    self.seen_urls.add(link)
                    title = q.get('title', 'StackOverflow Question')
                    question_body = BeautifulSoup(q.get('body', ''), 'html.parser').get_text(" ", strip=True)
                    question_body = re.sub(r'\s+', ' ', question_body)
                    accepted_id = q.get('accepted_answer_id')
                    accepted_body = self.fetch_stackoverflow_answer(accepted_id) if accepted_id else ''
                    content_parts = [f"Question: {title}", question_body]
                    if accepted_body:
                        content_parts.append("Accepted Answer:")
                        content_parts.append(accepted_body)
                    content = "\n\n".join([p for p in content_parts if p])
                    if len(content) > 300:
                        self.add_to_dataset({
                            'url': link,
                            'title': title,
                            'content': content[:18000],
                            'source': 'stackoverflow',
                            'tags': q.get('tags', []),
                            'score': q.get('score', 0),
                            'is_answered': q.get('is_answered', False),
                        })
                        print(f"    ✅ Added Q&A: {title[:60]}")
                    time.sleep(0.3)
                time.sleep(1.2)
            except Exception as e:
                print(f"  ⚠️  StackOverflow error for tag '{tag}': {e}")

    # ============== SAP Developers Tutorials ==============
    def scrape_sap_developers_tutorials(self):
        """Scrape tutorial listings from developers.sap.com/tutorials"""
        print("\n🟡 Scraping SAP Developers tutorials...")
        base = "https://developers.sap.com"
        listing_urls = [
            f"{base}/tutorial-navigator.html",
            f"{base}/tutorial-navigator.html?tag=software-product-function:technology-platform/sap-btp",
            f"{base}/tutorial-navigator.html?tag=software-product-function:analytics/sap-analytics-cloud",
            f"{base}/tutorial-navigator.html?tag=software-product-function:app-development/sapui5",
            f"{base}/tutorial-navigator.html?tag=software-product-function:database/sap-hana",
            f"{base}/tutorial-navigator.html?tag=topic:security",
            f"{base}/tutorial-navigator.html?tag=topic:abap",
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

    # ============== Guru99 SAP Tutorials ==============
    def scrape_guru99_sap(self):
        """Scrape Guru99 SAP tutorials - popular learning resource"""
        print("\n📖 Scraping Guru99 SAP tutorials...")
        
        base_url = "https://www.guru99.com"
        sap_pages = [
            "/sap-basis-tutorial.html",
            "/sap-hana-tutorial.html",
            "/sap-mm-training.html",
            "/sap-sd-tutorial.html",
            "/sap-fico-training.html",
            "/sap-abap-tutorial.html",
            "/sap-security-tutorial.html",
        ]
        
        for page in sap_pages:
            try:
                url = f"{base_url}{page}"
                resp = requests.get(url, headers=self.headers, timeout=12)
                if resp.status_code != 200:
                    continue
                
                soup = BeautifulSoup(resp.content, 'html.parser')
                
                # Get tutorial links from the page
                for link in soup.find_all('a', href=re.compile(r'/sap-')):
                    href = link.get('href', '')
                    full_url = urljoin(base_url, href)
                    if full_url not in self.seen_urls and 'guru99.com' in full_url:
                        self.seen_urls.add(full_url)
                        self.scrape_guru99_page(full_url)
                
                time.sleep(1)
            except Exception as e:
                print(f"  ⚠️  Guru99 error: {e}")
    
    def scrape_guru99_page(self, url):
        """Scrape individual Guru99 page"""
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code != 200:
                return False
            
            soup = BeautifulSoup(resp.content, 'html.parser')
            
            title = soup.find('h1')
            title = title.get_text(strip=True) if title else "Guru99 SAP Tutorial"
            
            # Get article content
            article = soup.find('article') or soup.find('div', class_=re.compile('content', re.I))
            if article:
                content = article.get_text(separator=' ', strip=True)
            else:
                content = soup.get_text(separator=' ', strip=True)
            
            content = re.sub(r'\s+', ' ', content).strip()
            
            if len(content) > 500:
                self.add_to_dataset({
                    'url': url,
                    'title': f"Guru99: {title}",
                    'content': content[:15000],
                    'source': 'guru99'
                })
                print(f"    ✅ Added: {title[:50]}")
                return True
        except Exception:
            pass
        return False

    # ============== TutorialsPoint SAP ==============
    def scrape_tutorialspoint_sap(self):
        """Scrape TutorialsPoint SAP tutorials"""
        print("\n📗 Scraping TutorialsPoint SAP content...")
        
        base_url = "https://www.tutorialspoint.com"
        sap_sections = [
            "/sap_basis/index.htm",
            "/sap_hana/index.htm",
            "/sap_abap/index.htm",
            "/sap_security/index.htm",
            "/sap_mm/index.htm",
            "/sap_sd/index.htm",
            "/sap_fico/index.htm",
        ]
        
        for section in sap_sections:
            try:
                url = f"{base_url}{section}"
                resp = requests.get(url, headers=self.headers, timeout=12)
                if resp.status_code != 200:
                    continue
                
                soup = BeautifulSoup(resp.content, 'html.parser')
                
                # Find tutorial links in sidebar/menu
                for link in soup.find_all('a', href=re.compile(r'\.htm$')):
                    href = link.get('href', '')
                    if href and not href.startswith('http'):
                        full_url = urljoin(url, href)
                    else:
                        full_url = href
                    
                    if full_url not in self.seen_urls and 'tutorialspoint.com/sap' in full_url:
                        self.seen_urls.add(full_url)
                        self.scrape_tutorialspoint_page(full_url)
                
                time.sleep(1)
            except Exception as e:
                print(f"  ⚠️  TutorialsPoint error: {e}")
    
    def scrape_tutorialspoint_page(self, url):
        """Scrape individual TutorialsPoint page"""
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code != 200:
                return False
            
            soup = BeautifulSoup(resp.content, 'html.parser')
            
            title = soup.find('h1')
            title = title.get_text(strip=True) if title else "TutorialsPoint SAP"
            
            content_div = soup.find('div', class_='tutorial-content') or soup.find('div', id='mainContent')
            if content_div:
                content = content_div.get_text(separator=' ', strip=True)
            else:
                content = soup.get_text(separator=' ', strip=True)
            
            content = re.sub(r'\s+', ' ', content).strip()
            
            if len(content) > 400:
                self.add_to_dataset({
                    'url': url,
                    'title': f"TutorialsPoint: {title}",
                    'content': content[:12000],
                    'source': 'tutorialspoint'
                })
                print(f"    ✅ Added: {title[:50]}")
                return True
        except Exception:
            pass
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
        content = article_data.get('content', '')
        content_hash = hashlib.md5(content.encode()).hexdigest()[:12]
        
        # Skip if we've seen this content before
        if content_hash in self.seen_content_hashes:
            return False
        
        self.seen_content_hashes.add(content_hash)
        article_data['id'] = content_hash
        article_data['timestamp'] = datetime.now().isoformat()
        
        self.dataset.append(article_data)
        return True
    
    def build(self):
        """Build comprehensive dataset"""
        print("🚀 Starting comprehensive SAP dataset build v2.0...")
        print("=" * 60)
        self.setup_directories()
        
        # Core sources
        self.scrape_sap_community()
        self.scrape_sap_community_rss()
        self.scrape_sap_tcode_blogs()  # NEW: Transaction code focused
        
        # Official documentation
        self.scrape_sap_help_portal()  # NEW: help.sap.com
        self.scrape_sap_developers_tutorials()
        self.scrape_opensap_courses()  # NEW: openSAP
        
        # Wiki & Community
        self.scrape_sap_wiki()  # NEW: SAP Wiki
        self.scrape_stackoverflow()
        
        # Learning platforms
        self.scrape_guru99_sap()  # NEW: Guru99
        self.scrape_tutorialspoint_sap()  # NEW: TutorialsPoint
        
        # Developer resources
        self.scrape_github_sap_repos()
        self.scrape_devto_articles()
        self.scrape_medium_tag()
        
        # Save dataset
        output_file = "data/sap_dataset.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.dataset, f, indent=2, ensure_ascii=False)
        
        print("\n" + "=" * 60)
        print(f"✅ Dataset build completed!")
        print(f"   📊 Total documents: {len(self.dataset)}")
        print(f"   💾 Saved to: {output_file}")
        
        # Print source breakdown
        sources = {}
        for doc in self.dataset:
            src = doc.get('source', 'unknown')
            sources[src] = sources.get(src, 0) + 1
        
        print("\n   📈 Source breakdown:")
        for src, count in sorted(sources.items(), key=lambda x: -x[1]):
            print(f"      - {src}: {count}")
        
        return self.dataset

if __name__ == "__main__":
    builder = SAPDatasetBuilder()
    dataset = builder.build()
