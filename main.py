import argparse
import asyncio
import sys

def main():
    parser = argparse.ArgumentParser(description="Jobs Scraper CLI")
    parser.add_argument(
        '--site', 
        type=str, 
        required=True, 
        choices=['targetjobs', 'jooble', 'reed', 'milkround', 'cwjobs'], 
        help="The website to scrape (targetjobs, jooble, reed, milkround, or cwjobs)"
    )
    parser.add_argument(
        '--query', 
        type=str, 
        default="graduate data analyst", 
        help="The search query (default: 'graduate data analyst')"
    )
    parser.add_argument(
        '--headed', 
        action='store_true', 
        help="Run the browser in headed mode (visible) to solve CAPTCHAs manually."
    )
    
    args = parser.parse_args()
    
    headless = not args.headed
    
    print(f"Starting {args.site.capitalize()} scraper for query: '{args.query}'...")
    
    if args.site == 'targetjobs':
        from targetjobs_scraper import scrape_targetjobs
        asyncio.run(scrape_targetjobs(search_query=args.query, headless=headless))
    elif args.site == 'jooble':
        from jooble_scraper import scrape_jooble
        asyncio.run(scrape_jooble(search_query=args.query, headless=headless))
    elif args.site == 'reed':
        from reed_scraper import scrape_reed
        asyncio.run(scrape_reed(search_query=args.query, headless=headless))
    elif args.site == 'milkround':
        from milkround_scraper import scrape_milkround
        asyncio.run(scrape_milkround(search_query=args.query, headless=headless))
    elif args.site == 'cwjobs':
        from cwjobs_scraper import scrape_cwjobs
        asyncio.run(scrape_cwjobs(search_query=args.query, headless=headless))

if __name__ == "__main__":
    main()
