import logging
from database import init_db, bulk_upsert_jobs
import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from utils import export_jobs_to_csv

logger = logging.getLogger(__name__)

async def scrape_targetjobs(search_query="data", headless=True, export_csv=False):
    url = f"https://targetjobs.co.uk/search/jobs?search={search_query}"
    
    jobs_data = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        page = await browser.new_page()
        
        logger.info(f"Navigating to {url}...")
        await page.goto(url, wait_until='networkidle')
        
        logger.info("Waiting for results to render...")
        try:
            await page.wait_for_selector('a[href^="/jobs/"]', timeout=10000)
        except Exception as e:
            logger.warning(f"Could not find job links, maybe no results or different selector: {e}")
        
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        job_links = soup.find_all('a', href=True)
        job_cards = [a for a in job_links if '/jobs/' in a['href'] and a.find('h3') or a.find('h2')]
        
        if not job_cards:
            logger.error("Could not find job cards with heuristic.")
            await browser.close()
            return
            
        logger.info(f"Found {len(job_cards)} potential job listings on the first page.")
        
        for card in job_cards:
            title_elem = card.find(['h3', 'h2'])
            job_title = title_elem.get_text(strip=True) if title_elem else ""
            
            # Use specific classes or data attributes to prevent layout breakages
            # But since TargetJobs uses styled divs without specific classes, we'll try a safer text approach
            text_chunks = [t for t in card.stripped_strings if len(t) > 1 and t.lower() not in ['save', 'spotlight']]
            
            company, location, salary, deadline = "", "", "", ""
            
            if text_chunks:
                company = text_chunks[0] if text_chunks else ""
                
                for chunk in text_chunks:
                    if '£' in chunk:
                        salary = chunk
                    elif 'apply' in chunk.lower() or 'days' in chunk.lower() or 'closes' in chunk.lower():
                        deadline = chunk
                        
                used_chunks = {company, job_title, salary, deadline}
                remaining = [c for c in text_chunks if c not in used_chunks]
                if remaining:
                    location = remaining[0]

            job_url = "https://targetjobs.co.uk" + card['href'] if card['href'].startswith('/') else card['href']
            
            jobs_data.append({
                "Job Title": job_title,
                "Company": company,
                "Location": location,
                "Salary": salary,
                "Deadline": deadline,
                "URL": job_url,
                "Description": ""
            })

        logger.info("Fetching job descriptions for each listing...")
        for i, job in enumerate(jobs_data):
            logger.info(f"[{i+1}/{len(jobs_data)}] Fetching description for {job['Job Title']} at {job['Company']}...")
            try:
                await page.goto(job['URL'], wait_until='domcontentloaded', timeout=15000)
                await page.wait_for_timeout(1000)
                
                job_html = await page.content()
                job_soup = BeautifulSoup(job_html, 'html.parser')
                
                main_content = job_soup.find('main')
                if main_content:
                    paragraphs = main_content.find_all('p')
                    if paragraphs:
                        description = "\n\n".join([p.get_text(strip=True) for p in paragraphs])
                    else:
                        description = main_content.get_text(separator="\n", strip=True)
                else:
                    description = job_soup.get_text(separator="\n", strip=True)
                    
                job['Description'] = description
            except Exception as e:
                logger.error(f"Failed to fetch {job['URL']}: {e}")
                job['Description'] = f"Error: {e}"
        
        await browser.close()
        
    init_db()
    bulk_upsert_jobs(jobs_data, "targetjobs")
    if export_csv:
        export_jobs_to_csv(jobs_data, "targetjobs")

if __name__ == "__main__":
    asyncio.run(scrape_targetjobs())
