from models import JobListing
from pydantic import ValidationError
import os
from datetime import datetime
import asyncio
import pandas as pd
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

async def scrape_targetjobs(search_query="data", headless=True):
    url = f"https://targetjobs.co.uk/search/jobs?search={search_query}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        page = await browser.new_page()
        
        print(f"Navigating to {url}...")
        await page.goto(url, wait_until='networkidle')
        
        # Wait for the job results to load (checking for job cards or empty state)
        print("Waiting for results to render...")
        try:
            # We'll wait for a common indicator of a job list, e.g. a link to a job
            await page.wait_for_selector('a[href^="/jobs/"]', timeout=10000)
        except Exception as e:
            print(f"Could not find job links, maybe no results or different selector: {e}")
        
        html = await page.content()
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        jobs_data = []
        
        # Try to find job cards - TargetJobs uses varying selectors, but often links starting with /jobs/
        # or specific article tags. We'll find all <a> tags linking to jobs first.
        job_links = soup.find_all('a', href=True)
        job_cards = [a for a in job_links if '/jobs/' in a['href'] and a.find('h3') or a.find('h2')] # Usually a card has a header inside
        
        if not job_cards:
            # Fallback if the DOM structure is different
            print("Could not find job cards with heuristic. Dumping a small snippet of HTML for debugging.")
            # Let's save the HTML to debug
            with open("debug_page.html", "w", encoding="utf-8") as f:
                f.write(html)
            await browser.close()
            return
            
        print(f"Found {len(job_cards)} potential job listings on the first page.")
        
        for card in job_cards:
            # Extract all text chunks
            text_chunks = [t for t in card.stripped_strings]
            
            # Clean chunks by removing known noise
            clean_chunks = [c for c in text_chunks if c.lower() not in ['save', 'spotlight'] and len(c) > 1]
            
            # The title is usually an h3 or h2, but let's try to extract it from the HTML directly if possible
            title_elem = card.find(['h3', 'h2'])
            job_title = title_elem.get_text(strip=True) if title_elem else ""
            
            company = ""
            location = ""
            salary = ""
            deadline = ""
            
            # If we have clean chunks, try to identify them
            if clean_chunks:
                # Company is usually the first chunk (after filtering 1-letter logos and 'spotlight')
                company = clean_chunks[0]
                
                # Find salary (contains £)
                salaries = [c for c in clean_chunks if '£' in c]
                if salaries:
                    salary = salaries[0]
                    
                # Find deadline (contains 'days' or 'apply')
                deadlines = [c for c in clean_chunks if 'apply' in c.lower() or 'days' in c.lower()]
                if deadlines:
                    deadline = deadlines[0]
                    
                # Location is tricky, but it's usually between Job Title and Salary/Deadline
                # Let's try to find it by elimination
                used_chunks = [company, job_title, salary, deadline]
                remaining = [c for c in clean_chunks if c not in used_chunks]
                if remaining:
                    location = remaining[0] # Usually the first remaining is location

            jobs_data.append({
                "Job Title": job_title,
                "Company": company,
                "Location": location,
                "Salary": salary,
                "Deadline": deadline,
                "URL": "https://targetjobs.co.uk" + card['href'] if card['href'].startswith('/') else card['href'],
                "Description": ""
            })

        print("Fetching job descriptions for each listing...")
        for i, job in enumerate(jobs_data):
            print(f"[{i+1}/{len(jobs_data)}] Fetching description for {job['Job Title']} at {job['Company']}...")
            try:
                await page.goto(job['URL'], wait_until='domcontentloaded', timeout=15000)
                # Give it a small moment for React to hydrate the DOM
                await page.wait_for_timeout(1000)
                
                # Extract HTML
                job_html = await page.content()
                job_soup = BeautifulSoup(job_html, 'html.parser')
                
                # The description is usually inside a main tag or article tag.
                main_content = job_soup.find('main')
                if main_content:
                    # We can grab all paragraphs or just the raw text
                    paragraphs = main_content.find_all('p')
                    if paragraphs:
                        description = "\n\n".join([p.get_text(strip=True) for p in paragraphs])
                    else:
                        description = main_content.get_text(separator="\n", strip=True)
                else:
                    description = job_soup.get_text(separator="\n", strip=True)
                    
                job['Description'] = description
            except Exception as e:
                print(f"Failed to fetch {job['URL']}: {e}")
                job['Description'] = f"Error: {e}"
        
        await browser.close()
        
    df = pd.DataFrame(jobs_data)
    df.to_csv("targetjobs_data.csv", index=False)
    print("Saved final data with descriptions to targetjobs_data.csv.")

