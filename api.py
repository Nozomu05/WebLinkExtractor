from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, List, Any
import uvicorn
from complete_data_extractor import extract_all_webpage_data
from depth_scraper import scrape_with_depth
import re
from urllib.parse import urlparse

# Initialize FastAPI app
app = FastAPI(
    title="URL Content Extractor API",
    description="Extract and organize webpage content with support for text, images, and videos",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for web applications
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class ExtractionRequest(BaseModel):
    url: HttpUrl
    include_images: bool = False
    include_videos: bool = False
    
class DepthExtractionRequest(BaseModel):
    url: HttpUrl
    include_images: bool = False
    include_videos: bool = False
    depth: int = 1
    max_pages: int = 10
    delay: float = 1.0

class ExtractionResponse(BaseModel):
    success: bool
    url: str
    content: Dict[str, Any]
    stats: Dict[str, int]
    message: Optional[str] = None

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Optional[str] = None

# Helper functions
def is_valid_url(url: str) -> bool:
    """Validate URL format"""
    try:
        result = urlparse(str(url))
        return all([result.scheme, result.netloc])
    except:
        return False

def separate_content_types(content: str) -> Dict[str, List[str]]:
    """Separate content into text, images, and videos"""
    # Extract all images from the entire content first
    all_images = re.findall(r'!\[.*?\]\([^)]+\)', content)
    
    # Remove images from content and split into sections
    text_only_content = content
    for img in all_images:
        text_only_content = text_only_content.replace(img, '')
    
    sections = text_only_content.split('\n\n')
    text_content = []
    video_content = []
    
    for section in sections:
        section = section.strip()
        if not section:
            continue
            
        # Check for video content
        if section.startswith('**[') and ('VIDEO:' in section or 'AUDIO:' in section or 'EMBEDDED' in section):
            video_content.append(section)
        else:
            text_content.append(section)
    
    return {
        'text': text_content,
        'images': all_images,
        'videos': video_content
    }

def calculate_stats(content_dict: Dict[str, List[str]]) -> Dict[str, int]:
    """Calculate content statistics"""
    all_text = '\n\n'.join(content_dict['text'])
    return {
        'total_characters': len(all_text),
        'word_count': len(all_text.split()),
        'text_sections': len(content_dict['text']),
        'image_count': len(content_dict['images']),
        'video_count': len(content_dict['videos'])
    }

# API Endpoints
@app.get("/", response_model=Dict[str, str])
async def root():
    """API root endpoint with basic information"""
    return {
        "message": "URL Content Extractor API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=Dict[str, str])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "url-content-extractor"}

@app.post("/extract", response_model=ExtractionResponse)
async def extract_content(request: ExtractionRequest):
    """
    Extract content from a webpage
    
    - **url**: The webpage URL to extract content from
    - **include_images**: Whether to include images in extraction (default: false)
    - **include_videos**: Whether to include videos in extraction (default: false)
    """
    try:
        # Validate URL
        if not is_valid_url(str(request.url)):
            raise HTTPException(status_code=400, detail="Invalid URL format")
        
        # Extract content
        raw_content = extract_all_webpage_data(
            str(request.url), 
            include_images=request.include_images, 
            include_videos=request.include_videos
        )
        
        # Check if extraction was successful
        if not raw_content or len(raw_content.strip()) < 50:
            raise HTTPException(
                status_code=422, 
                detail="Unable to extract meaningful content from this URL"
            )
        
        # Separate content types
        content_dict = separate_content_types(raw_content)
        
        # Calculate statistics
        stats = calculate_stats(content_dict)
        
        return ExtractionResponse(
            success=True,
            url=str(request.url),
            content=content_dict,
            stats=stats,
            message="Content extracted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting content: {str(e)}")

@app.get("/extract", response_model=ExtractionResponse)
async def extract_content_get(
    url: str = Query(..., description="The webpage URL to extract content from"),
    include_images: bool = Query(False, description="Include images in extraction"),
    include_videos: bool = Query(False, description="Include videos in extraction")
):
    """
    Extract content from a webpage using GET method
    
    Query parameters:
    - **url**: The webpage URL to extract content from
    - **include_images**: Whether to include images in extraction (default: false)
    - **include_videos**: Whether to include videos in extraction (default: false)
    """
    # Convert to POST request format
    request = ExtractionRequest(
        url=url,
        include_images=include_images,
        include_videos=include_videos
    )
    return await extract_content(request)

@app.post("/extract/text-only", response_model=ExtractionResponse)
async def extract_text_only(url: HttpUrl):
    """Extract only text content from a webpage"""
    request = ExtractionRequest(url=url, include_images=False, include_videos=False)
    return await extract_content(request)

@app.post("/extract/with-images", response_model=ExtractionResponse)
async def extract_with_images(url: HttpUrl):
    """Extract text and images from a webpage"""
    request = ExtractionRequest(url=url, include_images=True, include_videos=False)
    return await extract_content(request)

@app.post("/extract/with-videos", response_model=ExtractionResponse)
async def extract_with_videos(url: HttpUrl):
    """Extract text and videos from a webpage"""
    request = ExtractionRequest(url=url, include_images=False, include_videos=True)
    return await extract_content(request)

@app.post("/extract/full", response_model=ExtractionResponse)
async def extract_full_content(url: HttpUrl):
    """Extract all content types (text, images, and videos) from a webpage"""
    request = ExtractionRequest(url=url, include_images=True, include_videos=True)
    return await extract_content(request)

@app.post("/extract/depth", response_model=Dict[str, Any])
async def extract_with_depth(request: DepthExtractionRequest):
    """
    Extract content from a webpage with depth scraping
    
    - **url**: The webpage URL to start extraction from
    - **include_images**: Whether to include images in extraction (default: false)
    - **include_videos**: Whether to include videos in extraction (default: false)
    - **depth**: Maximum depth to scrape (1-3, default: 1)
    - **max_pages**: Maximum number of pages to scrape (5-50, default: 10)
    - **delay**: Delay between requests in seconds (0.5-3.0, default: 1.0)
    """
    try:
        # Validate parameters
        if not is_valid_url(str(request.url)):
            raise HTTPException(status_code=400, detail="Invalid URL format")
        
        if not (1 <= request.depth <= 3):
            raise HTTPException(status_code=400, detail="Depth must be between 1 and 3")
            
        if not (5 <= request.max_pages <= 50):
            raise HTTPException(status_code=400, detail="Max pages must be between 5 and 50")
            
        if not (0.5 <= request.delay <= 3.0):
            raise HTTPException(status_code=400, detail="Delay must be between 0.5 and 3.0 seconds")
        
        # Extract content with depth
        formatted_content = scrape_with_depth(
            str(request.url),
            depth=request.depth,
            include_images=request.include_images,
            include_videos=request.include_videos,
            delay=request.delay,
            max_pages=request.max_pages
        )
        
        # Check if extraction was successful
        if not formatted_content or len(formatted_content.strip()) < 100:
            raise HTTPException(
                status_code=422, 
                detail="Unable to extract meaningful content from this URL"
            )
        
        # Calculate basic statistics
        word_count = len(formatted_content.split())
        character_count = len(formatted_content)
        
        return {
            "success": True,
            "url": str(request.url),
            "depth": request.depth,
            "max_pages": request.max_pages,
            "content": formatted_content,
            "stats": {
                "total_characters": character_count,
                "word_count": word_count,
                "extraction_type": "depth_scraping"
            },
            "message": f"Depth extraction completed (depth: {request.depth}, max pages: {request.max_pages})"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in depth extraction: {str(e)}")

@app.get("/extract/depth", response_model=Dict[str, Any])
async def extract_with_depth_get(
    url: str = Query(..., description="The webpage URL to start extraction from"),
    include_images: bool = Query(False, description="Include images in extraction"),
    include_videos: bool = Query(False, description="Include videos in extraction"),
    depth: int = Query(1, description="Maximum depth to scrape (1-3)"),
    max_pages: int = Query(10, description="Maximum pages to scrape (5-50)"),
    delay: float = Query(1.0, description="Delay between requests (0.5-3.0 seconds)")
):
    """
    Extract content with depth scraping using GET method
    
    Query parameters:
    - **url**: The webpage URL to start extraction from
    - **include_images**: Whether to include images in extraction (default: false)
    - **include_videos**: Whether to include videos in extraction (default: false)
    - **depth**: Maximum depth to scrape (1-3, default: 1)
    - **max_pages**: Maximum pages to scrape (5-50, default: 10)
    - **delay**: Delay between requests (0.5-3.0 seconds, default: 1.0)
    """
    # Convert to POST request format
    request = DepthExtractionRequest(
        url=url,
        include_images=include_images,
        include_videos=include_videos,
        depth=depth,
        max_pages=max_pages,
        delay=delay
    )
    return await extract_with_depth(request)

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "success": False,
        "error": exc.detail,
        "status_code": exc.status_code
    }

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return {
        "success": False,
        "error": "Internal server error",
        "details": str(exc)
    }

if __name__ == "__main__":
    uvicorn.run(
        "api:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )