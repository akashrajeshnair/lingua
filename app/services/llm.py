from fastapi import HTTPException
import google.generativeai as genai
import os
import json
from typing import List
from dotenv import load_dotenv
from app.models.chat import Message, Chat
from app.models.test import LanguageTest, TestQuestion

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

# app/services/gemini_service.py - Update existing
DIFFICULTY_PROMPTS = {
    "A1": "Use basic vocabulary and simple present tense. Keep sentences short.",
    "A2": "Use elementary vocabulary and simple past tense. Include basic questions.",
    "B1": "Use intermediate vocabulary. Mix different tenses.",
    "B2": "Use advanced vocabulary and complex sentence structures.",
    "C1": "Use sophisticated vocabulary and idioms.",
    "C2": "Use native-level language with cultural references."
}

async def generate_chat_response(message: str, language: str, level: str) -> str:
    difficulty_context = DIFFICULTY_PROMPTS.get(level, DIFFICULTY_PROMPTS["A2"])
    prompt = f"""You are a helpful language tutor teaching {language}.
    The level of the student is: {difficulty_context}
    Respond to: {message}.
    Any queries outside the scope of language learning
    should be responded to with: I'm not sure, let's focus on learning {language}."""
    
    response = await model.generate_content_async(prompt)
    return response.text

async def create_language_chat(user_id: str, language: str, initial_message: str, level: str = "A2") -> Chat:
    # Initialize a new chat session
    chat = Chat(
        user_id=user_id,
        language=language,
        level = level,
        title=f"{language} Learning Session: {initial_message}"
    )
    
    # Add user's first message
    user_message = Message(
        content=initial_message,
        role="user",
        language=language
    )
    
    # Get AI response
    ai_response = await generate_chat_response(initial_message, language, level)
    assistant_message = Message(
        content=ai_response,
        role="assistant",
        language=language
    )
    
    chat.messages.extend([user_message, assistant_message])
    return chat

async def generate_language_test(chat_history: List[dict], language: str, level: str, user_id: str, chat_id: str) -> LanguageTest:
    chat_content = "\n".join([msg["content"] for msg in chat_history])
    
    structured_prompt = f"""Create 3 multiple-choice questions in {language} based on this conversation.
    Return the response in this exact JSON format:
    {{
        "questions": [
            {{
                "question": "question text in english if the level is below B1, else question text in {language}",
                "options": ["option1", "option2", "option3", "option4"],
                "correct_answer": "exact text of correct option",
                "explanation": "explanation in English",
                "topic": "grammar/vocabulary topic"
            }},
            // ... more questions
        ]
    }}

    Context:
    {chat_content}
    
    Level: {level}
    Language: {language}"""

    try:
        response = await model.generate_content_async(structured_prompt)
        test_data = json.loads(response.text)
        
        questions = [
            TestQuestion(
                question=q["question"],
                options=q["options"],
                correct_answer=q["correct_answer"],
                explanation=q["explanation"],
                topic=q["topic"],
                difficulty=level
            ) for q in test_data["questions"]
        ]
        
        return LanguageTest(
            questions=questions,
            language=language,
            level=level,
            user_id=user_id,
            chat_id=chat_id
        )
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating test: {str(e)}"
        )
