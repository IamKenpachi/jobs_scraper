from pydantic import BaseModel, HttpUrl, Field
from typing import Optional

class JobListing(BaseModel):
    title: str = Field(..., description="The title of the job position")
    company: str = Field(..., description="The company offering the job")
    location: str = Field("", description="The location of the job")
    salary: str = Field("", description="The salary or salary range for the job")
    deadline: str = Field("", description="The application deadline")
    url: HttpUrl = Field(..., description="The URL to the job posting")
    description: str = Field("", description="A short snippet or full description of the job")

    def to_dict(self):
        # Convert HttpUrl to string for pandas compatibility
        data = self.model_dump()
        data['url'] = str(data['url'])
        
        # Standardize the keys to match our CSV columns
        return {
            "Job Title": data['title'],
            "Company": data['company'],
            "Location": data['location'],
            "Salary": data['salary'],
            "Deadline": data['deadline'],
            "URL": data['url'],
            "Description": data['description']
        }
