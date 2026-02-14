from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from uuid import uuid4, UUID

app = FastAPI(
    title="Mini Resume Collector",
    description="A simple in-memory API to collect and view candidate resumes.",
    version="1.0.0"
)

RESUME_DB = []



class ResumeBase(BaseModel):
    full_name: str = Field(..., min_length=2, description="Candidate's full name")
    email: EmailStr = Field(..., description="Valid email address")
    phone_number: str = Field(..., min_length=10, max_length=15, description="Contact number")
    experience_years: float = Field(..., ge=0, description="Years of experience (must be positive)")
    skills: List[str] = Field(default=[], description="List of technical skills")

    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "John Doe",
                "email": "john.doe@tensorlogic.ai",
                "phone_number": "9876543210",
                "experience_years": 3.5,
                "skills": ["Python", "FastAPI", "Docker"]
            }
        }

class ResumeResponse(ResumeBase):
    id: UUID

# --- Endpoints ---

@app.get("/", tags=["System"])
async def root():
    """
    Root endpoint to provide a welcome message.
    """
    return {"message": "Welcome to Mini Resume Collector. Visit /docs for API documentation."}

@app.get(
    "/health", 
    status_code=status.HTTP_200_OK,
    tags=["System"]
)
async def health_check():
    """
    Health check endpoint to verify service availability.
    Returns 200 OK if the service is up.
    """
    return {"status": "healthy", "service": "miniresume-collector"}

@app.post(
    "/resumes", 
    response_model=ResumeResponse, 
    status_code=status.HTTP_201_CREATED,
    tags=["Resumes"]
)
async def create_resume(resume: ResumeBase):
    """
    Submit a new resume.
    - Validates input data.
    - Generates a unique ID.
    - Stores in memory.
    """
    new_entry = resume.model_dump()
    new_entry["id"] = uuid4()
    
    RESUME_DB.append(new_entry)
    return new_entry

@app.get(
    "/resumes", 
    response_model=List[ResumeResponse],
    tags=["Resumes"]
)
async def get_all_resumes():
    """
    Retrieve all stored resumes.
    """
    return RESUME_DB

@app.get(
    "/resumes/{resume_id}", 
    response_model=ResumeResponse,
    tags=["Resumes"]
)
async def get_resume_by_id(resume_id: UUID):
    """
    Retrieve a specific resume by its UUID.
    """
    for resume in RESUME_DB:
        if resume["id"] == resume_id:
            return resume
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail="Resume not found"
    )
