import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import trafilatura

def extract_all_webpage_data(url: str) -> str:
    """
    Extract absolutely everything from a webpage including all text, metadata, and content
    """
    try:
        # Validate URL
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError("Invalid URL format")
        
        # Enhanced headers
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
        
        # Create session
        session = requests.Session()
        session.headers.update(headers)
        
        # Try multiple user agents
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        
        response = None
        for user_agent in user_agents:
            try:
                session.headers.update({'User-Agent': user_agent})
                response = session.get(url, timeout=20, allow_redirects=True)
                response.raise_for_status()
                if len(response.text) > 100:
                    break
            except Exception:
                continue
        
        if not response or response.status_code != 200:
            raise Exception("Failed to fetch content")
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract all content sections
        all_content = []
        
        # 1. Extract page title and metadata
        title = soup.find('title')
        if title:
            all_content.append(f"# {title.get_text(strip=True)}\n")
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
        if meta_desc and meta_desc.get('content'):
            all_content.append(f"**Description:** {meta_desc.get('content')}\n")
        
        # 2. Remove scripts, styles, images, videos, and other media content
        for element in soup(['script', 'style', 'img', 'video', 'audio', 'iframe', 'embed', 'object', 'canvas', 'svg']):
            element.decompose()
        
        # Remove elements with image/media related classes or attributes
        for element in soup.find_all(attrs={'class': re.compile(r'image|img|photo|video|media|banner|ad', re.I)}):
            element.decompose()
        
        # Remove figure elements that typically contain images
        for element in soup(['figure', 'picture']):
            element.decompose()
        
        # 3. Extract content from all possible containers
        content_containers = [
            soup.find('main'),
            soup.find('article'),
            soup.find('div', class_=re.compile(r'content|main|article|post|body', re.I)),
            soup.find('div', id=re.compile(r'content|main|article|post|body', re.I)),
            soup.body,
            soup
        ]
        
        extracted_text = set()  # To avoid duplicates
        
        for container in content_containers:
            if not container:
                continue
                
            # Extract all text elements recursively
            for element in container.find_all(text=True):
                text = element.strip()
                if text and len(text) > 2:
                    # Clean up the text
                    text = re.sub(r'\s+', ' ', text)
                    if text not in extracted_text and len(text) > 3:
                        extracted_text.add(text)
        
        # 4. Also try trafilatura for structured extraction
        trafilatura_content = trafilatura.extract(
            response.text,
            include_comments=False,
            include_tables=True,
            include_formatting=True,
            favor_precision=False,
            favor_recall=True,
            include_links=False,
            with_metadata=False,
            no_fallback=False,
            deduplicate=False
        )
        
        if trafilatura_content:
            # Split trafilatura content and add to our set
            for line in trafilatura_content.split('\n'):
                line = line.strip()
                if line and len(line) > 3:
                    extracted_text.add(line)
        
        # 5. Extract content in exact DOM order preserving webpage structure
        def extract_in_dom_order(element, level=0):
            """Extract content in exact DOM traversal order maintaining webpage structure"""
            content_parts = []
            
            if not element:
                return content_parts
            
            # Process all child nodes in exact DOM order
            for child in element.children if hasattr(element, 'children') else []:
                if hasattr(child, 'name') and child.name:
                    element_name = child.name.lower()
                    
                    # Skip unwanted elements completely
                    if element_name in ['script', 'style', 'nav', 'aside'] or \
                       (child.get('class') and any(cls in str(child.get('class')).lower() 
                                                  for cls in ['nav', 'navigation', 'sidebar', 'menu', 'ad', 'advertisement', 'social'])):
                        continue
                    
                    # Handle different elements in exact order they appear
                    if element_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        text = child.get_text(strip=True)
                        if text and len(text) > 1:
                            heading_level = int(element_name[1])
                            content_parts.append(f"{'#' * heading_level} {text}")
                    
                    elif element_name == 'p':
                        text = child.get_text(strip=True)
                        if text and len(text) > 3:
                            content_parts.append(text)
                    
                    elif element_name in ['ul', 'ol']:
                        # Process list items in order
                        for li in child.find_all('li', recursive=False):
                            li_text = li.get_text(strip=True)
                            if li_text and len(li_text) > 1:
                                content_parts.append(f"• {li_text}")
                    
                    elif element_name == 'blockquote':
                        text = child.get_text(strip=True)
                        if text and len(text) > 5:
                            content_parts.append(f"> {text}")
                    
                    elif element_name == 'pre':
                        text = child.get_text(strip=True)
                        if text and len(text) > 3:
                            content_parts.append(f"```\n{text}\n```")
                    
                    elif element_name == 'table':
                        # Process table rows in order
                        for row in child.find_all('tr'):
                            cells = []
                            for cell in row.find_all(['td', 'th']):
                                cell_text = cell.get_text(strip=True)
                                if cell_text:
                                    cells.append(cell_text)
                            if cells:
                                content_parts.append(" | ".join(cells))
                    
                    elif element_name == 'details':
                        # Handle FAQ/accordion sections properly
                        summary = child.find('summary')
                        if summary:
                            summary_text = summary.get_text(strip=True)
                            if summary_text:
                                content_parts.append(f"**{summary_text}**")
                        
                        # Get the details content
                        details_content = extract_in_dom_order(child, level + 1)
                        content_parts.extend(details_content)
                    
                    elif element_name in ['div', 'section', 'article', 'main', 'header', 'footer']:
                        # For containers, check if they have meaningful direct text
                        direct_text_nodes = []
                        has_block_children = False
                        
                        for node in child.children:
                            if isinstance(node, str):
                                text = node.strip()
                                if text and len(text) > 5:
                                    direct_text_nodes.append(text)
                            elif hasattr(node, 'name') and node.name in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'div', 'section']:
                                has_block_children = True
                        
                        if direct_text_nodes and not has_block_children:
                            # Container with direct text content
                            combined_text = ' '.join(direct_text_nodes)
                            if len(combined_text) > 10:
                                content_parts.append(combined_text)
                        else:
                            # Recursively process children in DOM order
                            child_content = extract_in_dom_order(child, level + 1)
                            content_parts.extend(child_content)
                    
                    elif element_name in ['span', 'strong', 'em', 'b', 'i', 'a', 'code', 'small']:
                        # Only include if it's standalone (not inside paragraph)
                        parent = child.parent
                        if parent and parent.name not in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'td', 'th']:
                            text = child.get_text(strip=True)
                            if text and len(text) > 3:
                                content_parts.append(text)
                
                elif isinstance(child, str):
                    # Direct text node
                    text = child.strip()
                    if text and len(text) > 8:
                        content_parts.append(text)
            
            return content_parts
        
        # Extract content in exact DOM order from main body
        body = soup.body if soup.body else soup
        dom_ordered_content = extract_in_dom_order(body)
        
        # Combine title/metadata with DOM-ordered content
        final_content = []
        final_content.extend(all_content)  # Title and metadata first
        final_content.extend(dom_ordered_content)  # Then content in exact webpage order
        
        # Only add trafilatura content if we got very little from DOM extraction
        if len(dom_ordered_content) < 5 and trafilatura_content:
            trafilatura_lines = trafilatura_content.split('\n')
            for line in trafilatura_lines:
                line = line.strip()
                if line and len(line) > 10:
                    if not any(line in existing for existing in final_content):
                        final_content.append(line)
        
        # Join and clean up
        result = '\n\n'.join(filter(None, final_content))
        
        # Clean up excessive whitespace
        result = re.sub(r'\n\s*\n\s*\n+', '\n\n', result)
        result = re.sub(r'[ \t]+', ' ', result)
        
        if len(result.strip()) < 30:
            # Last resort - get absolutely everything
            all_text = soup.get_text(separator='\n', strip=True)
            return all_text if all_text else "No extractable content found"
        
        return result.strip()
        
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