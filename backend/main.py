from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from typing import Optional, List
from datetime import datetime

from typing import Optional, List, Dict
from gad7_protocol import GAD7Protocol
from llm_service import LLMService
import json

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
        
        # Initialize services
        protocol = GAD7Protocol()
        llm = LLMService()
        
        # Create new session if none exists
        if not session_id:
            session_response = supabase.table("chat_sessions").insert({
                "user_id": user_id,
                "title": "GAD-7 Screening",
                "protocol_type": "GAD7",
                "protocol_state": json.dumps(protocol.get_state())
            }).execute()
            session_id = session_response.data[0]["id"]
        
        # Load existing protocol state
        else:
            session_data = supabase.table("chat_sessions")\
                .select("protocol_state, protocol_completed")\
                .eq("id", session_id)\
                .execute()
            
            if session_data.data:
                state = session_data.data[0].get("protocol_state")
                if state:
                    protocol.load_state(json.loads(state))
                
                # Check if protocol already completed
                if session_data.data[0].get("protocol_completed"):
                    bot_reply = "This screening has already been completed. Would you like to start a new screening session?"
                    
                    # Save messages
                    supabase.table("chat_messages").insert({
                        "session_id": session_id,
                        "user_id": user_id,
                        "message": user_message,
                        "sender": "user"
                    }).execute()
                    
                    supabase.table("chat_messages").insert({
                        "session_id": session_id,
                        "user_id": user_id,
                        "message": bot_reply,
                        "sender": "bot"
                    }).execute()
                    
                    return {"response": bot_reply, "session_id": session_id}
        
        # --- CRISIS CHECK ---
        if protocol.check_crisis(user_message):
            crisis_message = protocol.get_crisis_message()
            
            # Save messages
            supabase.table("chat_messages").insert({
                "session_id": session_id,
                "user_id": user_id,
                "message": user_message,
                "sender": "user"
            }).execute()
            
            supabase.table("chat_messages").insert({
                "session_id": session_id,
                "user_id": user_id,
                "message": crisis_message,
                "sender": "bot"
            }).execute()
            
            # Mark session as completed (crisis termination)
            update_protocol_state(session_id, protocol.get_state(), completed=True)
            
            return {"response": crisis_message, "session_id": session_id, "crisis": True}
        
        # --- PROTOCOL FLOW ---
        # --- PROTOCOL FLOW ---
        bot_reply = ""
        
        # Step 1: Screening (Two-step process)
        if protocol.current_question == 0 and not protocol.screening_passed:
            
            # Initialize screening_step if not exists
            if not hasattr(protocol, 'screening_step'):
                protocol.screening_step = 0
            
            # Step 1a: Age screening
            if protocol.screening_step == 0:
                # Check if this is first message
                msg_count = supabase.table("chat_messages")\
                    .select("id", count="exact")\
                    .eq("session_id", session_id)\
                    .execute()
                
                if msg_count.count == 0:
                    # First message - ask age
                    bot_reply = protocol.get_age_screening()
                else:
                    # Parse age response
                    user_lower = user_message.lower().strip()
                    
                    if "yes" in user_lower or "yeah" in user_lower or "yep" in user_lower:
                        # 18+ confirmed, move to crisis question
                        protocol.screening_step = 1
                        bot_reply = protocol.get_crisis_screening()
                    elif "no" in user_lower or "nope" in user_lower:
                        # Under 18 - terminate
                        bot_reply = "I'm sorry, but you must be 18 or older to participate in this screening. Thank you for your interest."
                        update_protocol_state(session_id, protocol.get_state(), completed=True)
                    else:
                        # Unclear - ask again
                        bot_reply = "I need a clear Yes or No answer. Are you 18 or older?"
            
            # Step 1b: Crisis screening
            elif protocol.screening_step == 1:
                user_lower = user_message.lower().strip()
                
                if "no" in user_lower or "nope" in user_lower:
                    # Not in crisis - proceed to consent
                    protocol.screening_passed = True
                    protocol.screening_step = 2
                    bot_reply = protocol.get_consent_message()
                elif "yes" in user_lower or "yeah" in user_lower or "yep" in user_lower:
                    # In crisis - show crisis message and terminate
                    bot_reply = protocol.get_crisis_message()
                    update_protocol_state(session_id, protocol.get_state(), completed=True)
                else:
                    # Unclear - ask again
                    bot_reply = "I need a clear Yes or No answer. Are you currently in a crisis or feeling actively suicidal?"
        # Step 2: Consent
        elif protocol.screening_passed and not protocol.consent_given:
            if "yes" in user_message.lower():
                protocol.consent_given = True
                protocol.current_question = 1
                bot_reply = f"Thank you for consenting. Let's begin.\n\n{protocol.get_current_question()}"
            else:
                bot_reply = "I understand. Thank you for your time. You can close this conversation whenever you're ready."
                update_protocol_state(session_id, protocol.get_state(), completed=True)
        
        # Step 3: Questions 1-7
        elif 1 <= protocol.current_question <= 7:
            if not protocol.awaiting_frequency:
                # User just answered yes/no to symptom
                # Use LLM to interpret response
                conversation_history = load_conversation_context(session_id)
                system_prompt = get_system_prompt(protocol.get_state())
                
                # Ask LLM if this was a yes/no/unclear response
                interpretation_prompt = f"""The user was asked: "{protocol.get_current_question()}"

They responded: "{user_message}"

Respond with ONLY one word:
- "YES" if they indicated they experienced this symptom
- "NO" if they indicated they did not experience this symptom  
- "UNCLEAR" if you cannot determine their answer

ONE WORD ONLY:"""
                
                interpretation = llm.generate_response(
                    system_prompt="You are a response classifier. Respond with only YES, NO, or UNCLEAR.",
                    conversation_history=[],
                    user_message=interpretation_prompt
                ).strip().upper()
                
                if "YES" in interpretation:
                    protocol.awaiting_frequency = True
                    bot_reply = protocol.get_frequency_question()
                
                elif "NO" in interpretation:
                    # Score 0, move to next question
                    save_gad7_response(
                        session_id, user_id, 
                        protocol.current_question,
                        protocol.get_current_question(),
                        user_message, 0
                    )
                    
                    protocol.current_question += 1
                    if protocol.current_question <= 7:
                        bot_reply = protocol.get_current_question()
                    else:
                        # All questions done
                        protocol.completed = True
                        bot_reply = protocol.get_completion_message()
                        update_protocol_state(session_id, protocol.get_state(), 
                                            protocol.total_score, completed=True)
                
                else:
                    # Unclear - use LLM to ask for clarification
                    bot_reply = llm.generate_response(
                        system_prompt=system_prompt,
                        conversation_history=conversation_history[-4:],  # Last 2 exchanges
                        user_message=user_message
                    )
            
            else:
                # User is providing frequency (0-3)
                # Parse their response
                score = None
                user_msg_lower = user_message.lower()
                
                if "1" in user_message or "not at all" in user_msg_lower:
                    score = 0
                elif "2" in user_message or "several" in user_msg_lower:
                    score = 1
                elif "3" in user_message or "more than half" in user_msg_lower or "half the days" in user_msg_lower:
                    score = 2
                elif "4" in user_message or "nearly every" in user_msg_lower or "every day" in user_msg_lower:
                    score = 3
                
                if score is not None:
                    # Save response
                    save_gad7_response(
                        session_id, user_id,
                        protocol.current_question,
                        protocol.get_current_question(),
                        user_message, score
                    )
                    
                    protocol.total_score += score
                    protocol.awaiting_frequency = False
                    protocol.current_question += 1
                    
                    if protocol.current_question <= 7:
                        bot_reply = f"Thank you. Next question:\n\n{protocol.get_current_question()}"
                    else:
                        # All done!
                        protocol.completed = True
                        bot_reply = protocol.get_completion_message()
                        update_protocol_state(session_id, protocol.get_state(),
                                            protocol.total_score, completed=True)
                else:
                    # Couldn't parse - ask again
                    bot_reply = "I didn't quite catch that. Please choose a number from 1 to 4:\n\n" + protocol.get_frequency_question()
        
        # Save user message
        supabase.table("chat_messages").insert({
            "session_id": session_id,
            "user_id": user_id,
            "message": user_message,
            "sender": "user"
        }).execute()
        
        # Save bot response
        supabase.table("chat_messages").insert({
            "session_id": session_id,
            "user_id": user_id,
            "message": bot_reply,
            "sender": "bot"
        }).execute()
        
        # Update protocol state
        update_protocol_state(session_id, protocol.get_state(), protocol.total_score)
        
        # Update session title if still "New Chat" or "GAD-7 Screening"
        session_data = supabase.table("chat_sessions").select("title").eq("id", session_id).execute()
        if session_data.data and session_data.data[0]["title"] in ["New Chat", "GAD-7 Screening"]:
            new_title = f"GAD-7 Screening - {datetime.utcnow().strftime('%b %d, %Y')}"
            supabase.table("chat_sessions")\
                .update({"title": new_title})\
                .eq("id", session_id)\
                .execute()
        
        return {"response": bot_reply, "session_id": session_id}
        
    except Exception as e:
        print(f"Error in chat: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
# --- ROOT ENDPOINT ---
@app.get("/")
def read_root():
    return {"status": "Backend is running"}

# --- PROTOCOL HELPER FUNCTIONS ---

def get_system_prompt(protocol_state: Dict) -> str:
    """Generate system prompt based on protocol state"""
    
    base_prompt = """You are a compassionate mental health screening assistant conducting a GAD-7 (Generalized Anxiety Disorder) assessment.

CRITICAL RULES:
1. You are NOT a therapist or doctor. You are a screening tool.
2. NEVER diagnose or give medical advice
3. Follow the exact GAD-7 protocol provided
4. Be conversational but professional
5. If user is confused, provide clarification gently
6. If user goes off-topic, gently guide them back
7. Watch for crisis keywords and respond appropriately

YOUR TONE: Warm, supportive, non-judgmental, like a caring healthcare worker."""

    if not protocol_state.get("consent_given"):
        return base_prompt + "\n\nCurrent task: Obtain informed consent for the screening."
    
    elif protocol_state.get("awaiting_frequency"):
        return base_prompt + "\n\nCurrent task: Get the frequency score (0-3) for the last question asked."
    
    else:
        current_q = protocol_state.get("current_question", 0)
        if 1 <= current_q <= 7:
            return base_prompt + f"\n\nCurrent task: Ask GAD-7 question {current_q} and determine if they experienced this symptom (yes/no/unsure)."
    
    return base_prompt


def load_conversation_context(session_id: str) -> List[Dict]:
    """Load conversation history from database"""
    try:
        response = supabase.table("chat_messages")\
            .select("message, sender")\
            .eq("session_id", session_id)\
            .order("created_at", desc=False)\
            .execute()
        
        context = []
        for msg in response.data:
            role = "user" if msg["sender"] == "user" else "assistant"
            context.append({"role": role, "content": msg["message"]})
        
        return context
    except Exception as e:
        print(f"Error loading context: {e}")
        return []


def save_gad7_response(session_id: str, user_id: str, question_num: int, 
                       question_text: str, user_response: str, score: Optional[int]):
    """Save individual GAD-7 response to database"""
    try:
        supabase.table("gad7_responses").insert({
            "session_id": session_id,
            "user_id": user_id,
            "question_number": question_num,
            "question_text": question_text,
            "user_response": user_response,
            "score": score
        }).execute()
    except Exception as e:
        print(f"Error saving GAD-7 response: {e}")


def update_protocol_state(session_id: str, protocol_state: Dict, 
                          total_score: int = None, completed: bool = False):
    """Update protocol state in database"""
    try:
        update_data = {
            "protocol_state": json.dumps(protocol_state),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if total_score is not None:
            update_data["total_score"] = total_score
            update_data["severity_level"] = GAD7Protocol().calculate_severity() if total_score else None
        
        if completed:
            update_data["protocol_completed"] = True
        
        supabase.table("chat_sessions")\
            .update(update_data)\
            .eq("id", session_id)\
            .execute()
    except Exception as e:
        print(f"Error updating protocol state: {e}")