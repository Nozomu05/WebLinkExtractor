# URL Content Extractor

## Overview

This is a Streamlit web application that extracts and organizes webpage content into logical topic groups. The application scrapes web content from user-provided URLs, processes the text using natural language processing techniques, and presents the organized content through an intuitive web interface.

## System Architecture

The application follows a modular architecture with clear separation of concerns:

- **Frontend**: Streamlit-based web interface for user interaction
- **Web Scraping**: Trafilatura-based content extraction from URLs
- **Text Processing**: NLTK-powered natural language processing for content organization
- **Deployment**: Replit-hosted with autoscale deployment configuration

The architecture prioritizes simplicity and ease of use, with a single-page application design that handles the entire workflow from URL input to processed content display.

## Key Components

### 1. Main Application (`app.py`)
- **Purpose**: Entry point and user interface controller
- **Key Features**: URL validation, user input handling, content display orchestration
- **Technology**: Streamlit framework for rapid web app development
- **Design Decision**: Chosen for its simplicity and ability to create interactive web apps with minimal code

### 2. Web Scraper (`web_scraper.py`)
- **Purpose**: Extract clean text content from web pages
- **Key Features**: URL validation, content extraction, error handling
- **Technology**: Trafilatura library for robust web content extraction
- **Design Decision**: Trafilatura was chosen over BeautifulSoup for its superior ability to extract main content while filtering out navigation, ads, and boilerplate

### 3. Text Processor (`text_processor.py`)
- **Purpose**: Analyze and organize extracted content using NLP techniques
- **Key Features**: Keyword extraction, content grouping, TF-IDF-like processing
- **Technology**: NLTK for natural language processing tasks
- **Design Decision**: NLTK provides comprehensive NLP capabilities with good documentation and community support

### 4. Configuration Files
- **`.replit`**: Defines deployment and runtime configuration
- **`pyproject.toml`**: Python project dependencies and metadata
- **`.streamlit/config.toml`**: Streamlit server configuration for headless operation

## Data Flow

1. **User Input**: User enters URL through Streamlit interface
2. **Validation**: URL format validation before processing
3. **Content Extraction**: Web scraper fetches and extracts clean text content
4. **Text Processing**: NLP pipeline analyzes content and extracts keywords/topics
5. **Content Organization**: Processed content is grouped into logical sections
6. **Display**: Organized content is presented through Streamlit interface

The flow is designed to be linear and straightforward, with proper error handling at each stage to provide clear feedback to users.

## External Dependencies

### Core Libraries
- **Streamlit (>=1.46.0)**: Web application framework
- **Trafilatura (>=2.0.0)**: Web content extraction
- **NLTK (>=3.9.1)**: Natural language processing
- **Requests (>=2.32.4)**: HTTP requests handling

### NLTK Data Dependencies
- **punkt**: Sentence tokenization
- **stopwords**: Common word filtering
- **averaged_perceptron_tagger**: Part-of-speech tagging

The application automatically downloads required NLTK data on first run, ensuring smooth operation without manual setup.

## Deployment Strategy

### Replit Configuration
- **Runtime**: Python 3.11 with Nix package management
- **Deployment**: Autoscale deployment target for automatic scaling
- **Port Configuration**: Runs on port 5000 with proper server binding
- **Workflow**: Parallel execution support for development efficiency

### Server Settings
- **Headless Mode**: Configured for server deployment without GUI
- **Network Binding**: Accepts connections from all interfaces (0.0.0.0)
- **Process Management**: Streamlit handles server lifecycle automatically

The deployment strategy prioritizes ease of deployment and automatic scaling, making it suitable for varying traffic loads without manual intervention.

## Changelog

```
Changelog:
- June 25, 2025: Successfully implemented Pictures tab with checkbox-controlled image extraction - displays all extracted images from webpages
- June 25, 2025: Fixed image detection logic to properly extract and display images in separate Pictures tab when checkbox is selected
- June 25, 2025: Implemented tabbed interface with checkboxes for media extraction - separate tabs for Text, Pictures, and Videos
- June 25, 2025: Redesigned UI with separate extraction tools: "Extract Text Only", "Extract with Pictures", "Extract with Videos"
- June 25, 2025: Added optional media extraction with checkboxes to include/exclude images and videos in original positions
- June 25, 2025: Completed FAQ extraction system with proper Q&A display under all 8 sections (4 per category)
- June 25, 2025: Added comprehensive README.md with Linux server deployment instructions
- June 25, 2025: Enhanced FAQ extraction to properly structure questions and answers within their respective sections with immediate Q&A pairing
- June 25, 2025: Enhanced extractor to preserve original webpage structure and remove all media content (images, videos, audio)
- June 24, 2025: Initial setup
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```