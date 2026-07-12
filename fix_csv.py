import re

for file in ['targetjobs_scraper.py', 'jooble_scraper.py']:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'targetjobs' in file:
        content = re.sub(r'df\s*=\s*pd\.DataFrame\(jobs_data\).*?print\([^\)]+\)', 'init_db()\n    for job in jobs_data:\n        save_job_to_db(job, "targetjobs")\n    print("Saved final data to database.")', content, flags=re.DOTALL)
    else:
        content = re.sub(r'df\s*=\s*pd\.DataFrame\(jobs_data\).*?print\([^\)]+\)', 'init_db()\n    for job in jobs_data:\n        save_job_to_db(job, "jooble")\n    print("Saved Jooble API data to database.")', content, flags=re.DOTALL)
        
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)
