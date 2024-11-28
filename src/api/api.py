from fastapi import FastAPI, HTTPException, BackgroundTasks, Header
from pydantic import BaseModel, Field
from scraper.web_scraper import WebScraper
from typing import Dict, Any, Optional
import logging
import requests
from concurrent.futures import ThreadPoolExecutor
import threading

class InputParams(BaseModel):
    starting_point: str = Field(..., alias='startingPoint')
    max_depth: int = Field(..., alias='maxDepth')
    max_files: int = Field(..., alias='maxFiles')
    max_pages: int = Field(..., alias='maxPages')
    model: str = Field(..., alias='model')
    max_time_per_file: int = Field(..., alias='maxTimePerFile')
    max_total_time: int = Field(..., alias='maxTotalTime')

class ScrapingParams(BaseModel):
    analysis_id: str = Field(..., alias='analysisId')
    input_params: InputParams = Field(..., alias='inputParams')

app = FastAPI()

scraping_results: Dict[str, Dict[str, Any]] = {}

executor = ThreadPoolExecutor(max_workers=1)
executor_lock = threading.Lock()

def perform_scraping(analysis_id: str, params: InputParams, bearer_token: str):
    scraper = WebScraper(
        starting_point=params.starting_point,
        max_depth=params.max_depth,
        max_files=params.max_files,
        max_pages=params.max_pages,
        model=params.model,
        max_time_per_file=params.max_time_per_file,
        max_total_time=params.max_total_time,
        download_dir='./downloads'
    )
    
    files_scraped = scraper.scrape()
    
    headers = {"Authorization": f"Bearer {bearer_token}"}
    try:
        body = {"analysisId": analysis_id, "files": files_scraped}
        logging.info(body)

        response = requests.post(
            'http://host.docker.internal:9090/scraper/report',
            json=body,
            headers=headers,
            timeout=100
        )
        
        if response.status_code == 200:
            logging.info("Successfully sent report data")
        else:
            logging.error(f"Error response: {response.status_code}, Body: {response.text}")
    except requests.RequestException as exc:
        logging.error(f"Request failed: {exc}")
    finally:
        with executor_lock:
            scraping_results[analysis_id]["status"] = "completed"

@app.post("/scraping/start")
async def start_scraping(scraping_params: ScrapingParams, authorization: Optional[str] = Header(None)):
    if scraping_params.analysis_id in scraping_results:
        raise HTTPException(status_code=400, detail="Analysis ID already in use")
    
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
        bearer_token = authorization.split(" ", 1)[1]
    except IndexError:
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")
    
    scraping_results[scraping_params.analysis_id] = {"status": "in_progress"}
    
    executor.submit(perform_scraping, scraping_params.analysis_id, scraping_params.input_params, bearer_token)
    
    return {"analysisId": scraping_params.analysis_id, "message": "Scraping task submitted"}
