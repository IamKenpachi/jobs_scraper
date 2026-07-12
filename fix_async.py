import os

files = ['jooble_scraper.py', 'reed_scraper.py']

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    content = content.replace('async def scrape_jooble', 'def scrape_jooble')
    content = content.replace('async def scrape_reed', 'def scrape_reed')
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
