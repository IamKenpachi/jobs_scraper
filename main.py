import argparse
import asyncio
import logging
from dotenv import load_dotenv
from targetjobs_scraper import scrape_targetjobs
from jooble_scraper import scrape_jooble
from reed_scraper import scrape_reed
from milkround_scraper import scrape_milkround
from cwjobs_scraper import scrape_cwjobs

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

async def run_all(query, headless):
    logger.info(f"Starting CONCURRENT scrape for query: '{query}'...")
    
    tasks = [
        scrape_targetjobs(query, headless=headless),
        asyncio.to_thread(scrape_jooble, query),
        asyncio.to_thread(scrape_reed, query),
        scrape_milkround(query, headless=headless),
        scrape_cwjobs(query, headless=headless)
    ]
    
    # Use return_exceptions=True so one failure doesn't crash everything
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    scrapers = ["Targetjobs", "Jooble", "Reed", "Milkround", "CWJobs"]
    for scraper_name, result in zip(scrapers, results):
        if isinstance(result, Exception):
            logger.error(f"❌ {scraper_name} FAILED: {result}")
        else:
            logger.info(f"✅ {scraper_name} OK")
            
    logger.info("All scrapers finished!")

def main():
    parser = argparse.ArgumentParser(description="UK Jobs Scraper CLI")
    parser.add_argument("--site", required=True, choices=["targetjobs", "jooble", "reed", "milkround", "cwjobs", "all"], help="Which job board to scrape, or 'all'")
    parser.add_argument("--query", default="graduate data analyst", help="The job title to search for")
    parser.add_argument("--headed", action="store_true", help="Run the browser in headed mode (visible)")
    parser.add_argument("--debug", action="store_true", help="Save debug HTML files for browser scrapers")
    
    args = parser.parse_args()
    is_headless = not args.headed
    
    # We pass args.debug down if needed, but for now we'll just set it globally or adapt scrapers
    # The scrapers are currently hardcoded, but we can pass it later.
    
    if args.site == "all":
        asyncio.run(run_all(args.query, is_headless))
    elif args.site == "targetjobs":
        asyncio.run(scrape_targetjobs(args.query, headless=is_headless))
    elif args.site == "jooble":
        scrape_jooble(args.query)
    elif args.site == "reed":
        scrape_reed(args.query)
    elif args.site == "milkround":
        asyncio.run(scrape_milkround(args.query, headless=is_headless))
    elif args.site == "cwjobs":
        asyncio.run(scrape_cwjobs(args.query, headless=is_headless))

if __name__ == "__main__":
    main()
