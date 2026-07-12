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
        jobs_data.append({
            "Job Title": job.get("jobTitle", ""),
            "Company": job.get("employerName", ""),
            "Location": job.get("locationName", ""),
            "Salary": f"£{job.get('minimumSalary', '')} - £{job.get('maximumSalary', '')}",
            "Deadline": job.get("expirationDate", ""),
            "URL": job.get("jobUrl", ""),
            "Description": job.get("jobDescription", "")
        })
        
    df = pd.DataFrame(jobs_data)
    df.to_csv("reed_data.csv", index=False)
    print("Saved Reed API data to reed_data.csv.")

if __name__ == "__main__":
    asyncio.run(scrape_reed())
