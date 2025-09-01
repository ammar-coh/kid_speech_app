# app/init_db.py
from app.db import engine, Base
from app.models import User, Recording, Evaluation  # import all models


def init_db():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")


if __name__ == "__main__":
    init_db()
