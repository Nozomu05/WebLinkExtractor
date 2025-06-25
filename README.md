# URL Content Extractor

A Streamlit web application that extracts and organizes webpage content into logical topic groups. The application scrapes web content from user-provided URLs, processes the text using natural language processing techniques, and presents organized content through an intuitive web interface.

## Features

- **Web Content Extraction**: Uses Trafilatura for robust content extraction from any URL
- **Structured Output**: Preserves original webpage hierarchy and organization
- **FAQ Processing**: Special handling for FAQ sections with proper question-answer pairing
- **Media Filtering**: Automatically removes images, videos, and other media content
- **Vietnamese Support**: Full support for Vietnamese text processing and display
- **Real-time Processing**: Live extraction and display of webpage content

## System Requirements

- Linux server (Ubuntu 18.04+ recommended)
- Python 3.8 or higher
- 2GB RAM minimum
- Internet connection for content extraction

## Installation

### 1. System Dependencies

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install system dependencies for web scraping
sudo apt install curl wget git -y
```

### 2. Clone and Setup Project

```bash
# Clone the repository
git clone <your-repository-url>
cd url-content-extractor

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Required Python Packages

If `requirements.txt` doesn't exist, install packages manually:

```bash
pip install streamlit beautifulsoup4 nltk requests trafilatura
```

### 4. Download NLTK Data

```bash
python3 -c "
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
"
```

## Configuration

### 1. Streamlit Configuration

The application includes a `.streamlit/config.toml` file with optimal server settings:

```toml
[server]
headless = true
address = "0.0.0.0"
port = 5000
```

### 2. Environment Variables (Optional)

```bash
# Set environment variables for production
export STREAMLIT_SERVER_PORT=5000
export STREAMLIT_SERVER_ADDRESS="0.0.0.0"
export STREAMLIT_SERVER_HEADLESS=true
```

## Deployment Options

### Option 1: Direct Python Execution

```bash
# Navigate to project directory
cd /path/to/url-content-extractor

# Activate virtual environment
source venv/bin/activate

# Run the application
streamlit run app.py --server.port 5000 --server.address 0.0.0.0
```

### Option 2: systemd Service (Recommended)

Create a systemd service for automatic startup and management:

```bash
# Create service file
sudo nano /etc/systemd/system/url-extractor.service
```

Add the following content:

```ini
[Unit]
Description=URL Content Extractor
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/url-content-extractor
Environment=PATH=/path/to/url-content-extractor/venv/bin
ExecStart=/path/to/url-content-extractor/venv/bin/streamlit run app.py --server.port 5000 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable url-extractor

# Start service
sudo systemctl start url-extractor

# Check status
sudo systemctl status url-extractor
```

### Option 3: Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

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

# Expose port
EXPOSE 5000

# Run application
CMD ["streamlit", "run", "app.py", "--server.port", "5000", "--server.address", "0.0.0.0"]
```

Build and run:

```bash
# Build image
docker build -t url-extractor .

# Run container
docker run -d -p 5000:5000 --name url-extractor url-extractor
```

## Reverse Proxy Setup (Nginx)

For production deployment, use Nginx as a reverse proxy:

```bash
# Install Nginx
sudo apt install nginx -y

# Create site configuration
sudo nano /etc/nginx/sites-available/url-extractor
```

Add configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support for Streamlit
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Enable the site:

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/url-extractor /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

## SSL Certificate (Optional)

Install SSL certificate using Let's Encrypt:

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d your-domain.com
```

## Firewall Configuration

```bash
# Allow HTTP and HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Allow SSH (if needed)
sudo ufw allow 22

# Enable firewall
sudo ufw enable
```

## Monitoring and Logs

### Check Application Logs

```bash
# systemd service logs
sudo journalctl -u url-extractor -f

# Docker logs
docker logs -f url-extractor
```

### Monitor System Resources

```bash
# Check memory usage
free -h

# Check disk usage
df -h

# Check running processes
ps aux | grep streamlit
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using port 5000
   sudo lsof -i :5000
   
   # Kill process if needed
   sudo kill -9 <PID>
   ```

2. **Permission Denied**
   ```bash
   # Fix file permissions
   sudo chown -R www-data:www-data /path/to/url-content-extractor
   ```

3. **NLTK Data Missing**
   ```bash
   # Re-download NLTK data
   python3 -c "import nltk; nltk.download('all')"
   ```

4. **Memory Issues**
   ```bash
   # Add swap space
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

### Performance Optimization

1. **Increase worker processes** (for high traffic):
   ```bash
   # Edit systemd service to use multiple workers
   ExecStart=/path/to/venv/bin/streamlit run app.py --server.port 5000 --server.address 0.0.0.0 --server.maxUploadSize 200
   ```

2. **Enable caching**:
   Add to `.streamlit/config.toml`:
   ```toml
   [global]
   developmentMode = false
   
   [server]
   enableCORS = false
   enableXsrfProtection = true
   ```

## Maintenance

### Regular Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Python packages
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Restart service
sudo systemctl restart url-extractor
```

### Backup

```bash
# Backup application files
tar -czf url-extractor-backup-$(date +%Y%m%d).tar.gz /path/to/url-content-extractor
```

## Security Considerations

1. **Run as non-root user**
2. **Keep dependencies updated**
3. **Use HTTPS in production**
4. **Configure proper firewall rules**
5. **Regular security updates**
6. **Monitor application logs**

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review application logs
3. Ensure all dependencies are installed
4. Verify network connectivity for web scraping

## License

This project is provided as-is for educational and development purposes.