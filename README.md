# URL Content Extractor

A comprehensive web content extraction and presentation tool that transforms complex web pages into clean, structured, and readable formats with advanced parsing capabilities and depth scraping functionality.

## 🚀 Features

### Core Functionality
- **Smart Content Extraction**: Extract clean text content while preserving original webpage structure
- **Media Extraction**: Optional extraction of images and videos with separate display tabs
- **Depth Scraping**: Crawl linked pages from the same domain with configurable depth levels
- **Domain-Safe Crawling**: Respects robots.txt and stays within the same domain
- **Structured Output**: Organized content with proper formatting and hierarchy

### User Interface
- **Streamlit Web App**: Interactive web interface with real-time extraction
- **Progress Tracking**: Visual indicators for multi-page scraping operations
- **Download Options**: Export content as Markdown or plain text
- **Statistics Dashboard**: Character counts, word counts, and extraction metrics

### API Access
- **RESTful API**: Full programmatic access with FastAPI
- **Multiple Endpoints**: Single-page and depth extraction options
- **Interactive Documentation**: Swagger UI at `/docs`
- **CORS Support**: Cross-origin requests enabled

## 🛠 Technical Stack

- **Backend**: Python 3.11+ with FastAPI and Streamlit
- **Web Scraping**: Trafilatura for content extraction, BeautifulSoup for DOM parsing
- **Text Processing**: NLTK for natural language processing
- **Deployment**: Replit with autoscale configuration
- **API Documentation**: OpenAPI/Swagger integration

## 📋 Installation & Setup

### Prerequisites
- Python 3.11+
- pip package manager

### Dependencies
```bash
# Core dependencies
streamlit>=1.46.0
fastapi>=0.104.0
uvicorn>=0.24.0
trafilatura>=2.0.0
beautifulsoup4>=4.12.0
nltk>=3.9.1
requests>=2.32.4
pydantic>=2.5.0
python-multipart>=0.0.6
```

### Installation
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the applications:
   ```bash
   # Start Streamlit web interface
   streamlit run app.py --server.port 5000
   
   # Start FastAPI server (in separate terminal)
   python api.py
   ```

## 🌐 Web Interface Usage

### Basic Extraction
1. Enter a URL in the input field
2. Select extraction options:
   - **Extract Pictures**: Include images in the output
   - **Extract Videos**: Include videos and audio content
3. Click "Extract Content" to process the webpage

### Depth Scraping
1. Check "Enable Depth Scraping"
2. Configure options:
   - **Scraping Depth** (1-3): How many levels of links to follow
   - **Max Pages** (5-25): Maximum number of pages to scrape
3. The system will crawl linked pages from the same domain

### Results
- View extracted content with preserved structure
- See statistics: character count, word count, pages scraped
- Download results as Markdown or plain text files

## 🔌 API Documentation

### Base URL
```
http://localhost:8000
```

### Authentication
No authentication required for local deployment.

### Endpoints

#### Health Check
```http
GET /health
```
**Response:**
```json
{
  "status": "healthy",
  "service": "url-content-extractor"
}
```

#### Root Information
```http
GET /
```
**Response:**
```json
{
  "message": "URL Content Extractor API",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

#### Single Page Extraction (GET)
```http
GET /extract?url={url}&include_images={boolean}&include_videos={boolean}
```

**Parameters:**
- `url` (required): The webpage URL to extract content from
- `include_images` (optional, default: false): Include images in extraction
- `include_videos` (optional, default: false): Include videos in extraction

**Example:**
```http
GET /extract?url=https://example.com&include_images=true&include_videos=false
```

#### Single Page Extraction (POST)
```http
POST /extract
Content-Type: application/json

{
  "url": "https://example.com",
  "include_images": false,
  "include_videos": false
}
```

#### Depth Extraction (POST)
```http
POST /extract/depth
Content-Type: application/json

