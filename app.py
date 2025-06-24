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
            # Regular content section
            section_text = section.strip()
            if len(section_text) > 0:
                # Split very long sections into paragraphs
                if len(section_text) > 500:
                    # Try to split on sentence boundaries
                    sentences = re.split(r'(?<=[.!?])\s+', section_text)
                    current_paragraph = []
                    
                    for sentence in sentences:
                        current_paragraph.append(sentence)
                        # Group roughly 2-3 sentences per paragraph
                        if len(current_paragraph) >= 3 or len(' '.join(current_paragraph)) > 300:
                            st.markdown(' '.join(current_paragraph))
                            st.markdown("")  # Add spacing
                            current_paragraph = []
                    
                    # Display remaining sentences
                    if current_paragraph:
                        st.markdown(' '.join(current_paragraph))
                        st.markdown("")
                else:
                    # Display as single paragraph
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
