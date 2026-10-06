"""
FastAPI backend for Gynalogical Disease Detection & Expert System (GDDES).
Replaces the old Flask app.py.

Routes
------
GET  /                   → welcome message + API info
POST /api/register       → user registration
POST /api/login          → user login
POST /api/prediction     → disease prediction (ML model)
POST /api/voice          → speech recognition + translation + review match
POST /api/model          → algorithm accuracy lookup
GET  /api/health         → health check

Interactive docs: http://127.0.0.1:8001/docs
"""

import os
import re
import sqlite3

import joblib
import nltk
import pandas as pd
from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# ── Optional libraries ──────────────────────────────────────────────────────
try:
    import speech_recognition as sr
except ImportError:
    sr = None

try:
    from googletrans import Translator
except ImportError:
    Translator = None

try:
    from gtts import gTTS
except ImportError:
    gTTS = None

try:
    import mysql.connector
except ImportError:
    mysql = None

# ── NLTK data ───────────────────────────────────────────────────────────────
try:
    stop_words = set(stopwords.words("english"))
except LookupError:
    nltk.download("stopwords", quiet=True)
    nltk.download("punkt", quiet=True)
    nltk.download("punkt_tab", quiet=True)
    stop_words = set(stopwords.words("english"))

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "app.db")
MODEL_PATH = os.path.join(BASE_DIR, "random_forest_model.joblib")
CSV_PATH = os.path.join(BASE_DIR, "gynecological_reviews.csv")
AUDIO_DIR = os.path.join(BASE_DIR, "static", "saves_audio")

# ── Load review dataset ──────────────────────────────────────────────────────
df_reviews = None
if os.path.exists(CSV_PATH):
    try:
        df_reviews = pd.read_csv(CSV_PATH)
    except Exception as e:
        print(f"[WARN] Could not load reviews CSV: {e}")

# ── Database setup ───────────────────────────────────────────────────────────
mydb = None
mycursor = None

try:
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        port="3306",
        database="db",
    )
    mycursor = mydb.cursor()
except Exception:
    mydb = None
    mycursor = None


def sqlite_connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def sqlite_query(query):
    return query.replace("%s", "?")


# Ensure users table exists
conn = sqlite_connect()
conn.execute(
    """CREATE TABLE IF NOT EXISTS users
       (id INTEGER PRIMARY KEY AUTOINCREMENT,
        name     TEXT,
        email    TEXT UNIQUE,
        password TEXT)"""
)
conn.commit()
conn.close()


def execute_query(query, values):
    if mydb is not None:
        try:
            mycursor.execute(query, values)
            mydb.commit()
            return
        except Exception:
            pass
    c = sqlite_connect()
    c.execute(sqlite_query(query), values)
    c.commit()
    c.close()


def fetch_query(query, values=()):
    if mydb is not None:
        try:
            mycursor.execute(query, values)
            return mycursor.fetchall()
        except Exception:
            pass
    c = sqlite_connect()
    data = c.execute(sqlite_query(query), values).fetchall()
    c.close()
    return [tuple(row) for row in data]


# ── NLP helpers ───────────────────────────────────────────────────────────────
def preprocess_text(text):
    ps = PorterStemmer()
    current_stop = set(stopwords.words("english"))
    text = re.sub("[^a-zA-Z]", " ", str(text)).lower()
    words = word_tokenize(text)
    return " ".join(ps.stem(w) for w in words if w not in current_stop)


def find_most_similar_review(input_text, reviews_df):
    if reviews_df is None or len(reviews_df) == 0:
        return "No review data available."
    processed_input = preprocess_text(input_text)
    temp = reviews_df.copy()
    temp["processed_review"] = temp["Review"].apply(preprocess_text)
    reviews = temp["processed_review"].tolist() + [processed_input]
    tfidf = TfidfVectorizer().fit_transform(reviews)
    sim = cosine_similarity(tfidf[-1], tfidf[:-1])
    return temp["Review"].iloc[sim.argmax()]


# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="GDDES – Gynalogical Disease Detection API",
    description="REST API backend (FastAPI) for the GDDES application.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Pydantic models ───────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    c_password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class PredictionRequest(BaseModel):
    Nausea: int
    Lumber: int
    Urine: int
    Micturition: int
    Urethra: int
    Itch: int
    Swelling: int
    Inflammation: int
    Nephritis: int
    Irregular: int
    No_Periods: int
    Excessive_Hair_Growth: int
    Buttocks: int
    Belly_Fat: int
    Hair_Loss: int
    Acne: int


class AlgorithmRequest(BaseModel):
    algo: str  # "1" ... "5"


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", tags=["General"])
def root():
    return {
        "app": "GDDES – Gynalogical Disease Detection API",
        "version": "2.0.0",
        "docs": "/docs",
        "endpoints": [
            "POST /api/register",
            "POST /api/login",
            "POST /api/prediction",
            "POST /api/voice",
            "POST /api/model",
            "GET  /api/health",
        ],
    }


@app.get("/api/health", tags=["General"])
def health():
    return {"status": "ok", "database": "sqlite" if mydb is None else "mysql"}


