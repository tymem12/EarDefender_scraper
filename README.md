# EarDefender_scraper

## Local run

1. Build Docker image
```
docker build -t fastapi-scraper-app .
```

2. Run Docker container
```
docker run -p 8000:8000 --shm-size=2g fastapi-scraper-app
```