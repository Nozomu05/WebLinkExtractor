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

def display_content_with_tabs(content, include_pictures, include_videos):
    """Display content in organized tabs"""
    # Separate content types
    text_content = []
    image_content = []
    video_content = []
    
    sections = content.split('\n\n')
    
    for section in sections:
        section = section.strip()
        if not section:
            continue
            
        # Check content type
        if section.startswith('![') and '](' in section and section.endswith(')'):
            image_content.append(section)
        elif section.startswith('**[') and ('VIDEO:' in section or 'AUDIO:' in section or 'EMBEDDED' in section):
            video_content.append(section)
        else:
            text_content.append(section)
    
    # Create tabs based on selected options
    tab_names = ["Text Content"]
    if include_pictures:
        tab_names.append("Pictures")
    if include_videos:
        tab_names.append("Videos")
    

    
    # Always create tabs if any media extraction is enabled
    if include_pictures or include_videos:
        # Create tabs
        tabs = st.tabs(tab_names)
        
        # Text content tab
        with tabs[0]:
            display_formatted_content('\n\n'.join(text_content))
        
        # Pictures tab
        tab_index = 1
        if include_pictures:
            with tabs[tab_index]:
                st.subheader("Extracted Images")
                if image_content:
                    st.write(f"Found {len(image_content)} images:")
                    for i, img_section in enumerate(image_content, 1):
                        st.write(f"**Image {i}:**")
                        display_image_content(img_section)
                        st.write("---")  # Separator between images
                else:
                    st.info("No images found on this webpage.")
                    st.write("This could be because:")
                    st.markdown("- The webpage doesn't contain images")
                    st.markdown("- Images are loaded dynamically with JavaScript")
                    st.markdown("- Images are in unsupported formats")
            tab_index += 1
        
        # Videos tab
        if include_videos:
            with tabs[tab_index]:
                st.subheader("Extracted Videos & Audio")
                if video_content:
                    st.write(f"Found {len(video_content)} videos/audio files:")
                    for i, video_section in enumerate(video_content, 1):
                        st.write(f"**Media {i}:**")
                        display_video_content(video_section)
                        st.write("---")  # Separator between videos
                else:
                    st.info("No videos or audio found on this webpage.")
                    st.write("This could be because:")
                    st.markdown("- The webpage doesn't contain video/audio content")
                    st.markdown("- Media is embedded in unsupported formats")
                    st.markdown("- Media requires JavaScript to load")
    else:
        # Only text content, display normally
        display_formatted_content('\n\n'.join(text_content))

def display_image_content(section):
    """Display image content"""
    try:
        alt_start = section.find('[') + 1
        alt_end = section.find(']')
        url_start = section.find('(') + 1
        url_end = section.find(')')
        
        alt_text = section[alt_start:alt_end]
        image_url = section[url_start:url_end]
        
        if image_url:
            st.image(image_url, caption=alt_text if alt_text else None, use_column_width=True)
    except:
        st.markdown(section)

