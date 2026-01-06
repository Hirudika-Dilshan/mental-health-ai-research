from groq import Groq
import os
from typing import List, Dict

class LLMService:
    """Service for handling LLM interactions"""
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"
    
    def generate_response(self, 
                         system_prompt: str, 
                         conversation_history: List[Dict[str, str]], 
                         user_message: str) -> str:
        """
        Generate response using Groq
        
        Args:
            system_prompt: Instructions for the LLM
            conversation_history: Previous messages [{"role": "user/assistant", "content": "..."}]
            user_message: Current user message
            
        Returns:
            LLM response text
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"LLM Error: {str(e)}")
            return "I apologize, but I'm having trouble processing that. Could you please try again?"