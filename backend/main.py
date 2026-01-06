from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from typing import Optional, List
from datetime import datetime

load_dotenv()

app = FastAPI()

# --- CORS SETUP ---
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
    session_id: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str

class CreateSessionRequest(BaseModel):
    user_id: str

class UpdateSessionTitleRequest(BaseModel):
    title: str

# --- AUTH ENDPOINTS ---
@app.post("/register")
def register(user_data: RegisterRequest):
    try:
        response = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
            "options": {
                "email_redirect_to": None
            }
        })
        if response.user:
            if response.session:
                return {
                    "message": "User registered successfully",
                    "user": {"id": response.user.id, "email": response.user.email},
                    "session": {"access_token": response.session.access_token}
                }
            else:
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

# --- CHAT SESSION ENDPOINTS ---
@app.post("/sessions")
def create_session(request: CreateSessionRequest):
    """Create a new chat session"""
    try:
        print(f"Creating session for user: {request.user_id}")  # Debug log
        
        response = supabase.table("chat_sessions").insert({
            "user_id": request.user_id,
            "title": "New Chat",
        }).execute()
        
        print(f"Response: {response}")  # Debug log
        
        if response.data and len(response.data) > 0:
            return {"session": response.data[0]}
        else:
            raise HTTPException(status_code=500, detail=f"Failed to create session. Response: {response}")
    except Exception as e:
        print(f"Error creating session: {str(e)}")  # Debug log
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/sessions/{user_id}")
def get_sessions(user_id: str):
    """Get all chat sessions for a user"""
    try:
        print(f"Fetching sessions for user: {user_id}")  # Debug log
        
        response = supabase.table("chat_sessions")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("updated_at", desc=True)\
            .execute()
        
        print(f"Found {len(response.data)} sessions")  # Debug log
        
        sessions = []
        for session in response.data:
            # Get message count for each session
            msg_response = supabase.table("chat_messages")\
                .select("id", count="exact")\
                .eq("session_id", session["id"])\
                .execute()
            
            sessions.append({
                "id": session["id"],
                "title": session["title"],
                "created_at": session["created_at"],
                "updated_at": session["updated_at"],
                "message_count": msg_response.count or 0
            })
        
        return {"sessions": sessions}
    except Exception as e:
        print(f"Error fetching sessions: {str(e)}")  # Debug log
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/sessions/{session_id}/messages")
def get_session_messages(session_id: str):
    """Get all messages for a specific session"""
    try:
        response = supabase.table("chat_messages")\
            .select("*")\
            .eq("session_id", session_id)\
            .order("created_at", desc=False)\
            .execute()
        
        return {"messages": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    """Delete a chat session and all its messages"""
    try:
        # Messages will be automatically deleted due to CASCADE
        response = supabase.table("chat_sessions")\
            .delete()\
            .eq("id", session_id)\
            .execute()
        
        return {"message": "Session deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/sessions/{session_id}/title")
def update_session_title(session_id: str, request: UpdateSessionTitleRequest):
    """Update chat session title"""
    try:
        response = supabase.table("chat_sessions")\
            .update({"title": request.title, "updated_at": datetime.utcnow().isoformat()})\
            .eq("id", session_id)\
            .execute()
        
        return {"message": "Title updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- CHAT ENDPOINTS ---
@app.post("/chat")
def chat(user_input: UserInput):
    try:
        user_message = user_input.message
        user_id = user_input.user_id
        session_id = user_input.session_id
        
        # If no session_id provided, create a new session
        if not session_id:
            session_response = supabase.table("chat_sessions").insert({
                "user_id": user_id,
                "title": user_message[:50] + ("..." if len(user_message) > 50 else ""),
            }).execute()
            session_id = session_response.data[0]["id"]
        
        # Simple bot response
        bot_reply = f"You said: {user_message}. How can I help you with that?"
        
        # Save user message to database
        supabase.table("chat_messages").insert({
            "session_id": session_id,
            "user_id": user_id,
            "message": user_message,
            "sender": "user"
        }).execute()
        
        # Save bot response to database
        supabase.table("chat_messages").insert({
            "session_id": session_id,
            "user_id": user_id,
            "message": bot_reply,
            "sender": "bot"
        }).execute()
        
        # Update session's updated_at timestamp
        supabase.table("chat_sessions")\
            .update({"updated_at": datetime.utcnow().isoformat()})\
            .eq("id", session_id)\
            .execute()
        
        # Auto-generate title from first message if still "New Chat"
        session_data = supabase.table("chat_sessions").select("title").eq("id", session_id).execute()
        if session_data.data and session_data.data[0]["title"] == "New Chat":
            new_title = user_message[:50] + ("..." if len(user_message) > 50 else "")
            supabase.table("chat_sessions")\
                .update({"title": new_title})\
                .eq("id", session_id)\
                .execute()
        
        return {"response": bot_reply, "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- ROOT ENDPOINT ---
@app.get("/")
def read_root():
    return {"status": "Backend is running"}