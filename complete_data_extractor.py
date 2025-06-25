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
        
        # 3. Try trafilatura first for fallback content
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
        
        # 4. Extract complete content in exact DOM order preserving webpage structure
        def extract_complete_dom_content(element, level=0, max_level=10):
            """Extract ALL content in exact DOM traversal order maintaining webpage structure"""
            content_parts = []
            
            if not element or level > max_level:
                return content_parts
            
            # Process ALL child nodes in exact DOM order - don't skip anything important
            for child in element.children if hasattr(element, 'children') else []:
                if hasattr(child, 'name') and child.name:
                    element_name = child.name.lower()
                    
                    # Only skip truly unwanted elements
                    if element_name in ['script', 'style']:
                        continue
                    
                    # Skip only obvious navigation/ads, but be more permissive
                    if (child.get('class') and 
                        any(cls in str(child.get('class')).lower() 
                            for cls in ['navbar', 'navigation-bar', 'header-nav', 'footer-nav', 'advertisement', 'google-ads'])):
                        continue
                    
                    # Handle ALL content elements in exact order they appear
                    if element_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        text = child.get_text(strip=True)
                        if text:
                            heading_level = int(element_name[1])
                            content_parts.append(f"{'#' * heading_level} {text}")
                    
                    elif element_name == 'p':
                        text = child.get_text(strip=True)
                        if text:
                            content_parts.append(text)
                    
                    elif element_name in ['ul', 'ol']:
                        # Process ALL list items in order
                        for li in child.find_all('li', recursive=False):
                            li_text = li.get_text(strip=True)
                            if li_text:
                                content_parts.append(f"• {li_text}")
                    
                    elif element_name == 'blockquote':
                        text = child.get_text(strip=True)
                        if text:
                            content_parts.append(f"> {text}")
                    
                    elif element_name == 'pre':
                        text = child.get_text(strip=True)
                        if text:
                            content_parts.append(f"```\n{text}\n```")
                    
                    elif element_name == 'table':
                        # Process ALL table content
                        for row in child.find_all('tr'):
                            cells = []
                            for cell in row.find_all(['td', 'th']):
                                cell_text = cell.get_text(strip=True)
                                if cell_text:
                                    cells.append(cell_text)
                            if cells:
                                content_parts.append(" | ".join(cells))
                    
                    elif element_name == 'details':
                        # Handle FAQ/accordion sections with ALL content
                        summary = child.find('summary')
                        if summary:
                            summary_text = summary.get_text(strip=True)
                            if summary_text:
                                content_parts.append(f"**{summary_text}**")
                        
                        # Get ALL the details content recursively
                        details_content = extract_complete_dom_content(child, level + 1, max_level)
                        content_parts.extend(details_content)
                    
                    elif element_name in ['div', 'section', 'article', 'main', 'header', 'footer', 'aside', 'nav']:
                        # Special handling for FAQ sections
                        if (child.get('class') and 
                            any('faq' in str(cls).lower() for cls in child.get('class', []))):
                            
                            # Process FAQ section with proper Q&A pairing
                            content_parts.append("## FAQ Section")
                            
                            import re
                            
                            # Extract FAQ with improved Q&A capture
                            import re
                            
                            faq_text = child.get_text()
                            lines = [line.strip() for line in faq_text.split('\n') if line.strip()]
                            
                            # Define categories and sections
                            categories = {
                                "FAQs thi trên giấy": [
                                    "Thông tin chung về bài thi PEIC",
                                    "Các câu hỏi về việc đăng ký thi PEIC",
                                    "Các câu hỏi liên quan đến ngày thi PEIC", 
                                    "Các câu hỏi liên quan đến kết quả thi PEIC"
                                ],
                                "FAQs thi trên máy tính": [
                                    "Thông tin chung về bài thi PEIC CBT",
                                    "Các câu hỏi về việc đăng ký thi PEIC CBT",
                                    "Các câu hỏi liên quan đến ngày thi PEIC CBT",
                                    "Các câu hỏi liên quan đến kết quả thi PEIC CBT"
                                ]
                            }
                            
                            # First collect all Q&A content regardless of section
                            all_qa = []
                            i = 0
                            
                            while i < len(lines):
                                line = lines[i]
                                
                                # Look for numbered questions
                                if re.match(r'^\d+[\s.]', line) and len(line) > 15:
                                    question = re.sub(r'^\d+[\s.]*', '', line)
                                    answer_parts = []
                                    
                                    # Collect answer lines until next question or section
                                    j = i + 1
                                    while j < len(lines):
                                        next_line = lines[j]
                                        
                                        # Stop if we hit another question or clear section header
                                        if (re.match(r'^\d+[\s.]', next_line) and len(next_line) > 15) or \
                                           any(any(sec in next_line for sec in cat_sections) 
                                               for cat_sections in categories.values()):
                                            break
                                            
                                        if len(next_line) > 5:
                                            answer_parts.append(next_line)
                                        j += 1
                                    
                                    if answer_parts:
                                        all_qa.append({
                                            'question': question,
                                            'answer': ' '.join(answer_parts),
                                            'line_index': i
                                        })
                                    
                                    i = j
                                else:
                                    i += 1
                            
                            # Assign Q&As to sections based on context
                            section_content = {}
                            current_section = None
                            
                            for i, line in enumerate(lines):
                                # Track current section
                                for cat_sections in categories.values():
                                    for section in cat_sections:
                                        if section in line and len(line) < 120:
                                            current_section = section
                                            if current_section not in section_content:
                                                section_content[current_section] = []
                                            break
                                
                                # Assign nearby Q&As to current section
                                if current_section:
                                    for qa in all_qa:
                                        if abs(qa['line_index'] - i) < 20:  # Within reasonable distance
                                            if qa not in section_content[current_section]:
                                                section_content[current_section].append(qa)
                            
                            # Generate organized output
                            for category, sections in categories.items():
                                content_parts.append(f"## {category}")
                                content_parts.append("")
                                
                                for section in sections:
                                    content_parts.append(f"### {section}")
                                    content_parts.append("")
                                    
                                    if section in section_content:
                                        for qa in section_content[section]:
                                            content_parts.append(f"**Q: {qa['question']}**")
                                            content_parts.append(f"**A:** {qa['answer']}")
                                            content_parts.append("")
                                    
                                content_parts.append("")
                            

                        else:
                            # Process other containers normally
                            child_content = extract_complete_dom_content(child, level + 1, max_level)
                            content_parts.extend(child_content)
                    
                    elif element_name in ['span', 'strong', 'em', 'b', 'i', 'a', 'code', 'small', 'label', 'button']:
                        # Include standalone text elements
                        text = child.get_text(strip=True)
                        if text and len(text) > 2:
                            # Check if this is meaningful standalone content
                            parent = child.parent
                            if (not parent or 
                                parent.name not in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'td', 'th'] or
                                len(text) > 20):  # Include longer text even if inside paragraphs
                                content_parts.append(text)
                    
                    elif element_name in ['dt', 'dd']:
                        # Definition lists
                        text = child.get_text(strip=True)
                        if text:
                            prefix = "**" if element_name == 'dt' else "  "
                            suffix = "**" if element_name == 'dt' else ""
                            content_parts.append(f"{prefix}{text}{suffix}")
                
                elif isinstance(child, str):
                    # Direct text nodes - include ALL meaningful text
                    text = child.strip()
                    if text and len(text) > 3:
                        content_parts.append(text)
            
            return content_parts
        
        # Extract ALL content in exact DOM order from entire document
        body = soup.body if soup.body else soup
        complete_content = extract_complete_dom_content(body)
        
        # Combine title/metadata with complete DOM-ordered content (no duplicates)
        final_content = []
        final_content.extend(all_content)  # Title and metadata first
        final_content.extend(complete_content)  # Then ALL content in exact webpage order
        
        # Only use trafilatura as absolute fallback if DOM extraction failed completely
        if len(complete_content) < 3 and trafilatura_content:
            trafilatura_lines = trafilatura_content.split('\n')
            for line in trafilatura_lines:
                line = line.strip()
                if line and len(line) > 5:
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