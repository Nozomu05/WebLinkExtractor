# URL Content Extractor

A powerful web application built with Streamlit that extracts and organizes webpage content while preserving the original structure and hierarchy. The application supports text extraction, image extraction, and video extraction with an intuitive tabbed interface.

## Features

- **Text Content Extraction**: Clean text extraction while preserving webpage structure and hierarchy
- **Image Extraction**: Extract and display all images from webpages in a dedicated Pictures tab
- **Video Extraction**: Detect and extract HTML5 videos, embedded content, and iframes in a Videos tab
- **Tabbed Interface**: Organized display with separate tabs for Text, Pictures, and Videos
- **FAQ Support**: Specialized extraction and formatting for FAQ sections
- **Export Options**: Download extracted content as Markdown or plain text
- **Responsive Design**: Clean, modern interface with gradient backgrounds and metrics display
- **REST API**: Complete API interface for programmatic access and integration with other applications

## Technology Stack

- **Backend**: Python 3.11
- **Web Framework**: Streamlit 1.46.0+
- **API Framework**: FastAPI with Uvicorn
- **Content Extraction**: Trafilatura 2.0.0+, BeautifulSoup4
- **Text Processing**: NLTK 3.9.1+
- **HTTP Requests**: Requests 2.32.4+
- **Deployment**: Linux server with Nginx (optional) and systemd

## API Documentation

The URL Content Extractor provides a complete REST API for programmatic access to content extraction functionality.

### API Endpoints

**Base URL**: `http://localhost:8000` (development) or `https://your-domain.com` (production)

#### Health Check
```http
GET /health
```
Returns API health status.

#### Extract Content (POST)
```http
POST /extract
Content-Type: application/json

{
    "url": "https://example.com",
    "include_images": true,
    "include_videos": false
}
```

#### Extract Content (GET)
```http
GET /extract?url=https://example.com&include_images=true&include_videos=false
```

#### Specialized Endpoints
- `POST /extract/text-only` - Extract only text content
- `POST /extract/with-images` - Extract text and images
- `POST /extract/with-videos` - Extract text and videos  
- `POST /extract/full` - Extract all content types

### API Response Format
```json
{
    "success": true,
    "url": "https://example.com",
    "content": {
        "text": ["Section 1", "Section 2"],
        "images": ["![alt](url1)", "![alt](url2)"],
        "videos": ["**[VIDEO: title]**\nURL: url"]
    },
    "stats": {
        "total_characters": 1500,
        "word_count": 250,
        "text_sections": 5,
        "image_count": 3,
        "video_count": 1
    },
    "message": "Content extracted successfully"
}
```

### Interactive API Documentation
When the API server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### API Usage Examples

#### Python Example
```python
import requests

# Extract text and images
response = requests.post("http://localhost:8000/extract", json={
    "url": "https://example.com",
    "include_images": True,
    "include_videos": False
})

if response.status_code == 200:
    data = response.json()
    print(f"Extracted {data['stats']['text_sections']} text sections")
    print(f"Found {data['stats']['image_count']} images")
else:
    print(f"Error: {response.text}")
```

#### JavaScript Example
```javascript
fetch('http://localhost:8000/extract', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        url: 'https://example.com',
        include_images: true,
        include_videos: false
    })
})
.then(response => response.json())
.then(data => {
    console.log('Extraction successful:', data.stats);
    console.log('Text sections:', data.content.text.length);
})
.catch(error => console.error('Error:', error));
```

#### cURL Example
```bash
curl -X POST "http://localhost:8000/extract" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://example.com",
       "include_images": true,
       "include_videos": false
     }'
```

## Quick Start

### Prerequisites

- Linux server (Ubuntu 20.04+ or CentOS 8+ recommended)
- Python 3.11 or higher
- 2GB RAM minimum, 4GB recommended
- 10GB disk space

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd url-content-extractor
```

2. **Install Python dependencies**
```bash
# Install Python 3.11 if not available
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

