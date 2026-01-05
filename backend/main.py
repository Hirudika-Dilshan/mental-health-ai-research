from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

app = FastAPI()

# --- CORS SETUP (Crucial for React connection) ---
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SUPABASE SETUP ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- DATA MODELS ---
class UserInput(BaseModel):
    message: str
    user_id: str

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str

class BotResponse(BaseModel):
    response: str

# --- AUTH ENDPOINTS ---
@app.post("/register")
def register(user_data: RegisterRequest):
    try:
        # Sign up with email confirmation disabled (for development)
        # If email confirmation is enabled, user will need to confirm email first
        response = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
            "options": {
                "email_redirect_to": None
            }
        })
        if response.user:
            # Check if email confirmation is required
            if response.session:
                # User is automatically logged in (email confirmation disabled)
                return {
                    "message": "User registered successfully",
                    "user": {"id": response.user.id, "email": response.user.email},
                    "session": {"access_token": response.session.access_token}
                }
            else:
                # Email confirmation required
                return {
                    "message": "User registered. Please check your email to confirm your account.",
                    "user": {"id": response.user.id, "email": response.user.email},
                    "requires_confirmation": True
                }
        else:
            raise HTTPException(status_code=400, detail="Registration failed")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/login")
def login(user_data: LoginRequest):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": user_data.email,
            "password": user_data.password
        })
        if response.user:
            return {
                "message": "Login successful",
                "user": {"id": response.user.id, "email": response.user.email},
                "session": {"access_token": response.session.access_token}
            }
        else:
            raise HTTPException(status_code=401, detail="Login failed")
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

# --- CHAT ENDPOINTS ---
@app.post("/chat")
def chat(user_input: UserInput):
    try:
        user_message = user_input.message
        user_id = user_input.user_id
        
        # Simple bot response
        bot_reply = f"You said: {user_message}. How can I help you with that?"
        
        # Save user message to database
        supabase.table("chat_messages").insert({
            "user_id": user_id,
            "message": user_message,
            "sender": "user"
        }).execute()
        
        # Save bot response to database
        supabase.table("chat_messages").insert({
            "user_id": user_id,
            "message": bot_reply,
            "sender": "bot"
        }).execute()
        
        return {"response": bot_reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat/history/{user_id}")
def get_chat_history(user_id: str):
    try:
        response = supabase.table("chat_messages").select("*").eq("user_id", user_id).order("created_at", desc=False).execute()
        return {"messages": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- ROOT ENDPOINT ---
@app.get("/")
def read_root():
    return {"status": "Backend is running"}