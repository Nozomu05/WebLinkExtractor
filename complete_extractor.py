import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re

def extract_complete_webpage_content(url: str) -> str:
    """
    Extract ALL visible content from a webpage preserving structure
    """
    try:
        # Validate URL
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError("Invalid URL format")
        
        # Enhanced headers to bypass basic bot detection
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"'
        }
        
        # Create session for better handling
        session = requests.Session()
        session.headers.update(headers)
        
        # Try multiple user agents if first fails
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        
        response = None
        last_error = None
        
        for user_agent in user_agents:
            try:
                session.headers.update({'User-Agent': user_agent})
                response = session.get(url, timeout=20, allow_redirects=True)
                response.raise_for_status()
                
                # Check if we got meaningful content
                if len(response.text) > 500:
                    break
                    
            except Exception as e:
                last_error = e
                continue
        
        if not response or response.status_code != 200:
            if last_error:
                raise last_error
            else:
                raise Exception("Failed to fetch content with any user agent")
        
        # Parse HTML with better parser
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check if page seems to have meaningful content
        body_text = soup.get_text(strip=True) if soup.body else soup.get_text(strip=True)
        if len(body_text) < 100:
            raise Exception("Page appears to have minimal content - may require JavaScript or be behind protection")
        
        # Remove unwanted elements but preserve structure
        for element in soup(['script', 'style', 'noscript', 'meta', 'link', 'iframe']):
            element.decompose()
        
        # Remove common advertisement and navigation elements
        for element in soup.find_all(['div', 'section'], class_=re.compile(r'(ad|advertisement|sidebar|nav|menu|footer|header)', re.I)):
            element.decompose()
        
        for element in soup.find_all(['div', 'section'], id=re.compile(r'(ad|advertisement|sidebar|nav|menu|footer|header)', re.I)):
            element.decompose()
        
        # Extract content with structure preservation
        content_parts = []
        
        # Get title
        title = soup.find('title')
        if title and title.get_text(strip=True):
            content_parts.append(f"# {title.get_text(strip=True)}\n")
        
        # Process all content elements
        body = soup.find('body') or soup
        
        def extract_element_content(element, level=0):
            """Extract content with proper structure and formatting"""
            results = []
            
            if not element.name:
                return results
            
            # Handle headings with clear formatting
            if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                text = element.get_text(strip=True)
                if text and len(text) > 2:
                    heading_level = int(element.name[1])
                    prefix = '#' * heading_level
                    results.append(f"\n{prefix} {text}\n")
            
            # Handle paragraphs as distinct blocks
            elif element.name == 'p':
                text = element.get_text(strip=True)
                if text and len(text) > 10:
                    results.append(f"{text}\n\n")
            
            # Handle list containers
            elif element.name in ['ul', 'ol']:
                list_items = []
                for li in element.find_all('li', recursive=False):
                    li_text = li.get_text(strip=True)
                    if li_text and len(li_text) > 3:
                        list_items.append(f"• {li_text}")
                
                if list_items:
                    results.extend(list_items)
                    results.append("\n")
            
            # Handle table structure
            elif element.name == 'table':
                table_content = []
                for row in element.find_all('tr'):
                    cells = []
                    for cell in row.find_all(['td', 'th']):
                        cell_text = cell.get_text(strip=True)
                        if cell_text:
                            cells.append(cell_text)
                    if cells:
                        table_content.append(" | ".join(cells))
                
                if table_content:
                    results.extend(table_content)
                    results.append("\n")
            
            # Handle block elements that should be separated
            elif element.name in ['div', 'section', 'article', 'main', 'aside', 'header', 'footer', 'nav']:
                # Check if this element has meaningful direct text
                direct_text = []
                for child in element.children:
                    if isinstance(child, str):
                        text = child.strip()
                        if text and len(text) > 10:
                            direct_text.append(text)
                
                # If has direct text, treat as a block
                if direct_text:
                    combined_text = ' '.join(direct_text)
                    if len(combined_text) > 15:
                        results.append(f"{combined_text}\n\n")
                else:
                    # Process children recursively
                    for child in element.children:
                        if hasattr(child, 'name'):
                            child_results = extract_element_content(child, level + 1)
                            results.extend(child_results)
            
            # Handle other text elements
            elif element.name in ['span', 'strong', 'em', 'b', 'i', 'a', 'code']:
                text = element.get_text(strip=True)
                if text and len(text) > 5:
                    # Check if this is likely standalone content
                    parent_has_text = False
                    if element.parent:
                        parent_text = element.parent.get_text(strip=True)
                        if len(parent_text) > len(text) * 2:
                            parent_has_text = True
                    
                    if not parent_has_text:
                        results.append(f"{text}\n")
            
            return results
        
        # Extract all content
        all_content = extract_element_content(body)
        
        # Join and clean up
        final_content = '\n'.join(all_content)
        
        # Clean up excessive whitespace while preserving structure
        final_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', final_content)
        final_content = re.sub(r'[ \t]+', ' ', final_content)
        
        # Final validation
        if len(final_content.strip()) < 100:
            raise Exception("Extracted content is too short - page may require JavaScript or special handling")
        
        return final_content.strip()
        
    except requests.exceptions.Timeout:
        raise Exception("Request timed out. The website may be slow to respond.")
    except requests.exceptions.ConnectionError:
        raise Exception("Unable to connect to the website. Please check the URL and your internet connection.")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            raise Exception("Page not found (404). Please check if the URL is correct.")
        elif e.response.status_code == 403:
            raise Exception("Access forbidden (403). The website may be blocking automated requests.")
        elif e.response.status_code == 500:
            raise Exception("Server error (500). The website is experiencing technical difficulties.")
        else:
            raise Exception(f"HTTP error {e.response.status_code}: {e.response.reason}")
    except Exception as e:
        raise Exception(f"Error extracting content: {str(e)}")