def display_video_content(section):
    """Display video/audio content"""
    if 'VIDEO:' in section:
        video_url = section.replace('**[VIDEO:', '').replace(']**', '').strip()
        try:
            st.video(video_url)
        except:
            st.markdown(f"**Video:** {video_url}")
    elif 'AUDIO:' in section:
        audio_url = section.replace('**[AUDIO:', '').replace(']**', '').strip()
        try:
            st.audio(audio_url)
        except:
            st.markdown(f"**Audio:** {audio_url}")
    elif 'EMBEDDED VIDEO:' in section:
        embed_url = section.replace('**[EMBEDDED VIDEO:', '').replace(']**', '').strip()
        # Handle YouTube embeds
        if 'youtube.com/watch' in embed_url:
            video_id = embed_url.split('v=')[1].split('&')[0]
            embed_url = f"https://www.youtube.com/embed/{video_id}"
        elif 'youtu.be/' in embed_url:
            video_id = embed_url.split('youtu.be/')[1].split('?')[0]
            embed_url = f"https://www.youtube.com/embed/{video_id}"
        
        st.markdown(f'<iframe width="100%" height="315" src="{embed_url}" frameborder="0" allowfullscreen></iframe>', unsafe_allow_html=True)
    elif 'EMBEDDED CONTENT:' in section:
        embed_url = section.replace('**[EMBEDDED CONTENT:', '').replace(']**', '').strip()
        st.markdown(f"**Embedded Content:** {embed_url}")
    else:
        st.markdown(section)

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
            for line in lines:
                line = line.strip()
                if line.startswith('•'):
                    st.markdown(f"- {line[1:].strip()}")
                elif line and not line.startswith('•'):
                    st.markdown(line)
            st.markdown("")
        
        elif any('|' in line and line.count('|') >= 2 for line in lines):
            # This is a table section
            for line in lines:
                if '|' in line and line.count('|') >= 2:
                    cells = [cell.strip() for cell in line.split('|')]
                    st.markdown(" | ".join(filter(None, cells)))
                else:
                    st.markdown(line)
            st.markdown("")
        
        elif section.startswith('**Q:') and section.endswith('**'):
            # FAQ questions
            question_text = section[4:-2].strip()
            st.markdown(f"### Q: {question_text}")
            st.markdown("")
        
        elif section.startswith('**A:**'):
            # FAQ answers
            answer_text = section[6:].strip()
            st.markdown(f"**Answer:** {answer_text}")
            st.markdown("")
        
        elif section.startswith('![') and '](' in section and section.endswith(')'):
            # Handle images
            try:
                alt_start = section.find('[') + 1
                alt_end = section.find(']')
                url_start = section.find('(') + 1
                url_end = section.find(')')
                
                alt_text = section[alt_start:alt_end]
                image_url = section[url_start:url_end]
                
                if image_url:
                    st.image(image_url, caption=alt_text if alt_text else None)
            except:
                st.markdown(section)
        
        elif section.startswith('**[') and section.endswith(']**'):
            # Handle video/audio/embedded content
            if 'VIDEO:' in section:
                video_url = section.replace('**[VIDEO:', '').replace(']**', '').strip()
                try:
                    st.video(video_url)
                except:
                    st.markdown(f"**Video:** {video_url}")
            elif 'AUDIO:' in section:
                audio_url = section.replace('**[AUDIO:', '').replace(']**', '').strip()
                try:
                    st.audio(audio_url)
                except:
                    st.markdown(f"**Audio:** {audio_url}")
            elif 'EMBEDDED VIDEO:' in section:
                embed_url = section.replace('**[EMBEDDED VIDEO:', '').replace(']**', '').strip()
                # Handle YouTube embeds
                if 'youtube.com/watch' in embed_url:
                    video_id = embed_url.split('v=')[1].split('&')[0]
                    embed_url = f"https://www.youtube.com/embed/{video_id}"
                elif 'youtu.be/' in embed_url:
                    video_id = embed_url.split('youtu.be/')[1].split('?')[0]
                    embed_url = f"https://www.youtube.com/embed/{video_id}"
                
                st.markdown(f'<iframe width="560" height="315" src="{embed_url}" frameborder="0" allowfullscreen></iframe>', unsafe_allow_html=True)
            elif 'EMBEDDED CONTENT:' in section:
                embed_url = section.replace('**[EMBEDDED CONTENT:', '').replace(']**', '').strip()
                st.markdown(f"**Embedded Content:** {embed_url}")
            else:
                st.markdown(section)
        
        elif section.startswith('**') and section.endswith('**'):
            # Other emphasized content
            emphasized_text = section[2:-2].strip()
            st.markdown(f"**{emphasized_text}**")
            st.markdown("")
        
        elif section.startswith('>'):
            # Blockquotes
            quote_text = section[1:].strip()
            st.markdown(f"> {quote_text}")
            st.markdown("")
        
        elif section.startswith('```'):
            # Code blocks
            code_content = section.replace('```', '').strip()
            st.code(code_content, language=None)
            st.markdown("")
        
        else:
            # Regular paragraphs - display exactly as webpage
            section_text = section.strip()
            if len(section_text) > 0:
                if '\n' in section_text:
                    lines = section_text.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line:
                            st.markdown(line)
                    st.markdown("")
                else:
                    st.markdown(section_text)
                    st.markdown("")

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
    
    # Extraction options section
    st.subheader("Extraction Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        extract_pictures = st.checkbox("Extract Pictures", value=False, help="Include images in extraction")
    
    with col2:
        extract_videos = st.checkbox("Extract Videos", value=False, help="Include videos and audio in extraction")
    
    with col3:
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
                # Create dynamic message based on extraction settings
                media_status = []
                if extract_pictures:
                    media_status.append("images included")
                if extract_videos:
                    media_status.append("videos included")
                
                if media_status:
                    status_text = f"({', '.join(media_status)})"
                else:
                    status_text = "(text only)"
                
                st.success(f"Successfully extracted content from: **{url_input}** {status_text}")
                
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
                
                # Separate content types for tab display
                text_content = []
                image_content = []
                video_content = []
                
                sections = content.split('\n\n')
                
                for section in sections:
                    section = section.strip()
                    if not section:
                        continue
                        
                    # Check content type - look for images anywhere in the section
                    if '![' in section and '](' in section:
                        # Extract individual image patterns from the section
                        import re
                        img_patterns = re.findall(r'!\[.*?\]\([^)]+\)', section)
                        if img_patterns:
                            image_content.extend(img_patterns)
                            # Remove images from text content and keep the rest
                            text_part = section
                            for img in img_patterns:
                                text_part = text_part.replace(img, '').strip()
                            if text_part:
                                text_content.append(text_part)
                        else:
                            text_content.append(section)
                    elif section.startswith('**[') and ('VIDEO:' in section or 'AUDIO:' in section or 'EMBEDDED' in section):
                        video_content.append(section)
                    else:
                        text_content.append(section)
                
                # Create tabs based on selected options
                tab_names = ["Text Content"]
                if extract_pictures:
                    tab_names.append("Pictures")
                if extract_videos:
                    tab_names.append("Videos")
                
                # Always create tabs if any media extraction is enabled
                if extract_pictures or extract_videos:
                    # Create tabs
                    tabs = st.tabs(tab_names)
                    
                    # Text content tab
                    with tabs[0]:
                        display_formatted_content('\n\n'.join(text_content))
                    
                    # Pictures tab
                    tab_index = 1
                    if extract_pictures:
                        with tabs[tab_index]:
                            st.subheader("Extracted Images")
                            if image_content:
                                st.write(f"Found {len(image_content)} images:")
                                for i, img_section in enumerate(image_content, 1):
                                    st.write(f"**Image {i}:**")
                                    display_image_content(img_section)
                                    st.write("---")
                            else:
                                st.info("No images found on this webpage.")
                                st.write("**Debug Info:**")
                                st.write(f"Total content sections: {len(sections)}")
                                st.write("Sample sections:")
                                for i, section in enumerate(sections[:5]):
                                    if section.strip():
                                        st.write(f"Section {i+1}: {section[:100]}...")
                                
                                st.write("**This could be because:**")
                                st.markdown("- The webpage doesn't contain images")
                                st.markdown("- Images are loaded dynamically with JavaScript")
                                st.markdown("- Images are in unsupported formats")
                        tab_index += 1
                    
                    # Videos tab
                    if extract_videos:
                        with tabs[tab_index]:
                            st.subheader("Extracted Videos & Audio")
                            if video_content:
                                st.write(f"Found {len(video_content)} videos/audio files:")
                                for i, video_section in enumerate(video_content, 1):
                                    st.write(f"**Media {i}:**")
                                    display_video_content(video_section)
                                    st.write("---")
                            else:
                                st.info("No videos or audio found on this webpage.")
                                st.write("This could be because:")
                                st.markdown("- The webpage doesn't contain video/audio content")
                                st.markdown("- Media is embedded in unsupported formats")
                                st.markdown("- Media requires JavaScript to load")
                else:
                    # Only text content, display normally
                    display_formatted_content('\n\n'.join(text_content))
                
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
