# EarDefender scraper

The scraper module in EarDefender is responsible for automatically retrieving audio files from websites, including both main pages and linked subpages. It uses advanced libraries like Selenium and yt-dlp to navigate websites and download audio content for analysis. Optimized for efficiency, the scraper ensures fast and reliable data collection, handling both static and dynamic web content. By automating the extraction process, it eliminates the need for manual file uploads, streamlining the analysis of large datasets. The module's performance is key to the system's overall speed and scalability, making it suitable for processing audio from various online platforms.

## Local run

1. Build Docker image
```
docker build -t scraper-app .
```

2. Run Docker container
```
docker run -p 8000:8000 --shm-size=2g scraper-app
```