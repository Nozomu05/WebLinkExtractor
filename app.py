import streamlit as st
import requests
import re
from urllib.parse import urlparse
from complete_data_extractor import extract_all_webpage_data

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
    Display content with proper formatting and structure
    """
    if not content:
        st.warning("No content to display")
        return
    
    # Clean up the content first
    content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)  # Remove excessive line breaks
    
    # Split content into sections
    sections = content.split('\n\n')
    
    for section in sections:
        section = section.strip()
        if not section:
            continue
        
        lines = section.split('\n')
        
        # Check if this section starts with a heading
        first_line = lines[0].strip()
        
        if first_line.startswith('#'):
            # This is a heading section
            heading_level = len(first_line) - len(first_line.lstrip('#'))
            heading_text = first_line.lstrip('# ').strip()
            
            # Display heading
            if heading_level == 1:
                st.header(heading_text)
            elif heading_level == 2:
                st.subheader(heading_text)
            else:
                st.markdown(f"{'#' * heading_level} {heading_text}")
            
            # Display rest of section if any
            if len(lines) > 1:
                remaining_content = '\n'.join(lines[1:]).strip()
                if remaining_content:
                    st.markdown(remaining_content)
        
        elif any(line.strip().startswith('•') for line in lines):
            # This is a list section
            st.markdown("**List:**")
            for line in lines:
                line = line.strip()
                if line.startswith('•'):
                    st.markdown(f"  {line}")
                elif line and not line.startswith('•'):
                    st.markdown(line)
        
        elif any('|' in line and line.count('|') >= 2 for line in lines):
            # This is a table section
            st.markdown("**Table:**")
            for line in lines:
                if '|' in line and line.count('|') >= 2:
                    st.markdown(f"`{line}`")
                else:
                    st.markdown(line)
        
        else:
            # Regular content section - display as webpage structure
            section_text = section.strip()
            if len(section_text) > 0:
                # Check if this looks like multiple sentences that should be separate blocks
                if '. ' in section_text and len(section_text) > 200:
                    # Split into natural blocks maintaining flow
                    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', section_text)
                    
                    # Group sentences into logical blocks (like webpage paragraphs)
                    current_block = []
                    for sentence in sentences:
                        current_block.append(sentence)
                        
                        # Create new block when we have 1-2 sentences or reach reasonable length
                        if (len(current_block) >= 2 or 
                            len(' '.join(current_block)) > 250 or
                            sentence.endswith(('.', '!', '?')) and len(' '.join(current_block)) > 100):
                            
                            block_text = ' '.join(current_block).strip()
                            if block_text:
                                st.markdown(block_text)
                                st.markdown("")  # Add spacing like webpage paragraphs
                            current_block = []
                    
                    # Display any remaining content
                    if current_block:
                        block_text = ' '.join(current_block).strip()
                        if block_text:
                            st.markdown(block_text)
                            st.markdown("")
                else:
                    # Display as single block maintaining webpage structure
                    st.markdown(section_text)
                    st.markdown("")  # Add spacing between sections

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
                # Extract all data from the webpage
                content = extract_all_webpage_data(url_input)
                
                if not content or len(content.strip()) < 50:
                    st.warning("Unable to extract meaningful content from this URL.")
                    st.info("**Possible reasons:**")
                    st.markdown("""
                    - The website requires JavaScript to load content
                    - Content is protected by anti-bot measures  
                    - Page contains mostly images, videos, or interactive elements
                    - Content is behind a paywall or login system
                    - Website is temporarily unavailable
                    """)
                    st.markdown("**Try these alternatives:**")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("""
                        **Different URLs:**
                        - News articles (BBC, CNN, etc.)
                        - Blog posts 
                        - Wikipedia pages
                        - Documentation sites
                        """)
                    with col2:
                        st.markdown("""
                        **Test URLs:**
                        - https://en.wikipedia.org/wiki/Python_(programming_language)
                        - https://www.bbc.com/news
                        - https://medium.com/@username/article
                        """)
                    return
                
                # Display results with enhanced styling
                st.success(f"Successfully extracted content from: **{url_input}** (Images and media removed)")
                
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
                        Webpage Content (Media-Free)
                    </h2>
                    <p style="color: #f0f0f0; text-align: center; margin: 10px 0 0 0; font-style: italic;">
                        Preserving original webpage structure and layout
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
