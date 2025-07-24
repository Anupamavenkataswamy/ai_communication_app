from fastapi import APIRouter, HTTPException, Form
from backend.database import cursor, conn
import bcrypt  # ✅ Import bcrypt

auth_router = APIRouter()

# 🔐 Signup route with hashed password
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

    # Hash the password before storing
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Store the hashed password (convert to bytes)
    cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                   (username, email, hashed_password))
    conn.commit()
    return {"message": "Signup successful"}

# 🔐 Login route with hashed password verification
@auth_router.post("/login")
def login(email: str = Form(...), password: str = Form(...)):
    cursor.execute("SELECT password FROM users WHERE email=?", (email,))
    result = cursor.fetchone()
    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    stored_hashed_password = result[0]

    # Verify hashed password
    if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
        return {"message": "Login successful"}

    raise HTTPException(status_code=401, detail="Invalid credentials")
