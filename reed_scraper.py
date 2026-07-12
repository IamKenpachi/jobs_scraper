from models import JobListing
from pydantic import ValidationError
import os
from datetime import datetime
import asyncio
import pandas as pd
import requests

async def scrape_reed(search_query="graduate data analyst", headless=True):
    api_key = '5f27214b-746f-48db-b79c-ce987f4b0a10'

    base_url = 'https://www.reed.co.uk/api/1.0/search'

    # Search parameters mapping
    params = {
        'keywords': search_query,
        'resultsToTake': 100
    }

    print(f"Making API request to Reed for query: '{search_query}'...")
    
    try:
        # Reed API uses Basic Auth with the API key as the username and an empty password
        response = requests.get(base_url, params=params, auth=(api_key, ''))
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Reed API: {e}")
        return
        
    jobs = data.get("results", [])
    if not jobs:
        print("No jobs found via API.")
        return
        
    print(f"Found {len(jobs)} jobs via Reed API.")
    
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
            print(f"Validation error for job: {e}")
        
    df = pd.DataFrame(jobs_data)
    os.makedirs("output", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"output/reed_{timestamp}.csv"
    df.to_csv(filename, index=False)
    print(f"Saved final data to {filename}.")

if __name__ == "__main__":
    asyncio.run(scrape_reed())
