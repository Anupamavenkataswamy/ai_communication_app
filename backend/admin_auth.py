from fastapi import APIRouter, HTTPException, Form, Depends, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from backend.database import cursor, conn

admin_auth_router = APIRouter()
security = HTTPBasic()

# ✅ Admin Signup Route
@admin_auth_router.post("/admin/signup")
def admin_signup(username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    cursor.execute("SELECT * FROM admins WHERE username=?", (username,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Admin already exists")
    
    cursor.execute("INSERT INTO admins (username, email, password) VALUES (?, ?, ?)", (username, email, password))
    conn.commit()
    return {"message": "Admin signup successful"}

# ✅ Admin Login & Report Route
@admin_auth_router.get("/admin/report")
def download_report(credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username
    password = credentials.password

    cursor.execute("SELECT * FROM admins WHERE username=? AND password=?", (username, password))
    if not cursor.fetchone():
        raise HTTPException(status_code=401, detail="Unauthorized admin")

    try:
        # Assuming interview feedback is stored in `reports.csv`
        return Response(
            content=open("Interview_Report.csv", "rb").read(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=Interview_Report.csv"}
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Report file not found")
