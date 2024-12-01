from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.models.chat import Chat, Message
from app.models.user import User
from app.services.llm import create_language_chat, generate_chat_response, generate_language_test
from app.db import create_chat, get_chat, list_user_chats, update_chat, update_user_progress, get_user_progress
from app.db import create_user, get_user_by_firebase_uid, update_user, delete_user


router = APIRouter()

@router.post("/users")
async def register_user(user: User):
    existing_user = await get_user_by_firebase_uid(user.firebase_uid)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    user_id = await create_user(user)
    return {"user_id": user_id}

@router.get("/users/{firebase_uid}")
async def get_user_profile(firebase_uid: str):
    user = await get_user_by_firebase_uid(firebase_uid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/users/{firebase_uid}")
async def update_user_profile(firebase_uid: str, user_update: dict):
    user = await get_user_by_firebase_uid(firebase_uid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await update_user(firebase_uid, user_update)
    return {"message": "User updated successfully"}

@router.delete("/users/{firebase_uid}")
async def delete_user_profile(firebase_uid: str):
    user = await get_user_by_firebase_uid(firebase_uid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await delete_user(firebase_uid)
    return {"message": "User deleted successfully"}


@router.post("/chats/create")
async def start_chat(user_id: str, language: str, initial_message: str):
    chat = await create_language_chat(user_id, language, initial_message)
    chat_id = await create_chat(chat.dict())
    return {"chat_id": chat_id, "chat": chat}

@router.post("/chats/{chat_id}/message")
async def send_message(chat_id: str, message: Message):
    chat = await get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=404, message="Chat not found")
    
    response = await generate_chat_response(
        message.content, 
        chat["language"],
        chat["level"]
    )
    
    progress_data = await get_user_progress(chat["user_id"], chat["language"])
    if not progress_data:
        progress_data = {
            "user_id": chat["user_id"],
            "language": chat["language"],
            "level": chat["level"],
            "xp_points": 0,
            "messages_sent": 0
        }
    
    progress_data["messages_sent"] += 1
    progress_data["xp_points"] += 10
    progress_data["last_interaction"] = datetime.now()
    
    await update_user_progress(progress_data)
    
    # Update chat with new messages
    assistant_message = Message(
        content=response,
        role="assistant",
        language=chat["language"]
    )
    
    await update_chat(
        chat_id,
        {
            "messages": chat["messages"] + [message.dict(), assistant_message.dict()],
            "updated_at": datetime.now()
        }
    )
    
    return {
        "response": response,
        "progress": progress_data
    }

@router.get("/chats/user/{user_id}")
async def get_user_chats(user_id: str):
    chats = await list_user_chats(user_id)
    return {"chats": chats}

@router.post("/chats/{chat_id}/generate-test")
async def generate_test_from_chat(chat_id: str):
    chat = await get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=404, message="Chat not found")
    
    test = await generate_language_test(
        chat["messages"],
        chat["language"],
        chat["level"]
    )
    
    # Update progress for test generation
    progress_data = await get_user_progress(chat["user_id"], chat["language"])
    progress_data["xp_points"] += 5
    await update_user_progress(progress_data)
    
    return test