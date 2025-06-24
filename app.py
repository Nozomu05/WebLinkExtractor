import streamlit as st
import requests
import re
from urllib.parse import urlparse
from web_scraper import get_website_text_content
from text_processor import process_and_group_content

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
        with st.spinner("Extracting and processing content..."):
            try:
                # Extract content from the webpage
                content = get_website_text_content(url_input)
                
                if not content or len(content.strip()) < 50:
                    st.warning("Unable to extract meaningful content from this URL. The page might be:")
                    st.markdown("""
                    - Protected by anti-bot measures
                    - Requiring JavaScript to load content
                    - Containing mostly images or videos
                    - Behind a paywall or login
                    """)
                    return
                
                # Process and group the content
                grouped_content = process_and_group_content(content)
                
                # Display results
                st.success(f"Successfully extracted content from: {url_input}")
                
                # Show content statistics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Characters", len(content))
                with col2:
                    st.metric("Topic Groups", len(grouped_content))
                with col3:
                    word_count = len(content.split())
                    st.metric("Word Count", word_count)
                
                st.divider()
                
                # Display grouped content
                st.subheader("📋 Organized Content by Topics")
                
                if not grouped_content:
                    st.info("No distinct topic groups were identified. The content appears to be uniform in nature.")
                    st.subheader("Full Content")
                    st.markdown(content)
                else:
                    # Display each topic group
                    for i, group in enumerate(grouped_content, 1):
                        with st.expander(f"📝 Topic Group {i}: {group['title']}", expanded=True):
                            st.markdown(group['content'])
                            
                            # Show additional metadata if available
                            if group.get('keywords'):
                                st.caption(f"Key themes: {', '.join(group['keywords'][:5])}")
                
                # Add export functionality
                st.divider()
                st.subheader("📤 Export Options")
                
                # Prepare export content
                export_content = f"# Content extracted from: {url_input}\n\n"
                for i, group in enumerate(grouped_content, 1):
                    export_content += f"## Topic Group {i}: {group['title']}\n\n"
                    export_content += f"{group['content']}\n\n"
                    if group.get('keywords'):
                        export_content += f"**Key themes:** {', '.join(group['keywords'][:5])}\n\n"
                    export_content += "---\n\n"
                
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
        **URL Content Extractor** intelligently processes webpage content through these steps:
        
        1. **Content Extraction**: Retrieves clean text content from the webpage, removing ads, navigation, and other clutter
        2. **Text Processing**: Analyzes the content structure and identifies key themes
        3. **Topic Grouping**: Groups related sentences and paragraphs based on semantic similarity
        4. **Organization**: Presents content in logical sections with descriptive titles
        
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