{
  "url": "https://example.com",
  "include_images": false,
  "include_videos": false,
  "depth": 2,
  "max_pages": 15,
  "delay": 1.0
}
```

**Parameters:**
- `url` (required): Starting URL for depth extraction
- `include_images` (optional, default: false): Include images
- `include_videos` (optional, default: false): Include videos
- `depth` (optional, default: 1): Scraping depth (1-3)
- `max_pages` (optional, default: 10): Maximum pages to scrape (5-50)
- `delay` (optional, default: 1.0): Delay between requests (0.5-3.0 seconds)

#### Depth Extraction (GET)
```http
GET /extract/depth?url={url}&depth={int}&max_pages={int}&delay={float}
```

### Response Format

#### Standard Extraction Response
```json
{
  "success": true,
  "url": "https://example.com",
  "content": {
    "text": ["Content sections..."],
    "images": ["Image URLs..."],
    "videos": ["Video URLs..."]
  },
  "stats": {
    "total_characters": 1250,
    "word_count": 200,
    "text_sections": 5,
    "image_count": 3,
    "video_count": 1
  },
  "message": "Content extracted successfully"
}
```

#### Depth Extraction Response
```json
{
  "success": true,
  "url": "https://example.com",
  "depth": 2,
  "max_pages": 15,
  "content": "# Depth Scraping Results\n\n**Start URL:** https://example.com...",
  "stats": {
    "total_characters": 5240,
    "word_count": 850,
    "extraction_type": "depth_scraping"
  },
  "message": "Depth extraction completed (depth: 2, max pages: 15)"
}
```

#### Error Response
```json
{
  "success": false,
  "error": "Invalid URL format",
  "details": "URL must include http:// or https://"
}
```

## 📮 Postman Collection

### Import Instructions
1. Open Postman
2. Click "Import" button
3. Select "Raw text" tab
4. Paste the collection JSON below
5. Click "Continue" and then "Import"

### Collection JSON
```json
{
  "info": {
    "name": "URL Content Extractor API",
    "description": "Complete API collection for URL Content Extractor with depth scraping capabilities",
    "version": "1.0.0"
  },
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000",
      "type": "string"
    },
    {
      "key": "test_url",
      "value": "https://example.com",
      "type": "string"
    }
  ],
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{base_url}}/health",
          "host": ["{{base_url}}"],
          "path": ["health"]
        },
        "description": "Check API health status"
      }
    },
    {
      "name": "API Info",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{base_url}}/",
          "host": ["{{base_url}}"],
          "path": [""]
        },
        "description": "Get API information and available endpoints"
      }
    },
    {
      "name": "Extract Content (GET)",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{base_url}}/extract?url={{test_url}}&include_images=false&include_videos=false",
          "host": ["{{base_url}}"],
          "path": ["extract"],
          "query": [
            {
              "key": "url",
              "value": "{{test_url}}"
            },
            {
              "key": "include_images",
              "value": "false"
            },
            {
              "key": "include_videos",
              "value": "false"
            }
          ]
        },
        "description": "Extract content from a single webpage using GET method"
      }
    },
    {
      "name": "Extract Content (POST)",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"url\": \"{{test_url}}\",\n  \"include_images\": false,\n  \"include_videos\": false\n}"
        },
        "url": {
          "raw": "{{base_url}}/extract",
          "host": ["{{base_url}}"],
          "path": ["extract"]
        },
        "description": "Extract content from a single webpage using POST method"
      }
    },
    {
      "name": "Extract Text Only",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"url\": \"{{test_url}}\"\n}"
        },
        "url": {
          "raw": "{{base_url}}/extract/text-only",
          "host": ["{{base_url}}"],
          "path": ["extract", "text-only"]
        },
        "description": "Extract only text content from a webpage"
      }
    },
    {
      "name": "Extract with Images",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"url\": \"{{test_url}}\"\n}"
        },
        "url": {
          "raw": "{{base_url}}/extract/with-images",
          "host": ["{{base_url}}"],
          "path": ["extract", "with-images"]
        },
        "description": "Extract text and images from a webpage"
      }
    },
    {
      "name": "Extract with Videos",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"url\": \"{{test_url}}\"\n}"
        },
        "url": {
          "raw": "{{base_url}}/extract/with-videos",
          "host": ["{{base_url}}"],
          "path": ["extract", "with-videos"]
        },
        "description": "Extract text and videos from a webpage"
      }
    },
    {
      "name": "Extract Full Content",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"url\": \"{{test_url}}\"\n}"
        },
        "url": {
          "raw": "{{base_url}}/extract/full",
          "host": ["{{base_url}}"],
          "path": ["extract", "full"]
        },
        "description": "Extract all content types (text, images, and videos)"
      }
    },
    {
      "name": "Depth Extraction (POST)",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"url\": \"{{test_url}}\",\n  \"include_images\": false,\n  \"include_videos\": false,\n  \"depth\": 2,\n  \"max_pages\": 10,\n  \"delay\": 1.0\n}"
        },
        "url": {
          "raw": "{{base_url}}/extract/depth",
          "host": ["{{base_url}}"],
          "path": ["extract", "depth"]
        },
        "description": "Extract content with depth scraping using POST method"
      }
    },
    {
      "name": "Depth Extraction (GET)",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{base_url}}/extract/depth?url={{test_url}}&depth=2&max_pages=10&delay=1.0&include_images=false&include_videos=false",
          "host": ["{{base_url}}"],
          "path": ["extract", "depth"],
          "query": [
            {
              "key": "url",
              "value": "{{test_url}}"
            },
            {
              "key": "depth",
              "value": "2"
            },
            {
              "key": "max_pages",
              "value": "10"
            },
            {
              "key": "delay",
              "value": "1.0"
            },
            {
              "key": "include_images",
              "value": "false"
            },
            {
              "key": "include_videos",
              "value": "false"
            }
          ]
        },
        "description": "Extract content with depth scraping using GET method"
      }
    }
  ]
}
```

### Environment Variables
Set these variables in Postman for easy testing:

| Variable | Value | Description |
|----------|-------|-------------|
| `base_url` | `http://localhost:8000` | API base URL |
| `test_url` | `https://example.com` | URL for testing extraction |

### Testing Workflow
1. **Health Check**: Verify API is running
2. **API Info**: Get endpoint information
3. **Single Page Extraction**: Test basic extraction
4. **Depth Extraction**: Test multi-page crawling
5. **Media Extraction**: Test with images/videos enabled

## 🔧 Configuration

### Streamlit Configuration
Create `.streamlit/config.toml`:
```toml
[server]
headless = true
address = "0.0.0.0"
port = 5000
```

### API Configuration
- Default port: 8000
- CORS enabled for all origins
- Auto-reload enabled in development

### Depth Scraping Limits
- **Depth Levels**: 1-3 (configurable)
- **Max Pages**: 5-50 (configurable)
- **Request Delay**: 0.5-3.0 seconds (configurable)
- **Same Domain Only**: Automatic domain filtering

## 🚨 Error Handling

### Common Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| 400 | Invalid URL format | Ensure URL includes http:// or https:// |
| 422 | Unprocessable content | Check if URL contains extractable content |
| 429 | Rate limiting | Reduce request frequency |
| 500 | Server error | Check server logs for details |

### Troubleshooting

#### No Content Extracted
- Website may require JavaScript
- Content behind paywall/login
- Anti-bot protection active
- Try different URLs (news sites, blogs, documentation)

#### Depth Scraping Issues
- Verify domain has linkable pages
- Check if robots.txt blocks crawling
- Reduce depth/max_pages if timing out

## 📊 Performance

### Benchmarks
- **Single Page**: ~2-5 seconds average
- **Depth Scraping**: Varies by page count and delay settings
- **API Throughput**: ~10-20 requests/second
- **Memory Usage**: ~50-100MB per extraction

### Optimization Tips
- Use appropriate delay settings (1-2 seconds recommended)
- Limit max_pages for faster results
- Cache frequently accessed content
- Use GET endpoints for simpler requests

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch
3. Install development dependencies
4. Run tests: `python test_api.py`
5. Submit pull request

### Code Style
- Follow PEP 8 guidelines
- Use type hints where possible
- Add docstrings for functions
- Include error handling

## 📝 License

This project is open source and available under the MIT License.

## 🔗 Links

- **Web Interface**: http://localhost:5000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **OpenAPI Spec**: http://localhost:8000/openapi.json

## 📞 Support

For issues, questions, or feature requests, please contact the development team or create an issue in the project repository.