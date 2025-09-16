
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
import shutil as sh
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class Entry(BaseModel):
    date: str
    symptoms: str
    pain_level: int
    notes: Optional[str] = ""
    file_name: Optional[str] = None

entries: List[Entry] = []

@app.post("/journal-entry")
async def add_entry(
    date: str = Form(...),
    symptoms: str = Form(...),
    pain_level: int = Form(...),
    notes: str = Form(""),
    file: Optional[UploadFile] = File(None)
):
    filename = None
    if file:
        filename = f"{UPLOAD_DIR}/{file.filename}"
        with open(filename, "wb") as buffer:
            sh.copyfileobj(file.file, buffer)

    entry = Entry(
        date=date,
        symptoms=symptoms,
        pain_level=pain_level,
        notes=notes,
        file_name=file.filename if file else None
    )
    entries.insert(0, entry)
    return {"message": "Entry added", "entry": entry}

@app.get("/journal-entries", response_model=List[Entry])
def get_entries():
    return entries
