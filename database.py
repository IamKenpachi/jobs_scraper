import os
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import declarative_base, sessionmaker

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

# Ensure the database directory exists
os.makedirs("output", exist_ok=True)
DATABASE_URL = "sqlite:///output/jobs.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def save_job_to_db(job_dict, source_site):
    """
    Upserts a job into the database based on the URL.
    """
    db = SessionLocal()
    try:
        # Check if job exists
        existing_job = db.query(JobDB).filter(JobDB.url == job_dict["URL"]).first()
        
        if existing_job:
            # Update existing job
            existing_job.title = job_dict["Job Title"]
            existing_job.company = job_dict["Company"]
            existing_job.location = job_dict["Location"]
            existing_job.salary = job_dict["Salary"]
            existing_job.deadline = job_dict["Deadline"]
            existing_job.description = job_dict["Description"]
            existing_job.source = source_site
        else:
            # Insert new job
            new_job = JobDB(
                url=job_dict["URL"],
                title=job_dict["Job Title"],
                company=job_dict["Company"],
                location=job_dict["Location"],
                salary=job_dict["Salary"],
                deadline=job_dict["Deadline"],
                description=job_dict["Description"],
                source=source_site
            )
            db.add(new_job)
            
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error saving to DB: {e}")
    finally:
        db.close()
