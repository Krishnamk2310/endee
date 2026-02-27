from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import uuid
from typing import List, Dict, Any

from config import MODEL_NAME
from pdf_parser import extract_text_from_pdf_stream
from vector_store import create_index, insert_resume, search_job_description

# setup app
app = FastAPI(
    title="Resume-Job Matcher",
    description="Match Resumes to Job Descriptions using Endee Vector Database",
    version="1.0.0"
)

# serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# init model early
print(f"Loading Embedding Model: {MODEL_NAME}...")
model = SentenceTransformer(MODEL_NAME)
print("Model loaded successfully!")

@app.on_event("startup")
def startup_event():
    # check endee index
    create_index()

class MatchRequest(BaseModel):
    job_description: str
    top_k: int = 5

@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    """ upload and index pdf """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    try:
        # read pdf text
        file_bytes = await file.read()
        extracted_text = extract_text_from_pdf_stream(file_bytes)
        
        if not extracted_text:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF.")
        
        # generate random id
        resume_id = str(uuid.uuid4())
        
        # get embeddings
        vector = model.encode(extracted_text).tolist()
        
        # metadata for cards
        metadata = {
            "filename": file.filename,
            "text_snippet": extracted_text[:200] + "..." 
        }
        
        # save to endee
        success = insert_resume(resume_id, vector, metadata)
        
        if not success:
             raise HTTPException(status_code=500, detail="Failed to store resume in Endee database.")
             
        return {
            "message": "Resume successfully uploaded and indexed.",
            "resume_id": resume_id,
            "filename": file.filename
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/match")
async def match_job_description(request: MatchRequest):
    """ search by jd """
    if not request.job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")
        
    try:
        # embed query
        jd_vector = model.encode(request.job_description).tolist()
        
        # get matches
        results = search_job_description(jd_vector, top_k=request.top_k)
        
        return {
            "job_description_snippet": request.job_description[:100] + "...",
            "matches": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

# health check
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API is running"}

# ui route
from fastapi.responses import FileResponse
import os

@app.get("/")
def read_index():
    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "index.html not found in static folder."}

