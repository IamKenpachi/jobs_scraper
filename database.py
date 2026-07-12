import os
import logging
from datetime import datetime
from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.dialects.sqlite import insert

logger = logging.getLogger(__name__)

Base = declarative_base()

class JobDB(Base):
    __tablename__ = 'jobs'
    
    url = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String)
    salary = Column(String)
    deadline = Column(String)
    description = Column(String)
    source = Column(String) # To track which site it came from
    scraped_at = Column(DateTime, default=datetime.utcnow)

# Ensure the database directory exists
os.makedirs("output", exist_ok=True)
DATABASE_URL = "sqlite:///output/jobs.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def save_job_to_db(job_dict, source_site):
    """
    Backwards compatibility function for single jobs.
    It's recommended to use bulk_upsert_jobs instead for performance.
    """
    bulk_upsert_jobs([job_dict], source_site)

def bulk_upsert_jobs(jobs_list, source_site):
    """
    Upserts a list of jobs into the database based on the URL using a single query.
    """
    if not jobs_list:
        return
        
    db_jobs = []
    now = datetime.utcnow()
    for job in jobs_list:
        db_jobs.append({
            "url": job["URL"],
            "title": job["Job Title"],
            "company": job["Company"],
            "location": job["Location"],
            "salary": job["Salary"],
            "deadline": job["Deadline"],
            "description": job["Description"],
            "source": source_site,
            "scraped_at": now
        })
        
    try:
        stmt = insert(JobDB).values(db_jobs)
        
        # On conflict (URL exists), update the details and the scraped_at timestamp
        stmt = stmt.on_conflict_do_update(
            index_elements=["url"],
            set_={
                "title": stmt.excluded.title,
                "company": stmt.excluded.company,
                "location": stmt.excluded.location,
                "salary": stmt.excluded.salary,
                "deadline": stmt.excluded.deadline,
                "description": stmt.excluded.description,
                "source": stmt.excluded.source,
                "scraped_at": stmt.excluded.scraped_at
            }
        )
        
        with engine.begin() as conn:
            conn.execute(stmt)
            
        logger.info(f"Successfully upserted {len(db_jobs)} jobs from {source_site} to the database.")
    except Exception as e:
        logger.error(f"Error bulk saving to DB: {e}")
