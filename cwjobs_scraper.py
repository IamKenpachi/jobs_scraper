import logging
from database import init_db, bulk_upsert_jobs
from models import JobListing
from pydantic import ValidationError
import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

logger = logging.getLogger(__name__)

async def scrape_cwjobs(search_query="graduate data analyst", headless=True):
    url = "https://www.cwjobs.co.uk/"
    
    jobs_data = [] # Initialize early to avoid NameError
    
    async with async_playwright() as p:
        # Launching Firefox to bypass some basic bot protections
        browser = await p.firefox.launch(headless=headless)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"
        )
        page = await context.new_page()
        await Stealth().apply_stealth_async(page)
        
        logger.info(f"Navigating to {url}...")
        try:
            await page.goto(url, wait_until='domcontentloaded')
            # Wait for any potential anti-bot checks or cookie banners
            await page.wait_for_timeout(3000)
            
            # Try to accept cookies if the button exists
            try:
                # StepStone usually uses 'ccm-widget' or 'onetrust' for cookies
                await page.click("text=Accept All", timeout=2000)
                await page.wait_for_timeout(1000)
            except Exception:
                pass
                
            logger.info(f"Typing search query '{search_query}'...")
            
            # Locate the search bar. This handles a few common Stepstone/CWJobs IDs
            search_input_selectors = [
                "input[name='keywords']",
                "input[id*='keywords']",
                "input[placeholder*='Job title']",
                "input[type='text']"
            ]
            
            input_found = False
            for selector in search_input_selectors:
                if await page.locator(selector).count() > 0:
                    await page.fill(selector, search_query)
                    input_found = True
                    break
                    
            if not input_found:
                logger.error("Could not find search bar.")
                await browser.close()
                return

            logger.info("Submitting search...")
            await page.keyboard.press("Enter")
            
            # Wait for search results to load
            await page.wait_for_timeout(5000)
            
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find job cards. Usually <article> or divs with specific classes
            job_articles = soup.find_all('article')
            if not job_articles:
                logger.info("No <article> tags found, looking for job cards...")
                # Fallback: look for common card divs
                job_articles = soup.find_all('div', class_=lambda x: x and 'job-card' in x.lower())
                
            logger.info(f"Found {len(job_articles)} potential job listings on CWJobs.")
            
            for article in job_articles:
                title_elem = article.find(['h2', 'h3'])
                job_title = title_elem.get_text(strip=True) if title_elem else "Unknown Title"
                
                link_elem = article.find('a', href=True)
                job_url = link_elem['href'] if link_elem else ""
                if job_url and job_url.startswith('/'):
                    job_url = "https://www.cwjobs.co.uk" + job_url
                    
                # The text chunks will contain company, location, salary etc
                text_chunks = [t for t in article.stripped_strings]
                company = text_chunks[1] if len(text_chunks) > 1 else ""
                
                try:
                    job_model = JobListing(
                        title=job_title or "Unknown Title",
                        company=company or "Unknown Company",
                        location="",
                        salary="",
                        deadline="",
                        url=job_url or "https://www.cwjobs.co.uk",
                        description=" ".join(text_chunks[:5])
                    )
                    jobs_data.append(job_model.to_dict())
                except ValidationError as e:
                    logger.warning(f"Validation error for job: {e}")
                
        except Exception as e:
            logger.error(f"Error during CWJobs scraping: {e}")
        finally:
            await browser.close()
            
    if jobs_data:
        init_db()
        bulk_upsert_jobs(jobs_data, "cwjobs")
    else:
        logger.info("No data extracted from CWJobs.")

if __name__ == "__main__":
    asyncio.run(scrape_cwjobs())
