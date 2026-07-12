from database import init_db, save_job_to_db
from models import JobListing
from pydantic import ValidationError
import os
from datetime import datetime
import asyncio
import pandas as pd
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def scrape_milkround(search_query="graduate data analyst", headless=True):
    url = "https://www.milkround.com/"
    
    async with async_playwright() as p:
        # Launching Firefox to bypass some basic bot protections
        browser = await p.firefox.launch(headless=headless)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"
        )
        page = await context.new_page()
        await Stealth().apply_stealth_async(page)
        
        print(f"Navigating to {url}...")
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
                
            print(f"Typing search query '{search_query}'...")
            
            # Locate the search bar. This handles a few common Stepstone/Milkround IDs
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
                print("Could not find search bar. Dumping HTML for inspection.")
                with open("milkround_debug.html", "w", encoding="utf-8") as f:
                    f.write(await page.content())
                await browser.close()
                return

            print("Submitting search...")
            await page.keyboard.press("Enter")
            
            # Wait for search results to load
            await page.wait_for_timeout(5000)
            
            # Save debug HTML to see what the results look like
            html = await page.content()
            with open("milkround_debug.html", "w", encoding="utf-8") as f:
                f.write(html)
                
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find job cards. Usually <article> or divs with specific classes
            job_articles = soup.find_all('article')
            if not job_articles:
                print("No <article> tags found, looking for job cards...")
                # Fallback: look for common card divs
                job_articles = soup.find_all('div', class_=lambda x: x and 'job-card' in x.lower())
                
            print(f"Found {len(job_articles)} potential job listings on Milkround.")
            
            jobs_data = []
            
            for article in job_articles:
                title_elem = article.find(['h2', 'h3'])
                job_title = title_elem.get_text(strip=True) if title_elem else "Unknown Title"
                
                link_elem = article.find('a', href=True)
                job_url = link_elem['href'] if link_elem else ""
                if job_url and job_url.startswith('/'):
                    job_url = "https://www.milkround.com" + job_url
                    
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
                        url=job_url or "https://totaljobs.com",
                        description=" ".join(text_chunks[:5])
                    )
                    jobs_data.append(job_model.to_dict())
                except ValidationError as e:
                    print(f"Validation error for job: {e}")
                
        except Exception as e:
            print(f"Error during Milkround scraping: {e}")
        finally:
            await browser.close()
            
    if jobs_data:
        init_db()

        for job in jobs_data:

            save_job_to_db(job, "milkround")

        print(f"Saved {len(jobs_data)} jobs to database.")
    else:
        print("No data extracted. Check milkround_debug.html")

if __name__ == "__main__":
    asyncio.run(scrape_milkround())
