import pandas as pd
import random
from fastapi import APIRouter

questions_router = APIRouter()

@questions_router.get("/questions")
def get_questions():
    df = pd.read_csv("backend/questions.csv")
    questions = df["question"].dropna().tolist()
    return {"questions": random.sample(questions, min(10, len(questions)))}
