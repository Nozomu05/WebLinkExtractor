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
    Display content with enhanced visual appeal and formatting
    """
    if not content:
        st.warning("No content to display")
        return
    
    # Add custom CSS for better styling
    st.markdown("""
    <style>
    .content-block {
        margin-bottom: 15px;
        padding: 12px;
        border-left: 3px solid #e6e6e6;
        background-color: #f8f9fa;
        border-radius: 5px;
    }
    .heading-block {
        margin: 20px 0 15px 0;
        padding: 15px;
        background: linear-gradient(90deg, #f0f2f6 0%, #ffffff 100%);
        border-left: 4px solid #4CAF50;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .list-container {
        background-color: #fff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    .table-container {
        background-color: #f9f9f9;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        margin: 15px 0;
        overflow: auto;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Split content into lines for processing
    lines = content.split('\n')
    
    in_list = False
    list_items = []
    paragraph_count = 0
    
    for line in lines:
        line = line.strip()
        
        # Skip completely empty lines
        if not line:
            # If we were building a list, display it
            if in_list and list_items:
                st.markdown('<div class="list-container">', unsafe_allow_html=True)
                for item in list_items:
                    st.markdown(f"🔸 {item}")
                st.markdown('</div>', unsafe_allow_html=True)
                list_items = []
                in_list = False
            continue
        
        # Handle headings with enhanced styling
        if line.startswith('#'):
            # Display any accumulated list first
            if in_list and list_items:
                st.markdown('<div class="list-container">', unsafe_allow_html=True)
                for item in list_items:
                    st.markdown(f"🔸 {item}")
                st.markdown('</div>', unsafe_allow_html=True)
                list_items = []
                in_list = False
            
            # Count heading level and display with enhanced styling
            heading_level = len(line) - len(line.lstrip('#'))
            heading_text = line.lstrip('# ').strip()
            
            if heading_level == 1:
                st.markdown(f'<div class="heading-block"><h1 style="color: #2E8B57; margin: 0;">{heading_text}</h1></div>', unsafe_allow_html=True)
            elif heading_level == 2:
                st.markdown(f'<div class="heading-block"><h2 style="color: #4169E1; margin: 0;">{heading_text}</h2></div>', unsafe_allow_html=True)
            elif heading_level == 3:
                st.markdown(f'<div class="heading-block"><h3 style="color: #FF6347; margin: 0;">{heading_text}</h3></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="heading-block"><h{min(heading_level, 6)} style="color: #9370DB; margin: 0;">{heading_text}</h{min(heading_level, 6)}></div>', unsafe_allow_html=True)
        
        # Handle list items
        elif line.startswith('•') or line.startswith('-') or line.startswith('*'):
            list_item = line.lstrip('•-* ').strip()
            if list_item:
                list_items.append(list_item)
                in_list = True
        
        # Handle table-like content with enhanced styling
        elif '|' in line and line.count('|') >= 2:
            # Display any accumulated list first
            if in_list and list_items:
                st.markdown('<div class="list-container">', unsafe_allow_html=True)
                for item in list_items:
                    st.markdown(f"🔸 {item}")
                st.markdown('</div>', unsafe_allow_html=True)
                list_items = []
                in_list = False
            
            # Display table row with styling
            st.markdown('<div class="table-container">', unsafe_allow_html=True)
            st.markdown(f"**{line}**")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Regular text content with enhanced blocks
        else:
            # Display any accumulated list first
            if in_list and list_items:
                st.markdown('<div class="list-container">', unsafe_allow_html=True)
                for item in list_items:
                    st.markdown(f"🔸 {item}")
                st.markdown('</div>', unsafe_allow_html=True)
                list_items = []
                in_list = False
            
            # Display text block with enhanced styling
            if line and len(line.strip()) > 2:
                paragraph_count += 1
                
                # Add visual variety to paragraphs
                if len(line) > 200:  # Long paragraphs
                    st.markdown(f'<div class="content-block"><p style="text-align: justify; line-height: 1.6; font-size: 16px;">{line}</p></div>', unsafe_allow_html=True)
                elif len(line) < 50:  # Short text - could be captions or labels
                    st.markdown(f'<div style="padding: 8px; background-color: #e8f4f8; border-radius: 15px; text-align: center; margin: 10px 0; font-style: italic; color: #2c3e50;"><small>{line}</small></div>', unsafe_allow_html=True)
                else:  # Regular paragraphs
                    st.markdown(f'<div class="content-block"><p style="line-height: 1.5;">{line}</p></div>', unsafe_allow_html=True)
    
    # Display any remaining list items
    if in_list and list_items:
        st.markdown('<div class="list-container">', unsafe_allow_html=True)
        for item in list_items:
            st.markdown(f"🔸 {item}")
        st.markdown('</div>', unsafe_allow_html=True)

def main():
    # Enhanced title with gradient background
    st.markdown("""
    <div style="background: linear-gradient(90deg, #ff7e5f 0%, #feb47b 100%); 
               padding: 30px; border-radius: 15px; margin-bottom: 30px; text-align: center;">
        <h1 style="color: white; margin: 0; font-size: 3em;">🔍 URL Content Extractor</h1>
        <p style="color: #fff; font-size: 1.2em; margin: 10px 0 0 0; opacity: 0.9;">
            Extract and beautifully format webpage content with preserved structure
        </p>
    </div>
    """, unsafe_allow_html=True)
    
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
                
                # Display results with enhanced styling
                st.success(f"✅ Successfully extracted content from: **{url_input}**")
                
                # Show content statistics with better visual design
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📊 Total Characters", f"{len(content):,}", delta=None)
                with col2:
                    word_count = len(content.split())
                    st.metric("📝 Word Count", f"{word_count:,}", delta=None)
                with col3:
                    line_count = len([line for line in content.split('\n') if line.strip()])
                    st.metric("📋 Content Blocks", line_count, delta=None)
                
                # Add visual separator
                st.markdown("---")
                
                # Enhanced header for content section
                st.markdown("""
                <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                           padding: 20px; border-radius: 10px; margin: 20px 0;">
                    <h2 style="color: white; margin: 0; text-align: center;">
                        📄 Extracted Website Content
                    </h2>
                    <p style="color: #f0f0f0; text-align: center; margin: 10px 0 0 0; font-style: italic;">
                        Formatted and organized for easy reading
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Display content with improved formatting
                display_formatted_content(content)
                
                # Enhanced export section
                st.markdown("---")
                st.markdown("""
                <div style="background-color: #f0f8ff; padding: 20px; border-radius: 10px; border: 2px dashed #4682b4;">
                    <h3 style="color: #4682b4; margin-top: 0;">📤 Export Your Content</h3>
                    <p style="color: #2c3e50; margin-bottom: 0;">Save the extracted content for later use</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Prepare export content
                export_content = f"# Content extracted from: {url_input}\n\n"
                export_content += f"**Extraction Date:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                export_content += f"**Word Count:** {word_count:,}\n\n"
                export_content += f"---\n\n{content}"
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.download_button(
                        label="📄 Download as Markdown",
                        data=export_content,
                        file_name=f"content_{urlparse(url_input).netloc}_{__import__('datetime').datetime.now().strftime('%Y%m%d_%H%M')}.md",
                        mime="text/markdown",
                        help="Download the content in Markdown format for easy editing"
                    )
                
                with col2:
                    # Plain text export option
                    plain_text = content.replace('#', '').replace('•', '-')
                    st.download_button(
                        label="📝 Download as Text",
                        data=plain_text,
                        file_name=f"content_{urlparse(url_input).netloc}_{__import__('datetime').datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                        mime="text/plain",
                        help="Download as plain text file"
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
