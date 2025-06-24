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
        
        # Request with proper headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove only truly unwanted elements
        for element in soup(['script', 'style', 'noscript', 'meta', 'link']):
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