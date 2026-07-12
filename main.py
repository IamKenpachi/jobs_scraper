import argparse
import asyncio
from targetjobs_scraper import scrape_targetjobs
from jooble_scraper import scrape_jooble
from reed_scraper import scrape_reed
from milkround_scraper import scrape_milkround
from cwjobs_scraper import scrape_cwjobs

async def run_all(query, headless):
    print(f"Starting CONCURRENT scrape for query: '{query}'...")
    
    tasks = [
        scrape_targetjobs(query, headless=headless),
        asyncio.to_thread(scrape_jooble, query),
        asyncio.to_thread(scrape_reed, query),
        scrape_milkround(query, headless=headless),
        scrape_cwjobs(query, headless=headless)
    ]
    
    await asyncio.gather(*tasks)
    print("All scrapers finished!")

def main():
    parser = argparse.ArgumentParser(description="UK Jobs Scraper CLI")
    parser.add_argument("--site", required=True, choices=["targetjobs", "jooble", "reed", "milkround", "cwjobs", "all"], help="Which job board to scrape, or 'all'")
    parser.add_argument("--query", default="graduate data analyst", help="The job title to search for")
    parser.add_argument("--headed", action="store_true", help="Run the browser in headed mode (visible)")
    
    args = parser.parse_args()
    is_headless = not args.headed
    
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
