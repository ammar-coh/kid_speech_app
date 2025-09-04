<!-- Speak Easy Kids Backend API -->
This is the backend API for the **Speak Easy Kids** application, built with **FastAPI** and **PostgreSQL**.  
It includes authentication, audio processing, and integrations (OpenAI, Google OAuth, etc.).
---
## 🚀 Setup Instructions
<!-- 1. **Clone the repository**  -->
```bash
git clone <your-repo-url>
cd kid_speech_app

# 2. Create and activate a virtual environment

python -m venv venv
venv\Scripts\activate.bat
# To deactivate:
deactivate
# 3. Create a .env file in the project root with the following:
APP_NAME=Speak easy kids Backend API
APP_ENV=development
# OpenAI API Key
OPENAI_API_KEY=OPENAIKEY2392i940230230230examplehere
# PostgreSQL Database URL
DATABASE_URL=postgresql://username:password@localhost:5432/speak_easydb
# JWT Secret (for authentication)
JWT_SECRET=supersecretkey
# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Session Secret (Generate with Python)
SESSION_SECRET=python -c "import secrets; print(secrets.token_hex(32))"
# 4. Install dependencies
pip install -r requirements.txt
# If you add new packages, update requirements:
pip freeze > requirements.txt
# 5. Run the server
uvicorn app.main:app --reload
# API Docs:
Swagger UI → http://127.0.0.1:8000/docs
ReDoc → http://127.0.0.1:8000/redoc
# Notes
Always activate the virtual environment before running or installing packages.
Run pip install -r requirements.txt after pulling latest code.
Generate a new session secret if needed: 
python -c "import secrets; print(secrets.token_hex(32))"
# Contribution Guidelines
Pull the latest changes before starting new work.
Create feature branches for new work.
Keep commits clean and descriptive.
Test your changes locally before pushing.
# Database migration tool alembic Schema Migration / Database Versioning Tools
Database schema out of sync with migration history
You have migration scripts in alembic/versions/ (good ✅).
But your database hasn’t had those migrations applied yet (that’s why you only see the users table).
Alembic tracks this with the alembic_version table inside your DB.
If it’s empty or missing, Alembic thinks no migrations have ever run.
📌 In short:
You pulled the code (and migrations) from Git, but your local database hasn’t been upgraded to the latest schema.
The fix = run:
alembic upgrade head
# Drop DB (dev)  once if the DB was created before Alembic was properly set up.===>>> WARNING <<<=====
# Quick dev fix: Drop DB, recreate, run migrations cleanly → ✅ now Alembic owns the schema history.
# To mark migrations as already applied, without dropping.
Alternative (prod style): alembic stamp head 
