import os
import json
import logging
import requests
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from database import init_db, bulk_upsert_jobs
from models import JobListing
from pydantic import ValidationError

logger = logging.getLogger(__name__)

@retry(
    wait=wait_exponential(multiplier=1, max=30),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(requests.exceptions.RequestException)
)
def fetch_jooble_jobs(api_url, payload, headers):
    response = requests.post(api_url, data=json.dumps(payload), headers=headers)
    response.raise_for_status()
    return response.json()

def scrape_jooble(
    search_query="graduate data analyst", 
    location="UK", 
    radius=80, 
    salary=None,
    page=1,
    result_on_page=100,
    company_search=False
):
    api_key = os.environ.get("JOOBLE_API_KEY", "f51b8bbe-8cf9-48ff-8fd7-9101ba1ffe91")
    api_url = f'https://jooble.org/api/{api_key}'
    
    payload = {
        "keywords": search_query,
        "location": location,
        "radius": str(radius),
        "page": str(page),
        "ResultOnPage": result_on_page,
        "companysearch": company_search
    }
    
    if salary is not None:
        payload["salary"] = salary
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    logger.info(f"Making API request to Jooble for query: '{search_query}'...")
    
    try:
        data = fetch_jooble_jobs(api_url, payload, headers)
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data from Jooble API after retries: {e}")
        return
        
    jobs = data.get("jobs", [])
    if not jobs:
        logger.info("No jobs found via API.")
        return
        
    logger.info(f"Found {len(jobs)} jobs via Jooble API.")
    
    jobs_data = []
    for job in jobs:
        try:
            job_model = JobListing(
                title=job.get("title", "Unknown Title"),
                company=job.get("company", "Unknown Company"),
                location=job.get("location", ""),
                salary=job.get("salary", ""),
                deadline="",
                url=job.get("link", "https://jooble.org"),
                description=job.get("snippet", "")
            )
            jobs_data.append(job_model.to_dict())
        except ValidationError as e:
            logger.warning(f"Validation error for job: {e}")
        
    init_db()
    bulk_upsert_jobs(jobs_data, "jooble")

if __name__ == "__main__":
    scrape_jooble()
