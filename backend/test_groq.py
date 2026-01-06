from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Test with llama-3.3-70b (best free model)
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "user", "content": "Say hello in a friendly way"}
    ],
    temperature=0.7,
    max_tokens=100
)

print(response.choices[0].message.content)