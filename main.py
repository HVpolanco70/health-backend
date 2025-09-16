
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import shutil as sh
import os

# For AI analysis
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")  # Make sure to set this in Render environment

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

@app.post("/analyze")
async def analyze(data: dict):
    symptoms = data.get("symptoms", "")
    notes = data.get("notes", "")

    prompt = f"""Patient reports the following symptoms: {symptoms}.
    Notes: {notes}.
    List possible conditions that could be related, whether urgent care is needed,
    and what kind of doctor or tests might be helpful. Keep the explanation simple and patient-friendly."""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        suggestion = response["choices"][0]["message"]["content"]
    except Exception as e:
        suggestion = f"Error generating analysis: {str(e)}"

    return {"suggestion": suggestion}
