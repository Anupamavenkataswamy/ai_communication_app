from fastapi import APIRouter
from fastapi.responses import JSONResponse, StreamingResponse
import sqlite3
import csv
from io import StringIO

admin_dashboard_router = APIRouter()

# Endpoint 1: Get all feedback entries
@admin_dashboard_router.get("/feedback")
def get_all_feedback():
    conn = sqlite3.connect("feedback.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username, email, question, answer, score, feedback, mode, submitted_at FROM feedback")
    data = cursor.fetchall()
    conn.close()

    columns = ["username", "email", "question", "answer", "score", "feedback", "mode", "submitted_at"]
    feedback_list = [dict(zip(columns, row)) for row in data]
    return {"feedback": feedback_list}

# Endpoint 2: Download feedback as CSV
@admin_dashboard_router.get("/feedback/csv")
def download_feedback_csv():
    conn = sqlite3.connect("feedback.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username, email, question, answer, score, feedback, mode, submitted_at FROM feedback")
    data = cursor.fetchall()
    conn.close()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Username", "Email", "Question", "Answer", "Score", "Feedback", "Mode", "Submitted At"])
    writer.writerows(data)
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=feedback.csv"}
    )
