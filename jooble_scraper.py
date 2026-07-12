from models import JobListing
from pydantic import ValidationError
import os
from datetime import datetime
import asyncio
import pandas as pd
import requests
import json
import sys

async def scrape_jooble(
    search_query="graduate data analyst", 
    location="UK", 
    radius=80, 
    salary=None,
    page=1,
    result_on_page=100,
    company_search=False,
    headless=True
):
    api_key = 'f51b8bbe-8cf9-48ff-8fd7-9101ba1ffe91'
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
    
    print(f"Making API request to Jooble for query: '{search_query}'...")
    
    try:
        response = requests.post(api_url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Jooble API: {e}")
        return
        
    jobs = data.get("jobs", [])
    if not jobs:
        print("No jobs found via API.")
        return
        
    print(f"Found {len(jobs)} jobs via Jooble API.")
    
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
            print(f"Validation error for job: {e}")
        
    df = pd.DataFrame(jobs_data)
    df.to_csv("jooble_data.csv", index=False)
    print("Saved Jooble API data to jooble_data.csv.")

if __name__ == "__main__":
    asyncio.run(scrape_jooble())

