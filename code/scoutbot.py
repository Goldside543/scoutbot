import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin, urlparse
import urllib.robotparser

def can_fetch(url, user_agent='*'):
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(base_url)
    rp.read()
    return rp.can_fetch(user_agent, url)

def crawl(url, max_pages=10, log_file='crawled_urls.txt', user_agent='*'):
    pages_crawled = 0
    urls_to_crawl = [url]
    crawled_urls = set()
    
    with open(log_file, 'w') as log:
        while urls_to_crawl and pages_crawled < max_pages:
            current_url = urls_to_crawl.pop(0)
            
            # Skip URLs that have already been crawled
            if current_url in crawled_urls:
                continue
            
            # Check if the URL can be crawled according to robots.txt
            if not can_fetch(current_url, user_agent):
                print(f"Disallowed by robots.txt: {current_url}")
                continue
            
            try:
                response = requests.get(current_url)
                if response.status_code != 200:
                    print(f"Failed to retrieve {current_url}")
                    continue
                
                # Parse the HTML content
                soup = BeautifulSoup(response.content, 'html.parser')
                crawled_urls.add(current_url)
                pages_crawled += 1
                
                # Log the current URL
                log.write(f"{current_url}\n")
                print(f"Crawled ({pages_crawled}): {current_url}")
                
                # Find all links on the current page
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    # Construct a full URL
                    full_url = urljoin(current_url, href)
                    
                    # Skip URLs that are already crawled or in the queue
                    if full_url not in crawled_urls and full_url not in urls_to_crawl:
                        urls_to_crawl.append(full_url)
                
                # Optional: Add a delay to avoid overloading the server
                time.sleep(1)
            
            except requests.RequestException as e:
                print(f"Error crawling {current_url}: {e}")

# Start crawling from a given URL
start_url = 'http://example.com'
crawl(start_url)
