import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import time
from typing import Set, List, Dict, Any
from complete_data_extractor import extract_all_webpage_data
import re

class DepthScraper:
    def __init__(self, max_depth: int = 2, delay: float = 1.0, max_pages: int = 10):
        """
        Initialize depth scraper with configuration
        
        Args:
            max_depth: Maximum depth to crawl (0 = current page only)
            delay: Delay between requests in seconds
            max_pages: Maximum number of pages to scrape
        """
        self.max_depth = max_depth
        self.delay = delay
        self.max_pages = max_pages
        self.visited_urls: Set[str] = set()
        self.scraped_content: List[Dict[str, Any]] = []
        
    def get_links_from_page(self, url: str, base_domain: str) -> List[str]:
        """Extract links from a webpage that belong to the same domain"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            links = []
            
            for link in soup.find_all('a', href=True):
                try:
                    href = link['href'] if link.has_attr('href') else ''
                except (KeyError, AttributeError):
                    href = ''
                
                # Convert relative URLs to absolute
                if href:
                    full_url = urljoin(url, str(href))
                    parsed_url = urlparse(full_url)
                else:
                    continue
                
                # Only include links from the same domain
                if parsed_url.netloc == base_domain:
                    # Clean URL (remove fragments)
                    clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
                    if parsed_url.query:
                        clean_url += f"?{parsed_url.query}"
                    
                    if clean_url not in self.visited_urls and clean_url != url:
                        links.append(clean_url)
            
            return links[:20]  # Limit to first 20 links per page
            
        except Exception as e:
            print(f"Error extracting links from {url}: {e}")
            return []
    
    def scrape_with_depth(self, start_url: str, include_images: bool = False, 
                         include_videos: bool = False) -> Dict[str, Any]:
        """
        Scrape starting from a URL with specified depth
        
        Args:
            start_url: The starting URL to scrape
            include_images: Whether to extract images
            include_videos: Whether to extract videos
            
        Returns:
            Dictionary containing all scraped content organized by depth
        """
        base_domain = urlparse(start_url).netloc
        urls_to_process: List[tuple[str, int]] = [(start_url, 0)]  # (url, depth)
        
        results = {
            'start_url': start_url,
            'max_depth': self.max_depth,
            'pages_scraped': 0,
            'total_pages_found': 0,
            'content_by_depth': {},
            'all_content': [],
            'summary': {
                'total_characters': 0,
                'total_words': 0,
                'total_images': 0,
                'total_videos': 0,
                'pages_by_depth': {}
            }
        }
        
        while urls_to_process and len(self.scraped_content) < self.max_pages:
            current_url, current_depth = urls_to_process.pop(0)
            
            if current_url in self.visited_urls or current_depth > self.max_depth:
                continue
                
            print(f"Scraping depth {current_depth}: {current_url}")
            self.visited_urls.add(current_url)
            
            try:
                # Extract content from current page
                content = extract_all_webpage_data(
                    current_url, 
                    include_images=include_images, 
                    include_videos=include_videos
                )
                
                if content and len(content.strip()) > 100:
                    page_data = {
                        'url': current_url,
                        'depth': current_depth,
                        'content': content,
                        'word_count': len(content.split()),
                        'character_count': len(content),
                        'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    # Count images and videos
                    image_count = len(re.findall(r'!\[.*?\]\([^)]+\)', content))
                    video_count = len(re.findall(r'\*\*\[.*?VIDEO.*?\]\*\*', content, re.IGNORECASE))
                    
                    page_data['image_count'] = image_count
                    page_data['video_count'] = video_count
                    
                    self.scraped_content.append(page_data)
                    
                    # Organize by depth
                    if current_depth not in results['content_by_depth']:
                        results['content_by_depth'][current_depth] = []
                    results['content_by_depth'][current_depth].append(page_data)
                    
                    # Update summary
                    results['summary']['total_characters'] += page_data['character_count']
                    results['summary']['total_words'] += page_data['word_count']
                    results['summary']['total_images'] += image_count
                    results['summary']['total_videos'] += video_count
                    
                    if current_depth not in results['summary']['pages_by_depth']:
                        results['summary']['pages_by_depth'][current_depth] = 0
                    results['summary']['pages_by_depth'][current_depth] += 1
                    
                    results['pages_scraped'] += 1
                    
                    # Get links for next depth level
                    if current_depth < self.max_depth:
                        links = self.get_links_from_page(current_url, base_domain)
                        for link in links:
                            if link not in self.visited_urls:
                                new_tuple: tuple[str, int] = (link, current_depth + 1)
                                urls_to_process.append(new_tuple)
                                results['total_pages_found'] += 1
                
                # Delay between requests
                if self.delay > 0:
                    time.sleep(self.delay)
                    
            except Exception as e:
                print(f"Error scraping {current_url}: {e}")
                continue
        
        results['all_content'] = self.scraped_content
        return results
    
    def format_depth_content(self, results: Dict[str, Any]) -> str:
        """Format the depth scraping results into readable text"""
        formatted_content = []
        
        # Add header with summary
        formatted_content.append(f"# Depth Scraping Results")
        formatted_content.append(f"**Start URL:** {results['start_url']}")
        formatted_content.append(f"**Max Depth:** {results['max_depth']}")
        formatted_content.append(f"**Pages Scraped:** {results['pages_scraped']}")
        formatted_content.append(f"**Total Pages Found:** {results['total_pages_found']}")
        formatted_content.append("")
        
        # Add summary statistics
        summary = results['summary']
        formatted_content.append("## Summary Statistics")
        formatted_content.append(f"- **Total Characters:** {summary['total_characters']:,}")
        formatted_content.append(f"- **Total Words:** {summary['total_words']:,}")
        formatted_content.append(f"- **Total Images:** {summary['total_images']}")
        formatted_content.append(f"- **Total Videos:** {summary['total_videos']}")
        formatted_content.append("")
        
        # Add pages by depth
        formatted_content.append("### Pages by Depth")
        for depth, count in summary['pages_by_depth'].items():
            formatted_content.append(f"- **Depth {depth}:** {count} pages")
        formatted_content.append("")
        
        # Add content organized by depth
        for depth in sorted(results['content_by_depth'].keys()):
            formatted_content.append(f"## Depth {depth} Content")
            formatted_content.append("")
            
            pages = results['content_by_depth'][depth]
            for i, page in enumerate(pages, 1):
                formatted_content.append(f"### Page {i}: {page['url']}")
                formatted_content.append(f"**Scraped at:** {page['scraped_at']}")
                formatted_content.append(f"**Word Count:** {page['word_count']:,}")
                formatted_content.append(f"**Images:** {page['image_count']} | **Videos:** {page['video_count']}")
                formatted_content.append("")
                formatted_content.append("**Content:**")
                formatted_content.append(page['content'])
                formatted_content.append("")
                formatted_content.append("---")
                formatted_content.append("")
        
        return "\n".join(formatted_content)


def scrape_with_depth(url: str, depth: int = 1, include_images: bool = False, 
                     include_videos: bool = False, delay: float = 1.0, 
                     max_pages: int = 10) -> str:
    """
    Convenience function to scrape with depth
    
    Args:
        url: Starting URL
        depth: Maximum depth to scrape (0 = current page only)
        include_images: Whether to extract images
        include_videos: Whether to extract videos
        delay: Delay between requests in seconds
        max_pages: Maximum number of pages to scrape
    
    Returns:
        Formatted content string
    """
    scraper = DepthScraper(max_depth=depth, delay=delay, max_pages=max_pages)
    results = scraper.scrape_with_depth(url, include_images, include_videos)
    return scraper.format_depth_content(results)