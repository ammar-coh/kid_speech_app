from fastapi import APIRouter, UploadFile, File

router = APIRouter()

@router.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    # For now, just return filename
    return {"filename": file.filename}

@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    # TODO: Add Whisper transcription later
    return {"transcription": f"Dummy transcription of {file.filename}"}

@router.post("/evaluate")
async def evaluate_audio(file: UploadFile = File(...)):
    # TODO: Add pronunciation scoring later
    return {"score": "Evaluation coming soon 🚧"}
