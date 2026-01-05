from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# --- CORS SETUP (Crucial for React connection) ---
# This allows requests from your React app running on localhost:3000
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

# --- DATA MODEL ---
class UserInput(BaseModel):
    message: str

class BotResponse(BaseModel):
    response: str

@app.post("/chat")
def chat(user_input: UserInput):
    # Get the user's message
    user_message = user_input.message
    
    
    
    bot_reply = f"You said: {user_message}. How can I help you with that?"
    
    return {"response": bot_reply}


# --- ROOT ENDPOINT (Just for testing) ---
@app.get("/")
def read_root():
    return {"status": "Backend is running"}