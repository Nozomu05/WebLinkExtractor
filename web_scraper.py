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
        
        # First try trafilatura with maximum extraction settings
        text = trafilatura.extract(
            downloaded,
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
        
        # Always use BeautifulSoup to extract comprehensive content
        soup = BeautifulSoup(downloaded, 'html.parser')
        
        # Remove unwanted elements but keep more content
        for element in soup(["script", "style", "noscript"]):
            element.decompose()
        
        # Extract all text content from the entire page
        all_text_elements = soup.find_all(text=True)
        full_text_parts = []
        
        for text_element in all_text_elements:
            text_content = text_element.strip()
            if text_content and len(text_content) > 3:  # Keep even shorter text
                # Skip if it's just whitespace or common web elements
                if not re.match(r'^[\s\n\r\t]*$', text_content):
                    full_text_parts.append(text_content)
        
        # Combine all extracted text
        comprehensive_text = '\n'.join(full_text_parts)
        
        # Use the more comprehensive extraction if it's significantly longer
        if len(comprehensive_text) > len(text or ''):
            text = comprehensive_text
        
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
