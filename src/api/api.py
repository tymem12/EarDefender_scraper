from fastapi import FastAPI, HTTPException, BackgroundTasks, Header
from pydantic import BaseModel, Field
from scraper.web_scraper import WebScraper
from typing import Dict, Any, Optional
import aiohttp
import logging
import asyncio
from fastapi.concurrency import run_in_threadpool


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


async def perform_scraping(analysis_id: str, params: InputParams, bearer_token: str):
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
    
    try:
        files_scraped = await run_in_threadpool(scraper.scrape)
        scraping_results[analysis_id] = {
            "status": "completed",
        }
    except Exception as e:
        scraping_results[analysis_id] = {
            "status": "failed",
        }
    
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {bearer_token}"}
        try:
            logging.info(files_scraped)
            async with session.post(
                'http://host.docker.internal:9090/scraper/report',
                json={"analysisId": analysis_id, "newFilePaths": files_scraped},
                headers=headers,
                timeout=100
            ) as response:
                if response.status == 200:
                    logging.info("Successfully sent report data")
                else:
                    response_body = await response.text()
                    logging.error(f"Error response: {response.status}, Body: {response_body}")
        except aiohttp.ClientError as exc:
            logging.error(f"Request failed: {exc}")


@app.post("/scraping/start")
async def start_scraping(scraping_params: ScrapingParams, background_tasks: BackgroundTasks, authorization: Optional[str] = Header(None)):
    if scraping_params.analysis_id in scraping_results:
        raise HTTPException(status_code=400, detail="Analysis ID already in use")
    
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
        bearer_token = authorization.split(" ", 1)[1]
    except IndexError:
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")
    
    scraping_results[scraping_params.analysis_id] = {"status": "in_progress"}
    
    background_tasks.add_task(perform_scraping, scraping_params.analysis_id, scraping_params.input_params, bearer_token)
    
    return {"analysisId": scraping_params.analysis_id, "message": "Scraping started"}
