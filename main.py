import argparse
import asyncio
from targetjobs_scraper import scrape_targetjobs
from jooble_scraper import scrape_jooble
from reed_scraper import scrape_reed
from milkround_scraper import scrape_milkround
from cwjobs_scraper import scrape_cwjobs
from totaljobs_scraper import scrape_totaljobs

async def run_all(query, headed):
    print(f"Starting CONCURRENT scrape for query: '{query}'...")
    
    # We run the synchronous API scrapers in threads using asyncio.to_thread,
    # and the async Playwright scrapers directly.
    tasks = [
        scrape_targetjobs(query, headed=headed),
        asyncio.to_thread(scrape_jooble, query),
        asyncio.to_thread(scrape_reed, query),
        scrape_milkround(query, headed=headed),
        scrape_cwjobs(query, headed=headed),
        scrape_totaljobs(query, headed=headed)
    ]
    
    await asyncio.gather(*tasks)
    print("All scrapers finished!")

def main():
    parser = argparse.ArgumentParser(description="UK Jobs Scraper CLI")
    parser.add_argument("--site", required=True, choices=["targetjobs", "jooble", "reed", "milkround", "cwjobs", "totaljobs", "all"], help="Which job board to scrape, or 'all'")
    parser.add_argument("--query", default="graduate data analyst", help="The job title to search for")
    parser.add_argument("--headed", action="store_true", help="Run the browser in headed mode (visible)")
    
    args = parser.parse_args()
    
    if args.site == "all":
        asyncio.run(run_all(args.query, args.headed))
    elif args.site == "targetjobs":
        asyncio.run(scrape_targetjobs(args.query, headed=args.headed))
    elif args.site == "jooble":
        scrape_jooble(args.query)
    elif args.site == "reed":
        scrape_reed(args.query)
    elif args.site == "milkround":
        asyncio.run(scrape_milkround(args.query, headed=args.headed))
    elif args.site == "cwjobs":
        asyncio.run(scrape_cwjobs(args.query, headed=args.headed))
    elif args.site == "totaljobs":
        asyncio.run(scrape_totaljobs(args.query, headed=args.headed))

if __name__ == "__main__":
    main()
