import streamlit as st
import requests
import re
from urllib.parse import urlparse
from complete_extractor import extract_complete_webpage_content

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

def display_formatted_content(content):
    """
    Display content with each text block on a new line as it appears on the webpage
    """
    if not content:
        st.warning("No content to display")
        return
    
    # Split content into lines for processing
    lines = content.split('\n')
    
    in_list = False
    list_items = []
    
    for line in lines:
        line = line.strip()
        
        # Skip completely empty lines
        if not line:
            # If we were building a list, display it
            if in_list and list_items:
                for item in list_items:
                    st.markdown(f"• {item}")
                list_items = []
                in_list = False
            continue
        
        # Handle headings
        if line.startswith('#'):
            # Display any accumulated list first
            if in_list and list_items:
                for item in list_items:
                    st.markdown(f"• {item}")
                list_items = []
                in_list = False
            
            # Count heading level and display
            heading_level = len(line) - len(line.lstrip('#'))
            heading_text = line.lstrip('# ').strip()
            
            if heading_level == 1:
                st.header(heading_text)
            elif heading_level == 2:
                st.subheader(heading_text)
            elif heading_level == 3:
                st.markdown(f"### {heading_text}")
            else:
                st.markdown(f"{'#' * heading_level} {heading_text}")
        
        # Handle list items
        elif line.startswith('•') or line.startswith('-') or line.startswith('*'):
            list_item = line.lstrip('•-* ').strip()
            if list_item:
                list_items.append(list_item)
                in_list = True
        
        # Handle table-like content (with |)
        elif '|' in line and line.count('|') >= 2:
            # Display any accumulated list first
            if in_list and list_items:
                for item in list_items:
                    st.markdown(f"• {item}")
                list_items = []
                in_list = False
            
            # Display table row
            st.markdown(line)
        
        # Regular text content - each line is a separate block
        else:
            # Display any accumulated list first
            if in_list and list_items:
                for item in list_items:
                    st.markdown(f"• {item}")
                list_items = []
                in_list = False
            
            # Display this text block on its own line
            if line and len(line.strip()) > 2:
                st.markdown(line)
    
    # Display any remaining list items
    if in_list and list_items:
        for item in list_items:
            st.markdown(f"• {item}")

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
                # Extract complete content from the webpage
                content = extract_complete_webpage_content(url_input)
                
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
                
                # Display content with improved formatting
                display_formatted_content(content)
                
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
