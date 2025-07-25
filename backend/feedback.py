from fastapi import APIRouter, Form, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from datetime import datetime
from io import StringIO
from dotenv import load_dotenv
import openai
import os
import tempfile
import sqlite3
import csv
import re

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

feedback_router = APIRouter()

# Database connection
conn = sqlite3.connect("feedback.db", check_same_thread=False)
cursor = conn.cursor()

# Helper: Extract scores from feedback text
def extract_score(label, text):
    match = re.search(rf"{label}:\s*(\d)/5", text)
    return int(match.group(1)) if match else 0

def extract_comment(label, text):
    match = re.search(rf"{label}:\s*\d/5\s*-\s*(.+)", text)
    return match.group(1).strip() if match else "No comment"

def extract_suggestions(text):
    match = re.search(r"Suggestions:\s*(.+)", text)
    return match.group(1).strip() if match else "No suggestion"

@feedback_router.post("/feedback")
async def get_feedback(
    username: str = Form(...),
    email: str = Form(...),
    question: str = Form(...),
    answer: str = Form(None),
    audio: UploadFile = File(None)
):
    mode = "text"

    # Handle audio upload and transcription
    if audio:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_audio:
                temp_audio.write(await audio.read())
                temp_audio_path = temp_audio.name

            with open(temp_audio_path, "rb") as audio_file:
                transcript = openai.Audio.transcribe("whisper-1", audio_file)
                answer = transcript["text"]
                mode = "audio"

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")

    # Ensure answer exists
    if not answer or answer.strip() == "":
        raise HTTPException(status_code=400, detail="No answer provided")

    # Prepare prompt for OpenAI
    prompt = f"""
You are a communication expert evaluating a candidate's interview answer.

Question: {question}
Answer: {answer}

Give scores and short comments in this format:

Clarity: X/5 - comment  
Fluency: X/5 - comment  
Grammar: X/5 - comment  
Confidence: X/5 - comment  
Suggestions: 1-2 line suggestion
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        feedback_text = response.choices[0].message.content.strip()

        # Extract scores
        clarity_score = extract_score("Clarity", feedback_text)
        fluency_score = extract_score("Fluency", feedback_text)
        grammar_score = extract_score("Grammar", feedback_text)
        confidence_score = extract_score("Confidence", feedback_text)
        total_score = clarity_score + fluency_score + grammar_score + confidence_score

        # Save to database
        cursor.execute('''
            INSERT INTO feedback (username, email, question, answer, score, feedback, mode, submitted_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            username,
            email,
            question,
            answer,
            total_score,
            feedback_text,
            mode,
            datetime.now().isoformat()
        ))
        conn.commit()

        return {"message": "Answer submitted successfully ✅"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating feedback: {str(e)}")

@feedback_router.get("/admin/feedback")
def get_all_feedback():
    try:
        cursor.execute("SELECT username, email, question, answer, score, feedback, mode, submitted_at FROM feedback ORDER BY submitted_at DESC")
        rows = cursor.fetchall()

        results = []
        for row in rows:
            feedback_text = row[5]

            clarity_score = extract_score("Clarity", feedback_text)
            fluency_score = extract_score("Fluency", feedback_text)
            grammar_score = extract_score("Grammar", feedback_text)
            confidence_score = extract_score("Confidence", feedback_text)

            clarity_comment = extract_comment("Clarity", feedback_text)
            fluency_comment = extract_comment("Fluency", feedback_text)
            grammar_comment = extract_comment("Grammar", feedback_text)
            confidence_comment = extract_comment("Confidence", feedback_text)
            suggestions = extract_suggestions(feedback_text)

            total_score = clarity_score + fluency_score + grammar_score + confidence_score

            results.append({
                "username": row[0],
                "email": row[1],
                "question": row[2],
                "answer": row[3],
                "clarity": f"{clarity_score}/5 - {clarity_comment}",
                "fluency": f"{fluency_score}/5 - {fluency_comment}",
                "grammar": f"{grammar_score}/5 - {grammar_comment}",
                "confidence": f"{confidence_score}/5 - {confidence_comment}",
                "total_score": total_score,
                "suggestions": suggestions,
                "mode": row[6],
                "submitted_at": row[7]
            })

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@feedback_router.get("/admin/feedback/download")
def download_feedback_csv():
    try:
        cursor.execute("SELECT username, email, question, answer, score, feedback, mode, submitted_at FROM feedback ORDER BY submitted_at DESC")
        rows = cursor.fetchall()

        csv_file = StringIO()
        writer = csv.writer(csv_file)
        writer.writerow(["Username", "Email", "Question", "Answer", "Score", "Feedback", "Mode", "Submitted At"])

        for row in rows:
            writer.writerow(row)

        csv_file.seek(0)
        return StreamingResponse(csv_file, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=feedback_report.csv"})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))