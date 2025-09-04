from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
import os, shutil, uuid
from openai import OpenAI
from dotenv import load_dotenv

# from app.controllers.user import register_user, login_user, UserCreate, UserLogin, UserOut
from app.deps import get_db
from app.models.recording import Recording
from app.models.evaluation import Evaluation
from app.models.user import User
from pydantic import BaseModel, EmailStr
from app.services.user_manager import UserManager
from app.services.auth_service import auth_service

# -------- Load ENV + OpenAI Client --------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

router = APIRouter()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# -------- Upload ==> Save to DB ==> Transcribe ==> Update DB--------
@router.post("/upload")
async def upload_audio(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    try:
        # -------- Save file locally --------
        filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # -------- Fetch user --------
        user = db.get(User, current_user.id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # -------- Insert DB row (status=processing) --------
        recording = Recording(file_path=file_path, user_id=user.id, status="processing")
        db.add(recording)
        db.commit()
        db.refresh(recording)

        try:
            # -------- Transcribe with OpenAI Whisper --------
            with open(recording.file_path, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    model="gpt-4o-mini-transcribe", file=audio_file
                )

            # -------- Update DB row (status=done) --------
            recording.transcription = transcription.text
            recording.status = "done"
            db.commit()
            db.refresh(recording)

        except Exception:
            # -------- Update DB row (status=failed) --------
            recording.status = "failed"
            db.commit()

        return {
            "recording_id": recording.id,
            "file_path": file_path,
            "user_id": current_user.id,
            "status": recording.status,
            "transcription": recording.transcription,
        }

    except Exception as e:
       
        raise HTTPException(status_code=500, detail=str(e))


# -------- Evaluate Pronunciation (Azure Hook) --------
@router.post("/evaluate/{recording_id}")
async def evaluate_audio(recording_id: int, db: Session = Depends(get_db)):
    recording = db.get(Recording, recording_id)
    if not recording or not recording.transcription:
        raise HTTPException(
            status_code=404, detail="Recording not found or not transcribed yet"
        )

    # TODO: Azure Pronunciation Assessment Integration
    # send (recording.file_path + recording.transcription) to Azure
    # receive: score + feedback + phoneme breakdown

    evaluation = Evaluation(
        recording_id=recording.id,
        score=85,  # <- placeholder
        feedback="Pronunciation is clear with minor errors",
        details={"phonemes": "coming soon from Azure SDK"},
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)

    return {
        "recording_id": recording.id,
        "score": evaluation.score,
        "feedback": evaluation.feedback,
    }
