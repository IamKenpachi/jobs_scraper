import argparse
import asyncio
import sys

def main():
    parser = argparse.ArgumentParser(description="Web scraper for job listings.")
    parser.add_argument(
        '--site', 
        type=str, 
        required=True, 
        choices=['targetjobs', 'jooble'], 
        help="The target website to scrape (targetjobs or jooble)"
    )
    parser.add_argument(
        '--query', 
        type=str, 
        default='data analyst', 
        help="The search query for job listings (default: 'data analyst')"
    )
    parser.add_argument(
        '--headless', 
        action='store_true', 
        default=True, 
        help="Run the scraper in headless mode (default: True)"
    )
    
    args = parser.parse_args()

    if args.site == 'targetjobs':
        from targetjobs_scraper import scrape_targetjobs
        print(f"Starting TargetJobs scraper for query: '{args.query}'...")
        asyncio.run(scrape_targetjobs(search_query=args.query, headless=args.headless))
        
    elif args.site == 'jooble':
        from jooble_scraper import scrape_jooble
        print(f"Starting Jooble scraper for query: '{args.query}'...")
        asyncio.run(scrape_jooble(search_query=args.query, headless=args.headless))
        
    else:
        print(f"Unknown site: {args.site}")
        sys.exit(1)

if __name__ == "__main__":
    main()
