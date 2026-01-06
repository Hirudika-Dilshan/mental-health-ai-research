from typing import Optional, Dict, List
from datetime import datetime
import json

class GAD7Protocol:
    """Manages GAD-7 conversation flow and scoring"""
    
    # GAD-7 Questions
    QUESTIONS = [
        {
            "number": 1,
            "text": "Over the last 2 weeks, have you been bothered by feeling nervous, anxious, or on edge?",
            "clarification": "'Nervous or on edge' means feeling restless, 'jumpy,' or easily startled. Over the last 2 weeks, have you been bothered by that feeling?",
            "examples": "Examples might include: feeling like you might spill your drink if someone surprises you, finding it hard to sit still, or feeling a 'pit' in your stomach."
        },
        {
            "number": 2,
            "text": "Over the last 2 weeks, have you been bothered by not being able to stop or control worrying?",
            "clarification": "This means having trouble stopping your worried thoughts even when you try. Have you experienced that?",
            "examples": "For example: lying awake thinking about problems, or your mind racing with worries you can't turn off."
        },
        {
            "number": 3,
            "text": "Have you been bothered by worrying too much about different things?",
            "clarification": "This means worrying about multiple different topics or situations. Have you experienced that?",
            "examples": "For example: worrying about work, family, health, money - many different things at once."
        },
        {
            "number": 4,
            "text": "Have you had trouble relaxing?",
            "clarification": "This means finding it difficult to feel calm or at ease. Have you experienced that?",
            "examples": "For example: feeling tense even when trying to rest, or unable to enjoy leisure time."
        },
        {
            "number": 5,
            "text": "Have you been bothered by being so restless that it is hard to sit still?",
            "clarification": "This means feeling the need to move around or fidget. Have you experienced that?",
            "examples": "For example: pacing, tapping your feet, or feeling uncomfortable staying in one place."
        },
        {
            "number": 6,
            "text": "Have you been bothered by becoming easily annoyed or irritable?",
            "clarification": "This means getting upset or frustrated more easily than usual. Have you experienced that?",
            "examples": "For example: snapping at people, feeling impatient, or being bothered by small things."
        },
        {
            "number": 7,
            "text": "Have you been bothered by feeling afraid as if something awful might happen?",
            "clarification": "This means having a sense of dread or fear about the future. Have you experienced that?",
            "examples": "For example: feeling like something bad is coming, or worrying that disaster is about to strike."
        }
    ]
    
    FREQUENCY_OPTIONS = {
        "not at all": 0,
        "several days": 1,
        "more than half the days": 2,
        "nearly every day": 3
    }
    
    # Crisis keywords
    CRISIS_KEYWORDS = [
        "suicide", "kill myself", "end my life", "want to die",
        "self harm", "hurt myself", "cut myself", "overdose"
    ]
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset protocol state"""
        self.current_question = 0  # 0 = screening, 1-7 = questions
        self.consent_given = False
        self.screening_passed = False
        self.screening_step = 0  # 0=age, 1=crisis, 2=done
        self.responses = {}
        self.awaiting_frequency = False
        self.last_question_answered = False
        self.confusion_count = 0
        self.total_score = 0
        self.completed = False
    
    def get_state(self) -> Dict:
        """Get current protocol state as dict"""
        return {
            "current_question": self.current_question,
            "consent_given": self.consent_given,
            "screening_passed": self.screening_passed,
            "screening_step": self.screening_step,
            "responses": self.responses,
            "awaiting_frequency": self.awaiting_frequency,
            "confusion_count": self.confusion_count,
            "total_score": self.total_score,
            "completed": self.completed
        }
    
    def load_state(self, state: Dict):
        """Load protocol state from dict"""
        self.current_question = state.get("current_question", 0)
        self.consent_given = state.get("consent_given", False)
        self.screening_passed = state.get("screening_passed", False)
        self.screening_step = state.get("screening_step", 0)
        self.responses = state.get("responses", {})
        self.awaiting_frequency = state.get("awaiting_frequency", False)
        self.confusion_count = state.get("confusion_count", 0)
        self.total_score = state.get("total_score", 0)
        self.completed = state.get("completed", False)
    
    def check_crisis(self, text: str) -> bool:
        """Check if user message contains crisis keywords"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.CRISIS_KEYWORDS)
    
    def get_age_screening(self) -> str:
        """Get age screening question"""
        return "Before we begin, I need to confirm: Are you 18 or older?\n\n(Please answer Yes or No)"
    
    def get_crisis_screening(self) -> str:
        """Get crisis screening question"""
        return "Thank you. One more important question: Are you currently in a crisis or feeling actively suicidal?\n\n(Please answer Yes or No)"
    
    def get_consent_message(self) -> str:
        """Get informed consent message"""
        return """Thank you for confirming. 

My purpose is to have a conversation with you. I am not a doctor, and this is not a diagnosis. This is only a screening tool. Your data will be used anonymously for research purposes.

Do you consent to participate? (Please answer Yes or No)"""
    
    def get_current_question(self) -> Optional[str]:
        """Get the current GAD-7 question"""
        if 1 <= self.current_question <= 7:
            return self.QUESTIONS[self.current_question - 1]["text"]
        return None
    
    def get_frequency_question(self) -> str:
        """Get the frequency scoring question"""
        return """Okay, how often have you been bothered by that over the last 2 weeks?

1. Not at all
2. Several days
3. More than half the days
4. Nearly every day

Please choose 1, 2, 3, or 4."""
    
    def calculate_severity(self) -> str:
        """Calculate severity level based on total score"""
        if self.total_score <= 4:
            return "minimal"
        elif self.total_score <= 9:
            return "mild"
        elif self.total_score <= 14:
            return "moderate"
        else:
            return "severe"
    
    def get_completion_message(self) -> str:
        """Get final message with score and recommendations"""
        severity = self.calculate_severity()
        
        base_message = f"""Thank you for completing the GAD-7 screening.

Your total score is: {self.total_score} out of 21
Severity level: {severity.upper()}

"""
        
        if severity == "minimal":
            return base_message + "Your responses suggest minimal anxiety symptoms. This is a good sign, but remember this is just a screening tool, not a diagnosis."
        
        elif severity == "mild":
            return base_message + "Your responses suggest mild anxiety symptoms. While this screening suggests some anxiety, only a healthcare professional can provide a proper assessment."
        
        elif severity == "moderate":
            return base_message + """Your responses suggest moderate anxiety symptoms. 

**IMPORTANT:** Talking to a qualified professional (like a doctor or counselor) about this could be very important. This screening suggests you may benefit from professional support."""
        
        else:  # severe
            return base_message + """Your responses suggest severe anxiety symptoms.

**IMPORTANT:** Your score is in the 'severe' range. I am not qualified to diagnose, but it is very important that you speak to a healthcare professional soon.

Please consider seeing a doctor or counselor. Here are some resources:
- 1926 (National Mental Health Helpline, 24/7)
- Ms Supeshala Rathnayaka (070 2211311)"""
    
    def get_crisis_message(self) -> str:
        """Get crisis protocol message"""
        return """I have detected keywords that indicate you may be in serious distress.

**I am an AI and not a crisis counselor.** Please contact a crisis hotline immediately:

- 1926 (National Mental Health Helpline, 24/7)
- Ms Supeshala Rathnayaka (070 2211311)

They can help you right now. Your safety is the most important thing."""