3. **Create requirements.txt** (if not present)
```bash
cat > requirements.txt << EOF
streamlit>=1.46.0
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
python-multipart>=0.0.6
trafilatura>=2.0.0
beautifulsoup4>=4.12.0
nltk>=3.9.1
requests>=2.32.4
EOF
```

4. **Download NLTK data**
```bash
python -c "
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
"
```

5. **Test the applications**
```bash
# Test Streamlit web interface
streamlit run app.py --server.port 8501

# Test API server (in another terminal)
python api.py

# Test API endpoints
python test_api.py
```

## Production Deployment

### Method 1: Systemd Service (Recommended)

This method deploys both the Streamlit web interface and the FastAPI server.

1. **Create application user**
```bash
sudo useradd -r -s /bin/false -d /opt/url-extractor streamlit-app
sudo mkdir -p /opt/url-extractor
sudo chown streamlit-app:streamlit-app /opt/url-extractor
```

2. **Install application**
```bash
# Copy files to production directory
sudo cp -r . /opt/url-extractor/
sudo chown -R streamlit-app:streamlit-app /opt/url-extractor

# Create virtual environment in production
sudo -u streamlit-app python3.11 -m venv /opt/url-extractor/venv
sudo -u streamlit-app /opt/url-extractor/venv/bin/pip install -r /opt/url-extractor/requirements.txt

# Download NLTK data for production user
sudo -u streamlit-app /opt/url-extractor/venv/bin/python -c "
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
"
```

3. **Create Streamlit configuration**
```bash
sudo mkdir -p /opt/url-extractor/.streamlit
sudo tee /opt/url-extractor/.streamlit/config.toml << EOF
[server]
headless = true
address = "0.0.0.0"
port = 8501
enableCORS = false
enableXsrfProtection = false

[theme]
base = "light"
EOF

sudo chown -R streamlit-app:streamlit-app /opt/url-extractor/.streamlit
```

4. **Create systemd services**
```bash
# Streamlit web interface service
sudo tee /etc/systemd/system/url-extractor-web.service << EOF
[Unit]
Description=URL Content Extractor Streamlit Web Interface
After=network.target

[Service]
Type=exec
User=streamlit-app
Group=streamlit-app
WorkingDirectory=/opt/url-extractor
Environment=PATH=/opt/url-extractor/venv/bin
ExecStart=/opt/url-extractor/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=3

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/opt/url-extractor
ProtectHome=true

[Install]
WantedBy=multi-user.target
EOF

# FastAPI server service
sudo tee /etc/systemd/system/url-extractor-api.service << EOF
[Unit]
Description=URL Content Extractor FastAPI Server
After=network.target

[Service]
Type=exec
User=streamlit-app
Group=streamlit-app
WorkingDirectory=/opt/url-extractor
Environment=PATH=/opt/url-extractor/venv/bin
ExecStart=/opt/url-extractor/venv/bin/python api.py
Restart=always
RestartSec=3

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/opt/url-extractor
ProtectHome=true

[Install]
WantedBy=multi-user.target
EOF
```

5. **Start and enable services**
```bash
sudo systemctl daemon-reload

# Enable and start both services
sudo systemctl enable url-extractor-web url-extractor-api
sudo systemctl start url-extractor-web url-extractor-api

# Check status
sudo systemctl status url-extractor-web
sudo systemctl status url-extractor-api
```

### Method 2: Nginx Reverse Proxy (Optional)

1. **Install Nginx**
```bash
sudo apt update
sudo apt install nginx
```

2. **Configure Nginx**
```bash
sudo tee /etc/nginx/sites-available/url-extractor << EOF
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain or IP

    # Web interface (Streamlit)
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        proxy_read_timeout 86400;
    }
    
    # API endpoints
    location /api/ {
        rewrite ^/api/(.*) /\$1 break;
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/url-extractor /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

3. **Configure firewall**
```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

