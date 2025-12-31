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
# This defines the structure of data we expect from React
class UserInput(BaseModel):
    message: str

# --- API ENDPOINT ---
@app.post("/analyze")
async def analyze_mental_health(input_data: UserInput):
    # This is where your AI Logic will go later
    print(f"Received from frontend: {input_data.message}")
    
    # Mock response for now
    return {
        "reply": "I received your message!",
        "sentiment": "neutral", 
        "original_message": input_data.message
    }

# --- ROOT ENDPOINT (Just for testing) ---
@app.get("/")
def read_root():
    return {"status": "Backend is running"}