# API Usage Examples

This document provides practical examples for using the URL Content Extractor API in different programming languages.

## Table of Contents
- [Python Examples](#python-examples)
- [JavaScript Examples](#javascript-examples)
- [cURL Examples](#curl-examples)
- [Response Examples](#response-examples)

## Python Examples

### Basic Setup
```python
import requests
import json

# API configuration
BASE_URL = "http://localhost:8000"
headers = {"Content-Type": "application/json"}
```

### Single Page Extraction
```python
def extract_single_page(url, include_images=False, include_videos=False):
    """Extract content from a single webpage"""
    endpoint = f"{BASE_URL}/extract"
    
    payload = {
        "url": url,
        "include_images": include_images,
        "include_videos": include_videos
    }
    
    try:
        response = requests.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        if data["success"]:
            print(f"✅ Extracted {data['stats']['total_characters']} characters")
            print(f"📊 Word count: {data['stats']['word_count']}")
            return data["content"]
        else:
            print(f"❌ Extraction failed: {data.get('error', 'Unknown error')}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

# Usage
content = extract_single_page("https://example.com", include_images=True)
```

### Depth Scraping
```python
def extract_with_depth(url, depth=2, max_pages=10, include_images=False):
    """Extract content with depth scraping"""
    endpoint = f"{BASE_URL}/extract/depth"
    
    payload = {
        "url": url,
        "depth": depth,
        "max_pages": max_pages,
        "delay": 1.0,
        "include_images": include_images,
        "include_videos": False
    }
    
    try:
        response = requests.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        if data["success"]:
            print(f"✅ Depth extraction completed")
            print(f"🌐 Depth: {data['depth']}")
            print(f"📄 Max pages: {data['max_pages']}")
            print(f"📊 Total characters: {data['stats']['total_characters']:,}")
            return data["content"]
        else:
            print(f"❌ Depth extraction failed: {data.get('error', 'Unknown error')}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

# Usage
content = extract_with_depth("https://blog.example.com", depth=2, max_pages=15)
```

### Batch Processing
```python
def batch_extract_urls(urls, output_dir="./extractions"):
    """Extract content from multiple URLs"""
    import os
    
    os.makedirs(output_dir, exist_ok=True)
    results = []
    
    for i, url in enumerate(urls, 1):
        print(f"Processing {i}/{len(urls)}: {url}")
        
        content = extract_single_page(url, include_images=True)
        if content:
            # Save to file
            filename = f"extraction_{i}.json"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    "url": url,
                    "content": content,
                    "extracted_at": str(datetime.now())
                }, f, indent=2, ensure_ascii=False)
            
            results.append({"url": url, "status": "success", "file": filepath})
        else:
            results.append({"url": url, "status": "failed"})
    
    return results

# Usage
urls = [
    "https://example.com/article1",
    "https://example.com/article2",
    "https://news.example.com/story"
]
results = batch_extract_urls(urls)
```

## JavaScript Examples

### Basic Fetch Request
```javascript
const BASE_URL = 'http://localhost:8000';

async function extractSinglePage(url, options = {}) {
    const {
        includeImages = false,
        includeVideos = false
    } = options;
    
    const endpoint = `${BASE_URL}/extract`;
    
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url: url,
                include_images: includeImages,
                include_videos: includeVideos
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            console.log(`✅ Extracted ${data.stats.total_characters} characters`);
            console.log(`📊 Word count: ${data.stats.word_count}`);
            return data.content;
        } else {
            console.error(`❌ Extraction failed: ${data.error}`);
            return null;
        }
        
    } catch (error) {
        console.error(`❌ Request failed: ${error.message}`);
        return null;
    }
}

// Usage
extractSinglePage('https://example.com', { includeImages: true })
    .then(content => {
        if (content) {
            console.log('Content extracted successfully');
            // Process content here
        }
    });
```

### Depth Scraping with Progress
```javascript
async function extractWithDepth(url, options = {}) {
    const {
        depth = 2,
        maxPages = 10,
        includeImages = false,
        includeVideos = false,
        delay = 1.0
    } = options;
    
    const endpoint = `${BASE_URL}/extract/depth`;
    
    console.log(`🚀 Starting depth extraction (depth: ${depth}, max pages: ${maxPages})`);
    
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url: url,
                depth: depth,
                max_pages: maxPages,
                delay: delay,
                include_images: includeImages,
                include_videos: includeVideos
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            console.log(`✅ Depth extraction completed`);
            console.log(`🌐 Depth: ${data.depth}`);
            console.log(`📄 Max pages: ${data.max_pages}`);
            console.log(`📊 Total characters: ${data.stats.total_characters.toLocaleString()}`);
            return data.content;
        } else {
            console.error(`❌ Depth extraction failed: ${data.error}`);
            return null;
        }
        
    } catch (error) {
        console.error(`❌ Request failed: ${error.message}`);
        return null;
    }
}

// Usage with async/await
(async () => {
    const content = await extractWithDepth('https://blog.example.com', {
        depth: 2,
        maxPages: 15,
        includeImages: true
    });
    
    if (content) {
        // Save or process content
        console.log('Depth extraction successful');
    }
})();
```

### Using with Axios
```javascript
const axios = require('axios');

const api = axios.create({
    baseURL: 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json'
    }
});

async function extractContent(url, config = {}) {
    try {
        const response = await api.post('/extract', {
            url: url,
            include_images: config.includeImages || false,
            include_videos: config.includeVideos || false
        });
        
        return response.data;
    } catch (error) {
        if (error.response) {
            console.error('API Error:', error.response.data);
        } else {
            console.error('Network Error:', error.message);
        }
        return null;
    }
}

// Usage
extractContent('https://example.com', { includeImages: true })
    .then(result => {
        if (result && result.success) {
            console.log('Extraction successful:', result.stats);
        }
    });
```

## cURL Examples

### Health Check
```bash
curl -X GET "http://localhost:8000/health" \
     -H "accept: application/json"
```

### Single Page Extraction (GET)
```bash
curl -X GET "http://localhost:8000/extract?url=https%3A//example.com&include_images=false&include_videos=false" \
     -H "accept: application/json"
```

### Single Page Extraction (POST)
```bash
curl -X POST "http://localhost:8000/extract" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://example.com",
       "include_images": false,
       "include_videos": false
     }'
```

### Depth Scraping
```bash
curl -X POST "http://localhost:8000/extract/depth" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://blog.example.com",
       "include_images": true,
       "include_videos": false,
       "depth": 2,
       "max_pages": 15,
       "delay": 1.0
     }'
```

### Full Content Extraction
```bash
curl -X POST "http://localhost:8000/extract/full" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://news.example.com/article"
     }'
```

### Using with jq for JSON Processing
```bash
# Extract and display stats
curl -s -X POST "http://localhost:8000/extract" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com"}' | \
     jq '.stats'

# Extract text content only
curl -s -X POST "http://localhost:8000/extract" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com"}' | \
     jq -r '.content.text[]'
```

## Response Examples

### Successful Single Page Extraction
```json
{
  "success": true,
  "url": "https://example.com",
  "content": {
    "text": [
      "# Example Domain",
      "This domain is for use in illustrative examples in documents.",
      "You may use this domain in literature without prior coordination or asking for permission."
    ],
    "images": [],
    "videos": []
  },
  "stats": {
    "total_characters": 210,
    "word_count": 32,
    "text_sections": 3,
    "image_count": 0,
    "video_count": 0
  },
  "message": "Content extracted successfully"
}
```

### Successful Depth Extraction
```json
{
  "success": true,
  "url": "https://blog.example.com",
  "depth": 2,
  "max_pages": 15,
  "content": "# Depth Scraping Results\n\n**Start URL:** https://blog.example.com\n**Max Depth:** 2\n**Pages Scraped:** 8\n**Total Pages Found:** 12\n\n## Summary Statistics\n- **Total Characters:** 15,240\n- **Total Words:** 2,486\n- **Total Images:** 12\n- **Total Videos:** 3\n\n### Pages by Depth\n- **Depth 0:** 1 pages\n- **Depth 1:** 4 pages\n- **Depth 2:** 3 pages\n\n## Depth 0 Content\n\n### Page 1: https://blog.example.com\n**Scraped at:** 2025-01-01 12:34:56\n**Word Count:** 324\n**Images:** 2 | **Videos:** 1\n\n**Content:**\n# Welcome to Our Blog\n\nThis is the main blog page with links to various articles...\n\n---\n\n## Depth 1 Content\n\n### Page 1: https://blog.example.com/article-1\n...",
  "stats": {
    "total_characters": 15240,
    "word_count": 2486,
    "extraction_type": "depth_scraping"
  },
  "message": "Depth extraction completed (depth: 2, max pages: 15)"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Invalid URL format",
  "details": "URL must include http:// or https://"
}
```

### Validation Error
```json
{
  "detail": [
    {
      "type": "greater_than_equal",
      "loc": ["body", "depth"],
      "msg": "Input should be greater than or equal to 1",
      "input": 0
    }
  ]
}
```

## Best Practices

### Error Handling
```python
def safe_extract(url, retries=3):
    """Extract with retry logic"""
    for attempt in range(retries):
        try:
            content = extract_single_page(url)
            if content:
                return content
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
    
    return None
```

### Rate Limiting
```python
import time
from functools import wraps

def rate_limit(delay=1.0):
    """Decorator to add delay between API calls"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            time.sleep(delay)
            return result
        return wrapper
    return decorator

@rate_limit(delay=1.5)
def extract_with_rate_limit(url):
    return extract_single_page(url)
```

### Content Validation
```python
def validate_extraction(result):
    """Validate extraction result"""
    if not result or not isinstance(result, dict):
        return False
    
    required_fields = ['text', 'images', 'videos']
    return all(field in result for field in required_fields)
```

### Save Results
```python
def save_extraction(url, content, format='json'):
    """Save extraction results to file"""
    import os
    from datetime import datetime
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    domain = url.replace('https://', '').replace('http://', '').split('/')[0]
    
    if format == 'json':
        filename = f"extraction_{domain}_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'url': url,
                'content': content,
                'extracted_at': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
    
    elif format == 'markdown':
        filename = f"extraction_{domain}_{timestamp}.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# Content from {url}\n\n")
            f.write(f"Extracted on: {datetime.now().isoformat()}\n\n")
            
            if isinstance(content, dict) and 'text' in content:
                for section in content['text']:
                    f.write(f"{section}\n\n")
    
    return filename
```

This comprehensive API documentation provides everything needed to integrate the URL Content Extractor into your applications.