### Method 3: Docker Deployment

1. **Create Dockerfile**
```bash
cat > Dockerfile << EOF
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger')"

# Copy application files
COPY . .

# Create Streamlit config
RUN mkdir -p .streamlit
COPY .streamlit/config.toml .streamlit/

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
EOF
```

2. **Build and run Docker container**
```bash
# Build image
docker build -t url-extractor .

# Run container
docker run -d \
  --name url-extractor \
  --restart unless-stopped \
  -p 8501:8501 \
  url-extractor

# Check logs
docker logs url-extractor
```

## SSL/HTTPS Setup (Recommended for Production)

### Using Certbot (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Verify auto-renewal
sudo certbot renew --dry-run
```

## Monitoring and Maintenance

### View Application Logs
```bash
# Web interface logs
sudo journalctl -u url-extractor-web -f

# API server logs
sudo journalctl -u url-extractor-api -f

# Application-specific logs
sudo tail -f /opt/url-extractor/logs/app.log
```

### Performance Monitoring
```bash
# Check system resources
htop
df -h
free -m

# Check service status
sudo systemctl status url-extractor-web url-extractor-api nginx
```

### Backup Strategy
```bash
# Create backup script
sudo tee /opt/backup-url-extractor.sh << EOF
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf /backup/url-extractor-\$DATE.tar.gz /opt/url-extractor
find /backup -name "url-extractor-*.tar.gz" -mtime +7 -delete
EOF

sudo chmod +x /opt/backup-url-extractor.sh

# Add to crontab for daily backups
echo "0 2 * * * /opt/backup-url-extractor.sh" | sudo crontab -
```

## Troubleshooting

### Common Issues

1. **Services won't start**
```bash
# Check web interface
sudo journalctl -u url-extractor-web --no-pager
sudo systemctl status url-extractor-web

# Check API server
sudo journalctl -u url-extractor-api --no-pager
sudo systemctl status url-extractor-api
```

2. **Permission denied errors**
```bash
sudo chown -R streamlit-app:streamlit-app /opt/url-extractor
sudo chmod +x /opt/url-extractor/app.py
```

3. **NLTK data missing**
```bash
sudo -u streamlit-app /opt/url-extractor/venv/bin/python -c "
import nltk
nltk.download('punkt', force=True)
nltk.download('stopwords', force=True)
nltk.download('averaged_perceptron_tagger', force=True)
"
```

4. **Memory issues**
```bash
# Check memory usage
free -m
# Restart services if needed
sudo systemctl restart url-extractor-web url-extractor-api
```

### Log Locations
- **Web interface logs**: `sudo journalctl -u url-extractor-web`
- **API server logs**: `sudo journalctl -u url-extractor-api`
- **Nginx logs**: `/var/log/nginx/access.log` and `/var/log/nginx/error.log`
- **System logs**: `/var/log/syslog`

## Configuration

### Environment Variables
```bash
# Optional: Set in /opt/url-extractor/.env
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
```

### Streamlit Configuration
Edit `/opt/url-extractor/.streamlit/config.toml`:
```toml
[server]
headless = true
address = "0.0.0.0"
port = 8501
maxUploadSize = 200

[theme]
base = "light"
primaryColor = "#ff6b6b"
```

## Security Considerations

1. **Firewall Configuration**
```bash
sudo ufw deny 8501  # Block direct access to Streamlit
sudo ufw allow 'Nginx Full'
```

2. **Regular Updates**
```bash
sudo apt update && sudo apt upgrade
pip install --upgrade -r requirements.txt
```

3. **Log Monitoring**
```bash
# Monitor for suspicious activity
sudo tail -f /var/log/nginx/access.log | grep -E "(POST|PUT|DELETE)"
```

## Support

For issues and questions:
- Check the troubleshooting section above
- Review application logs
- Ensure all dependencies are properly installed
- Verify network connectivity and firewall settings

## License

This project is open source. Please check the license file for details.