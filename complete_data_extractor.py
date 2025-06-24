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
        
        # 2. Remove only scripts and styles but keep everything else
        for element in soup(['script', 'style']):
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
        
        # 5. Extract specific elements with structure
        structured_content = []
        
        # Headers
        for i in range(1, 7):
            headers = soup.find_all(f'h{i}')
            for header in headers:
                header_text = header.get_text(strip=True)
                if header_text and len(header_text) > 2:
                    structured_content.append(f"{'#' * i} {header_text}")
        
        # Paragraphs
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            p_text = p.get_text(strip=True)
            if p_text and len(p_text) > 10:
                structured_content.append(p_text)
        
        # Lists
        lists = soup.find_all(['ul', 'ol'])
        for lst in lists:
            items = lst.find_all('li')
            for item in items:
                item_text = item.get_text(strip=True)
                if item_text and len(item_text) > 3:
                    structured_content.append(f"• {item_text}")
        
        # Tables
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
                if any(cells):
                    structured_content.append(" | ".join(filter(None, cells)))
        
        # Divs and other containers
        divs = soup.find_all(['div', 'section', 'article', 'aside'])
        for div in divs:
            # Get direct text content
            div_text = div.get_text(strip=True)
            if div_text and len(div_text) > 15:
                # Check if this div's text is not already captured by children
                children_text = ""
                for child in div.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']):
                    children_text += child.get_text(strip=True)
                
                # If the div has significantly more text than its children, include it
                if len(div_text) > len(children_text) * 1.2:
                    structured_content.append(div_text)
        
        # Combine all extracted content
        final_content = []
        
        # Add structured content first
        final_content.extend(all_content)
        final_content.extend(structured_content)
        
        # Add any remaining text that wasn't captured
        for text in sorted(extracted_text, key=len, reverse=True):
            if not any(text in existing for existing in final_content):
                final_content.append(text)
        
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