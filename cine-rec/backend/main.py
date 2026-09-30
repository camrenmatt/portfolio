# main.py
from fastapi import FastAPI, Query, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import pg8000
from pg8000.dbapi import IntegrityError
from passlib.context import CryptContext
import jwt
import csv
import io
import os
import requests
import time
from typing import Optional, Dict, Any

# --- Configuration ---
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-key")  # move to env var in production
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "cine-roARY18.")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME", "cinerec")
TMDB_API_KEY = "N/A"

# --- Security / password hashing ---
# Use bcrypt_sha256 for new hashes; keep bcrypt for compatibility with existing hashes.
pwd_context = CryptContext(schemes=["bcrypt_sha256", "bcrypt"], deprecated="auto")

auth_scheme = HTTPBearer()

# --- FastAPI app ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic schemas ---
class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str


# --- DB helpers ---
def get_db():
    """
    Returns a new pg8000 connection. Caller should close() when done.
    """
    return pg8000.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME
    )

def get_user_by_username(conn, username: str) -> Optional[Dict[str, Any]]:
    """
    Return a dict like {'user_id': int, 'username': str, 'password_hash': str}
    or None if not found.
    """
    cur = conn.cursor()
    cur.execute("SELECT user_id, username, password_hash FROM users WHERE username = %s", (username,))
    row = cur.fetchone()
    cur.close()
    if not row:
        return None
    return {"user_id": row[0], "username": row[1], "password_hash": row[2]}

def save_user_hash(conn, username: str, password_hash: str) -> int:
    """
    Insert a new user with username and password_hash.
    Returns the new user_id.
    Raises pg8000.exceptions.IntegrityError if username exists.
    """
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (username, password_hash)
        VALUES (%s, %s)
        RETURNING user_id
    """, (username, password_hash))
    user_id = cur.fetchone()[0]
    cur.close()
    conn.commit()
    return user_id

def update_user_hash(conn, user_id: int, password_hash: str):
    cur = conn.cursor()
    cur.execute("UPDATE users SET password_hash = %s WHERE user_id = %s", (password_hash, user_id))
    cur.close()
    conn.commit()

def create_token(user_id: int) -> str: #make user token
    return jwt.encode({"user_id": user_id}, JWT_SECRET, algorithm="HS256")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> int: #get current user_id
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return int(payload["user_id"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def fetch_tmdb_id(title: str, year: int): #get thhe tmdb_id for a movie
    url = (
        "https://api.themoviedb.org/3/search/movie"
        f"?api_key={TMDB_API_KEY}&query={title}&year={year}"
    )
    try:
        res = requests.get(url, timeout=5).json()
        results = res.get("results", [])
        if not results:
            return None
        return results[0]["id"]
    except Exception:
        return None


#password helpers
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, stored_hash: str) -> bool:
    return pwd_context.verify(password, stored_hash)

#endpoints
@app.post("/create-account")
def create_account(body: RegisterRequest):
    conn = get_db()
    try:
        username = body.username.strip()
        password = body.password

        if len(password) < 6: #validate password length
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

        if get_user_by_username(conn, username): #check if username exists
            raise HTTPException(status_code=400, detail="Username already exists")

        hashed = hash_password(password) #hash password

        user_id = save_user_hash(conn, username, hashed) #insert user

        token = create_token(user_id) #generate JWT

        return {
            "token": token,
            "username": username
        }

    except IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")
    finally:
        conn.close()

@app.post("/login")
def login(body: LoginRequest):
    conn = get_db()
    try:
        user = get_user_by_username(conn, body.username)
        if not user: #if user doesn't exist
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user_id = user["user_id"]
        stored_hash = user["password_hash"]

        #verify password
        try:
            ok = verify_password(body.password, stored_hash)
        except Exception:
            #verification error catch
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not ok:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        #migrate old bcrypt hashes to bcrypt_sha256 on successful login
        if pwd_context.needs_update(stored_hash):
            new_hash = hash_password(body.password)
            update_user_hash(conn, user_id, new_hash)

        token = create_token(user_id)
        return {"token": token}
    finally:
        conn.close()

@app.post("/upload-letterboxd") #upload letterboxd ratings csv to your account
def upload_letterboxd(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user)
):
    print("UPLOAD ENDPOINT HIT")
    
    if not file.filename.endswith(".csv"): #validate file type
        raise HTTPException(status_code=400, detail="Only CSV files allowed")

    content = file.file.read()
    if len(content) > 2_000_000:
        raise HTTPException(status_code=400, detail="File too large")

    text = content.decode("utf-8", errors="ignore")
    reader = csv.reader(io.StringIO(text))
    
    header = next(reader, None) #validate header
    print("RAW HEADER:", header)

    normalized = [h.strip().lstrip("\ufeff") for h in header] #remove whitespace + extras

    expected = ["Date", "Name", "Year", "Letterboxd URI", "Rating"]

    if normalized[:5] != expected: #ensure correct file
        raise HTTPException(status_code=400, detail=f"Invalid Letterboxd CSV format. Got: {normalized}")

    #parse rows
    rows = []
    for row in reader:
        if not row or len(row) < 3:
            continue
        name = row[1].strip()
        year = int(row[2])
        rating = float(row[4])
        rows.append((name, year, rating))

    conn = get_db()
    cur = conn.cursor()

    try:
        for name, year, rating in rows:
            print(f"Processing: {name} ({year}) — Rating: {rating}")

            #try to fetch TMDB ID FIRST
            tmdb_id = fetch_tmdb_id(name, year)

            if not tmdb_id:
                print(f" → SKIPPED: No TMDB match for {name} ({year})")
                continue  # skip this movie entirely

            #insert movie with TMDB ID
            cur.execute("""
                INSERT INTO movies (title, year, tmdb_id)
                VALUES (%s, %s, %s)
                ON CONFLICT (title, year) DO UPDATE SET tmdb_id = EXCLUDED.tmdb_id
                RETURNING movie_id
            """, (name, year, tmdb_id))

            movie_id = cur.fetchone()[0]
            print(f" → Movie ID: {movie_id}, TMDB ID: {tmdb_id}")

            #insert/update rating
            cur.execute("""
                INSERT INTO ratings (user_id, movie_id, rating)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, movie_id) DO UPDATE SET rating = EXCLUDED.rating
            """, (user_id, movie_id, rating))
            print(f" → Rating saved for user {user_id}")

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to process CSV: {str(e)}")
    finally:
        cur.close()
        conn.close()

    return {"status": "ok"}

@app.get("/seen") #get list of movies that the logged in user has seen for filtering
def get_seen_movies(user_id: int = Depends(get_current_user)):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT m.tmdb_id
            FROM ratings r
            JOIN movies m ON r.movie_id = m.movie_id
            WHERE r.user_id = %s
        """, (user_id,))
        rows = cur.fetchall()
        return [r[0] for r in rows]
    finally:
        cur.close()
        conn.close()

