from fastapi import APIRouter, HTTPException, Form
from backend.database import cursor, conn

auth_router = APIRouter()

@auth_router.post("/signup")
def signup(username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    # Check if email is already registered
    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if username already exists
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Insert new user
    cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
    conn.commit()
    return {"message": "Signup successful"}

@auth_router.post("/login")
def login(email: str = Form(...), password: str = Form(...)):
    cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    if cursor.fetchone():
        return {"message": "Login successful"}
    raise HTTPException(status_code=401, detail="Invalid credentials")
