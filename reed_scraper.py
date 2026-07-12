import os
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
def fetch_reed_jobs(api_key, params):
    base_url = 'https://www.reed.co.uk/api/1.0/search'
    response = requests.get(base_url, params=params, auth=(api_key, ''))
    response.raise_for_status()
    return response.json()

def scrape_reed(search_query="graduate data analyst"):
    # Read API key from environment variables (fallback to hardcoded for legacy)
    api_key = os.environ.get("REED_API_KEY", "5f27214b-746f-48db-b79c-ce987f4b0a10")

    params = {
        'keywords': search_query,
        'resultsToTake': 100
    }

    logger.info(f"Making API request to Reed for query: '{search_query}'...")
    
    try:
        data = fetch_reed_jobs(api_key, params)
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data from Reed API after retries: {e}")
        return
        
    jobs = data.get("results", [])
    if not jobs:
        logger.info("No jobs found via API.")
        return
        
    logger.info(f"Found {len(jobs)} jobs via Reed API.")
    
    jobs_data = []
    for job in jobs:
        try:
            job_model = JobListing(
                title=job.get("jobTitle", "Unknown Title"),
                company=job.get("employerName", "Unknown Company"),
                location=job.get("locationName", ""),
                salary=f"£{job.get('minimumSalary', '')} - £{job.get('maximumSalary', '')}",
                deadline=job.get("expirationDate", "") or "",
                url=job.get("jobUrl", "https://reed.co.uk"),
                description=job.get("jobDescription", "")
            )
            jobs_data.append(job_model.to_dict())
        except ValidationError as e:
            logger.warning(f"Validation error for job: {e}")
        
    init_db()
    bulk_upsert_jobs(jobs_data, "reed")

if __name__ == "__main__":
    scrape_reed()