@app.get("/recommend") #recommendation query
def recommend(ids: str = Query(...)):
    try:
        tmdb_ids = [int(x) for x in ids.split(",") if x.strip()]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ids parameter")

    conn = get_db()
    cur = conn.cursor()

    try:
        #convert tmdb_id to movie_id
        cur.execute("""
            SELECT movie_id
            FROM movies
            WHERE tmdb_id = ANY(%s) AND tmdb_id IS NOT NULL
        """, (tmdb_ids,))
        internal_ids = [row[0] for row in cur.fetchall()]

        if not internal_ids:
            return []

        #ALGORITHM REDACTED
        #Adds together recommendations based on other users, adding a tally to each movie approved by the agorithm per appearence across all relevent users

        tally_rows = cur.fetchall()  #list of (movie_id, tally, global_positive)
        if not tally_rows:
            return []

        #map movie_id to tally and preserve order
        movie_order = [row[0] for row in tally_rows]
        tally_map = {row[0]: row[1] for row in tally_rows}

        #return tmdb_ids + titles + tally, preserving order
        cur.execute("""
            SELECT movie_id, tmdb_id, title
            FROM movies
            WHERE movie_id = ANY(%s)
        """, (movie_order,))

        rows = cur.fetchall()  #unsorted
        movie_info = {r[0]: {"tmdb_id": r[1], "title": r[2]} for r in rows}

        results = []
        for mid in movie_order:
            info = movie_info.get(mid)
            if not info:
                continue
            results.append({
                "tmdb_id": info["tmdb_id"],
                "title": info["title"],
                "tally": tally_map.get(mid, 0)
            })

        return results
    finally:
        cur.close()
        conn.close()