from fastapi import APIRouter, HTTPException, Form
from backend.admin_database import admin_cursor, admin_conn
from passlib.context import CryptContext

admin_auth_router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ✅ Admin Signup
@admin_auth_router.post("/admin/signup")
def admin_signup(username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    # Hash password
    hashed_password = pwd_context.hash(password)
    
    try:
        admin_cursor.execute(
            "INSERT INTO admins (username, email, password) VALUES (?, ?, ?)",
            (username, email, hashed_password)
        )
        admin_conn.commit()
    except:
        raise HTTPException(status_code=400, detail="Admin already exists")
    
    return {"message": "Admin signup successful"}

# ✅ Admin Login
@admin_auth_router.post("/admin/login")
def admin_login(email: str = Form(...), password: str = Form(...)):
    admin_cursor.execute("SELECT * FROM admins WHERE email=?", (email,))
    admin = admin_cursor.fetchone()

    if not admin:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    
    stored_hashed_password = admin[3]

    if not pwd_context.verify(password, stored_hashed_password):
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    
    return {"message": "Admin login successful"}
