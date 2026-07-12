import asyncio
from curl_cffi import requests
from bs4 import BeautifulSoup
from models import JobListing
from pydantic import ValidationError
from database import init_db, save_job_to_db

async def scrape_totaljobs(query, headed=False):
    print(f"Starting Totaljobs scraper (Stealth Mode) for query: '{query}'...")
    
    # We ignore the 'headed' flag since we are completely bypassing the browser
    # using curl_cffi to perfectly mimic Google Chrome's TLS fingerprint.
    
    formatted_query = query.replace(" ", "-")
    url = f"https://www.totaljobs.com/jobs/{formatted_query}"
    
    try:
        # We use asyncio.to_thread because curl_cffi.requests is synchronous
        response = await asyncio.to_thread(
            requests.get,
            url,
            impersonate="chrome110",
            timeout=15
        )
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        jobs_data = []
        
        # StepStone network uses <article> tags or specific data-test-ids
        articles = soup.find_all("article")
        if not articles:
            # Fallback for dynamic rendering if article tags aren't present
            articles = soup.find_all("div", class_=lambda c: c and "job-card" in c.lower())
            
        for article in articles:
            title_tag = article.find("h2") or article.find("a")
            job_title = title_tag.text.strip() if title_tag else ""
            
            job_url = ""
            if title_tag and title_tag.name == "a":
                job_url = title_tag.get("href", "")
            elif title_tag:
                link = title_tag.find("a")
                job_url = link.get("href", "") if link else ""
                
            if job_url and not job_url.startswith("http"):
                job_url = "https://www.totaljobs.com" + job_url
                
            company_tag = article.find("li", class_=lambda c: c and "company" in c.lower()) or article.find("span", attrs={"data-at": "job-item-company-name"})
            company = company_tag.text.strip() if company_tag else ""
            
            snippet_tag = article.find("div", class_=lambda c: c and "snippet" in c.lower())
            snippet = snippet_tag.text.strip() if snippet_tag else ""
            
            if job_title:
                try:
                    job_model = JobListing(
                        title=job_title or "Unknown Title",
                        company=company or "Unknown Company",
                        location="",
                        salary="",
                        deadline="",
                        url=job_url or "https://totaljobs.com",
                        description=snippet
                    )
                    jobs_data.append(job_model.to_dict())
                except ValidationError as e:
                    print(f"Validation error for job: {e}")
                    
        print(f"Found {len(jobs_data)} jobs via Totaljobs stealth requests.")
        
        init_db()
        for job in jobs_data:
            save_job_to_db(job, "totaljobs")
        print(f"Saved {len(jobs_data)} jobs to database.")
        
    except Exception as e:
        print(f"Error scraping Totaljobs: {e}")
