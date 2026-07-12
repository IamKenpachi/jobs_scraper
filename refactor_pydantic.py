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
    
    if 'from models import JobListing' not in content:
        content = "from models import JobListing\nfrom pydantic import ValidationError\n" + content
        
    # Replace dict appends with Pydantic model appends
    
    if f == 'reed_scraper.py':
        old_block = '''        jobs_data.append({
            "Job Title": job.get("jobTitle", ""),
            "Company": job.get("employerName", ""),
            "Location": job.get("locationName", ""),
            "Salary": f"£{job.get('minimumSalary', '')} - £{job.get('maximumSalary', '')}",
            "Deadline": job.get("expirationDate", ""),
            "URL": job.get("jobUrl", ""),
            "Description": job.get("jobDescription", "")
        })'''
        new_block = '''        try:
            job_model = JobListing(
                title=job.get("jobTitle", "Unknown Title"),
                company=job.get("employerName", "Unknown Company"),
                location=job.get("locationName", ""),
                salary=f"£{job.get('minimumSalary', '')} - £{job.get('maximumSalary', '')}",
                deadline=job.get("expirationDate", "") or "",
                url=job.get("jobUrl", "https://reed.co.uk"),
                description=job.get("jobDescription", "")
            )
            jobs_data.append(job_model.to_dict())
        except ValidationError as e:
            print(f"Validation error for job: {e}")'''
        content = content.replace(old_block, new_block)
        
    elif f in ['milkround_scraper.py', 'cwjobs_scraper.py', 'totaljobs_scraper.py']:
        old_block = '''                jobs_data.append({
                    "Job Title": job_title,
                    "Company": company,
                    "Location": "",
                    "Salary": "",
                    "Deadline": "",
                    "URL": job_url,
                    "Description": " ".join(text_chunks[:5]) # Simple snippet
                })'''
        new_block = '''                try:
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
                    print(f"Validation error for job: {e}")'''
        content = content.replace(old_block, new_block)

    elif f == 'jooble_scraper.py':
        old_block = '''        jobs_data.append({
            "Job Title": job.get("title", ""),
            "Company": job.get("company", ""),
            "Location": job.get("location", ""),
            "Salary": job.get("salary", ""),
            "Deadline": "",
            "URL": job.get("link", ""),
            "Description": job.get("snippet", "")
        })'''
        new_block = '''        try:
            job_model = JobListing(
                title=job.get("title", "Unknown Title"),
                company=job.get("company", "Unknown Company"),
                location=job.get("location", ""),
                salary=job.get("salary", ""),
                deadline="",
                url=job.get("link", "https://jooble.org"),
                description=job.get("snippet", "")
            )
            jobs_data.append(job_model.to_dict())
        except ValidationError as e:
            print(f"Validation error for job: {e}")'''
        content = content.replace(old_block, new_block)

    elif f == 'targetjobs_scraper.py':
        old_block = '''                jobs_data.append({
                    "Job Title": title_text,
                    "Company": company_text,
                    "Location": location_text,
                    "Salary": salary_text,
                    "Deadline": deadline_text,
                    "URL": job_url,
                    "Description": ""
                })'''
        new_block = '''                try:
                    job_model = JobListing(
                        title=title_text or "Unknown Title",
                        company=company_text or "Unknown Company",
                        location=location_text,
                        salary=salary_text,
                        deadline=deadline_text,
                        url=job_url or "https://targetjobs.co.uk",
                        description=""
                    )
                    jobs_data.append(job_model.to_dict())
                except ValidationError as e:
                    print(f"Validation error for job: {e}")'''
        content = content.replace(old_block, new_block)

    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
