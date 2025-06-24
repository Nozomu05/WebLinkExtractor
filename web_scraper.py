import trafilatura
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re

def get_website_text_content(url: str) -> str:
    """
    This function takes a url and returns the main text content of the website.
    The text content is extracted using trafilatura and easier to understand.
    The results is not directly readable, better to be summarized by LLM before consume
    by the user.
    """
    try:
        # Validate URL format
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError("Invalid URL format")
        
        # Send a request to the website with proper headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Use trafilatura's fetch_url which handles requests properly
        downloaded = trafilatura.fetch_url(url)
        
        if not downloaded:
            # Fallback to manual request if trafilatura fails
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            downloaded = response.text
        
        # Extract text content using trafilatura
        text = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=True,
            include_formatting=True,
            favor_precision=True,
            include_links=False
        )
        
        if not text:
            raise ValueError("No extractable content found on this page")
        
        return text.strip()
        
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
    except ValueError as e:
        raise Exception(str(e))
    except Exception as e:
        raise Exception(f"Unexpected error occurred: {str(e)}")

def get_structured_content(url: str) -> str:
    """
    Extract webpage content preserving its original structure and hierarchy
    """
    try:
        # Validate URL format
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError("Invalid URL format")
        
        # Send a request to the website with proper headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Use trafilatura's fetch_url which handles requests properly
        downloaded = trafilatura.fetch_url(url)
        
        if not downloaded:
            # Fallback to manual request if trafilatura fails
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            downloaded = response.text
        
        # Extract content preserving structure - maximize content extraction
        text = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=True,
            include_formatting=True,
            favor_precision=False,  # Favor recall over precision to get more content
            favor_recall=True,
            include_links=False,
            with_metadata=False,
            no_fallback=False,  # Allow fallback methods
            deduplicate=False   # Don't remove duplicate content
        )
        
        # If trafilatura doesn't capture enough content, use BeautifulSoup as fallback
        if not text or len(text.strip()) < 500:
            soup = BeautifulSoup(downloaded, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                script.decompose()
            
            # Extract text from main content areas
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main|article|post', re.I)) or soup.body
            
            if main_content:
                # Get text while preserving some structure
                paragraphs = main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div', 'section', 'li'])
                text_parts = []
                
                for element in paragraphs:
                    element_text = element.get_text(strip=True)
                    if element_text and len(element_text) > 10:  # Filter out very short text
                        # Add spacing based on element type
                        if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                            text_parts.append(f"\n# {element_text}\n")
                        elif element.name == 'p':
                            text_parts.append(f"{element_text}\n")
                        else:
                            text_parts.append(element_text)
                
                if text_parts:
                    text = '\n'.join(text_parts)
        
        if not text:
            raise ValueError("No extractable content found on this page")
        
        return text.strip()
        
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
    except ValueError as e:
        raise Exception(str(e))
    except Exception as e:
        raise Exception(f"Unexpected error occurred: {str(e)}")

def clean_text(text: str) -> str:
    """
    Minimal cleaning while preserving structure
    """
    if not text:
        return ""
    
    # Only remove excessive blank lines while preserving paragraph breaks
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    
    return text.strip()