# ── Auth ──────────────────────────────────────────────────────────────────────

@app.post("/api/register", tags=["Auth"])
def register(body: RegisterRequest):
    if body.password != body.c_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")

    existing = fetch_query("SELECT UPPER(email) FROM users", ())
    existing_emails = [row[0] for row in existing]

    if body.email.upper() in existing_emails:
        raise HTTPException(status_code=409, detail="Email already registered.")

    execute_query(
        "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
        (body.name, body.email, body.password),
    )
    return {"message": "Successfully registered!", "email": body.email}


@app.post("/api/login", tags=["Auth"])
def login(body: LoginRequest):
    existing = fetch_query("SELECT UPPER(email) FROM users", ())
    existing_emails = [row[0] for row in existing]

    if body.email.upper() not in existing_emails:
        raise HTTPException(status_code=404, detail="Email does not exist.")

    pwd_data = fetch_query(
        "SELECT UPPER(password) FROM users WHERE email = %s", (body.email,)
    )
    if not pwd_data or body.password.upper() != pwd_data[0][0]:
        raise HTTPException(status_code=401, detail="Invalid password.")

    return {"message": "Login successful.", "email": body.email}


# ── Prediction ────────────────────────────────────────────────────────────────

@app.post("/api/prediction", tags=["ML"])
def prediction(body: PredictionRequest):
    if not os.path.exists(MODEL_PATH):
        raise HTTPException(status_code=500, detail="ML model file not found.")

    features = [[
        body.Nausea, body.Lumber, body.Urine, body.Micturition,
        body.Urethra, body.Itch, body.Swelling, body.Inflammation,
        body.Nephritis, body.Irregular, body.No_Periods,
        body.Excessive_Hair_Growth, body.Buttocks, body.Belly_Fat,
        body.Hair_Loss, body.Acne,
    ]]

    ml_model = joblib.load(MODEL_PATH)
    pred_value = ml_model.predict(features)[0]

    result_map = {0: "Healthy", 1: "PCOS", 2: "UTI"}
    result = result_map.get(int(pred_value), "Unknown")

    return {"prediction": result, "code": int(pred_value)}


# ── Voice ─────────────────────────────────────────────────────────────────────

INDIAN_LANGUAGES = {
    "hi": "Hindi", "bn": "Bengali", "ta": "Tamil", "te": "Telugu",
    "kn": "Kannada", "ml": "Malayalam", "gu": "Gujarati", "mr": "Marathi",
    "or": "Odia", "pa": "Punjabi", "as": "Assamese", "sd": "Sindhi",
    "ur": "Urdu", "ne": "Nepali",
}


@app.post("/api/voice", tags=["Voice"])
def voice(language: str = Form(...)):
    if language not in INDIAN_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language code '{language}'. Supported: {list(INDIAN_LANGUAGES)}",
        )
    if sr is None:
        raise HTTPException(status_code=501, detail="SpeechRecognition library not available.")
    if Translator is None:
        raise HTTPException(status_code=501, detail="googletrans library not available.")

    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
        wav_path = os.path.join(BASE_DIR, "input.wav")
        with open(wav_path, "wb") as f:
            f.write(audio.get_wav_data())
        my_text = recognizer.recognize_google(audio, language=f"{language}-IN")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech recognition failed: {e}")

    translator = Translator()
    translated_text = translator.translate(my_text, dest="en").text

    most_similar_review = find_most_similar_review(translated_text, df_reviews)

    audio_url = None
    if gTTS is not None:
        translator2 = Translator()
        translated_back = translator2.translate(str(most_similar_review), dest=language).text
        os.makedirs(AUDIO_DIR, exist_ok=True)
        output_path = os.path.join(AUDIO_DIR, "output.mp3")
        gTTS(text=translated_back, lang=language, slow=True).save(output_path)
        audio_url = "/static/saves_audio/output.mp3"

    return {
        "original_text": my_text,
        "translated_text": translated_text,
        "most_similar_review": str(most_similar_review),
        "audio_url": audio_url,
    }


# ── Model accuracy ────────────────────────────────────────────────────────────

ALGORITHM_MAP = {
    "1": {"name": "Decision Tree Classifier",     "accuracy": 99},
    "2": {"name": "Random Forest Classifier",      "accuracy": 99},
    "3": {"name": "Support Vector Machine (SVM)", "accuracy": 74},
    "4": {"name": "K-Nearest Neighbors (KNN)",    "accuracy": 66},
    "5": {"name": "Gradient Boosting Classifier", "accuracy": 67},
}


@app.post("/api/model", tags=["ML"])
def model_accuracy(body: AlgorithmRequest):
    entry = ALGORITHM_MAP.get(body.algo)
    if entry is None:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid algorithm key '{body.algo}'. Valid keys: 1-5.",
        )
    return {
        "algorithm": entry["name"],
        "accuracy": entry["accuracy"],
        "message": f"Accuracy for {entry['name']} is {entry['accuracy']}%",
    }


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8001, reload=True)
