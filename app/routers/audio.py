from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
import os, shutil, uuid
from openai import OpenAI
from dotenv import load_dotenv

from app.deps import get_db
from app.models.recording import Recording
from app.models.evaluation import Evaluation
from app.models.user import User
# -------- Load ENV + OpenAI Client --------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

router = APIRouter()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# -------- Upload & Save to DB --------
# -------- Upload & Save to DB --------
@router.post("/upload")
async def upload_audio(
    file: UploadFile = File(...),
    user_id: int = 1,  # 👈 replace this later with actual logged-in user
    db: Session = Depends(get_db)
):
    try:
        # Save file locally
        filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Fetch user (must exist)
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Insert into DB (linked to user)
        recording = Recording(file_path=file_path, user_id=user.id)
        db.add(recording)
        db.commit()
        db.refresh(recording)

        return {
            "recording_id": recording.id,
            "file_path": file_path,
            "user_id": user.id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    try:
        # Save file locally
        filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Insert into DB
        recording = Recording(file_path=file_path)
        db.add(recording)
        db.commit()
        db.refresh(recording)

        return {"recording_id": recording.id, "file_path": file_path}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------- Transcribe with OpenAI Whisper API --------
@router.post("/transcribe/{recording_id}")
async def transcribe_audio(
    recording_id: int,
    db: Session = Depends(get_db)
):
    recording = db.get(Recording, recording_id)
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    try:
        with open(recording.file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",  # ✅ faster & cheaper than whisper-1
                file=audio_file
            )

        # Update DB with transcription
        recording.transcription = transcription.text
        db.commit()
        db.refresh(recording)

        return {"recording_id": recording.id, "text": transcription.text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------- Evaluate Pronunciation (Azure Hook) --------
@router.post("/evaluate/{recording_id}")
async def evaluate_audio(
    recording_id: int,
    db: Session = Depends(get_db)
):
    recording = db.get(Recording, recording_id)
    if not recording or not recording.transcription:
        raise HTTPException(
            status_code=404,
            detail="Recording not found or not transcribed yet"
        )

    # TODO: Azure Pronunciation Assessment Integration
    # send (recording.file_path + recording.transcription) to Azure
    # receive: score + feedback + phoneme breakdown

    evaluation = Evaluation(
        recording_id=recording.id,
        score=85,  # <- placeholder
        feedback="Pronunciation is clear with minor errors",
        details={"phonemes": "coming soon from Azure SDK"}
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)

    return {
        "recording_id": recording.id,
        "score": evaluation.score,
        "feedback": evaluation.feedback
    }
