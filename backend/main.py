from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi.responses import FileResponse
import os

# Load environment variables
load_dotenv(dotenv_path="./backend/.env")

# Import routers
from backend.feedback import feedback_router
from backend.auth import auth_router
from backend.questions import questions_router
from backend.admin_auth import admin_auth_router
from backend.admin_dashboard import admin_dashboard_router


# Import DB initializers
from backend.database import init_db
from backend.admin_database import init_admin_db
from backend.feedback_db import init_feedback_db

# App
app = FastAPI()

# Init DBs
init_db()
init_admin_db()
init_feedback_db()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(feedback_router)
app.include_router(auth_router, prefix="/auth")
app.include_router(questions_router)
app.include_router(admin_auth_router)
app.include_router(admin_dashboard_router)

@app.get("/")
def read_root():
    return {"message": "Backend is running"}
    #return FileResponse("frontend/index.html")