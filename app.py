import streamlit as st
import requests
import re
from urllib.parse import urlparse
from web_scraper import get_website_text_content, get_structured_content

# Configure the Streamlit page
st.set_page_config(
    page_title="URL Content Extractor",
    page_icon="🔍",
    layout="wide"
)

def is_valid_url(url):
    """
    Validate if the provided URL is properly formatted
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def main():
    st.title("🔍 URL Content Extractor")
    st.markdown("Extract and organize webpage content into logical topic groups")
    
    # URL input section
    st.subheader("Enter URL to Extract Content")
    url_input = st.text_input(
        "URL:",
        placeholder="https://example.com/article",
        help="Enter a valid URL to extract and organize its content"
    )
    
    # Extract button
    extract_button = st.button("Extract Content", type="primary")
    
    if extract_button:
        if not url_input:
            st.error("Please enter a URL to extract content from.")
            return
        
        if not is_valid_url(url_input):
            st.error("Please enter a valid URL (must include http:// or https://)")
            return
        
        # Show loading state
        with st.spinner("Extracting content..."):
            try:
                # Extract content from the webpage preserving structure
                content = get_structured_content(url_input)
                
                if not content or len(content.strip()) < 50:
                    st.warning("Unable to extract meaningful content from this URL. The page might be:")
                    st.markdown("""
                    - Protected by anti-bot measures
                    - Requiring JavaScript to load content
                    - Containing mostly images or videos
                    - Behind a paywall or login
                    """)
                    return
                
                # Display results
                st.success(f"Successfully extracted content from: {url_input}")
                
                # Show content statistics
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Characters", len(content))
                with col2:
                    word_count = len(content.split())
                    st.metric("Word Count", word_count)
                
                st.divider()
                
                # Display content preserving original structure
                st.subheader("📄 Extracted Content")
                st.markdown("*Content displayed as it appears on the original webpage*")
                
                # Display the content in a clean format
                st.markdown(content)
                
                # Add export functionality
                st.divider()
                st.subheader("📤 Export Options")
                
                # Prepare export content
                export_content = f"# Content extracted from: {url_input}\n\n"
                export_content += content
                
                st.download_button(
                    label="Download as Markdown",
                    data=export_content,
                    file_name=f"extracted_content_{urlparse(url_input).netloc}.md",
                    mime="text/markdown"
                )
                
            except requests.exceptions.RequestException as e:
                st.error(f"Network error: Unable to access the URL. Please check your internet connection and try again.")
                st.caption(f"Technical details: {str(e)}")
            except Exception as e:
                st.error(f"An error occurred while processing the content: {str(e)}")
                st.caption("Please try with a different URL or contact support if the issue persists.")
    
    # Add information section
    st.divider()
    with st.expander("ℹ️ How it works"):
        st.markdown("""
        **URL Content Extractor** extracts webpage content preserving its original structure:
        
        1. **Content Extraction**: Retrieves clean text content from the webpage, removing ads, navigation, and other clutter
        2. **Structure Preservation**: Maintains the original hierarchy and flow of the content
        3. **Clean Display**: Presents content exactly as it appears on the webpage
        
        **Best Results With:**
        - News articles and blog posts
        - Educational content and tutorials
        - Product descriptions and reviews
        - Research papers and documentation
        
        **May Not Work Well With:**
        - Social media feeds
        - Image-heavy websites
        - Interactive web applications
        - Sites requiring login or subscription
        """)

if __name__ == "__main__":
    main()
