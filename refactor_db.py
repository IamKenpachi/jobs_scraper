import os
import re

files = [
    'targetjobs_scraper.py',
    'jooble_scraper.py',
    'reed_scraper.py',
    'milkround_scraper.py',
    'cwjobs_scraper.py',
    'totaljobs_scraper.py'
]

for f in files:
    if not os.path.exists(f):
        continue
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    site_name = f.split('_')[0]
    
    if 'from database import init_db, save_job_to_db' not in content:
        content = "from database import init_db, save_job_to_db\n" + content
    
    # We want to replace the pandas conversion and CSV saving with DB saving
    # The pandas part usually starts with: df = pd.DataFrame(jobs_data)
    # And ends with: print(f"Saved final data to {filename}.")
    
    # Let's use regex to find this block and replace it
    pattern = re.compile(r'(\s+)df = pd\.DataFrame\(jobs_data\).*?print\(f"Saved final data to \{filename\}\."\)', re.DOTALL)
    
    replacement = r'''\1init_db()
\1for job in jobs_data:
\1    save_job_to_db(job, "''' + site_name + r'''")
\1print(f"Saved {len(jobs_data)} jobs to database.")'''

    content = pattern.sub(replacement, content)
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
