from fastapi import APIRouter, HTTPException
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from app.models.chat import Chat, Message
from app.models.user import User
from app.services.llm import create_language_chat, generate_chat_response, generate_language_test
from app.db.db import (create_chat, get_chat, list_user_chats, update_chat, 
    update_user_progress, get_user_progress, create_user, get_user_by_firebase_uid, update_user, delete_user,
    create_test, get_test, update_test_results, list_user_tests)


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
    try:
        user = await get_user_by_firebase_uid(firebase_uid)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Convert MongoDB _id to string and prepare response
        user['_id'] = str(user['_id'])
        return jsonable_encoder(user)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.put("/users/{firebase_uid}")
async def update_user_profile(firebase_uid: str, user_update: dict):
    try:
        user = await get_user_by_firebase_uid(firebase_uid)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        await update_user(firebase_uid, user_update)
        updated_user = await get_user_by_firebase_uid(firebase_uid)
        updated_user['_id'] = str(updated_user['_id'])
        return jsonable_encoder(updated_user)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.delete("/users/{firebase_uid}")
async def delete_user_profile(firebase_uid: str):
    try:
        user = await get_user_by_firebase_uid(firebase_uid)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        await delete_user(firebase_uid)
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/chats/create")
async def start_chat(user_id: str, language: str, initial_message: str, level: str = "A2"):
    chat = await create_language_chat(user_id, language, initial_message, level)
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

    # await update_chat(
    #     chat_id,
    #     {
    #         "messages": chat["messages"] + [message.dict(), assistant_message.dict()],
    #         "updated_at": datetime.now()
    #     }
    # )

    return {
        "response": response,
        "progress": progress_data
    }



@router.get("/chats/user/{user_id}")
async def get_user_chats(user_id: str):
    try:
        chats = await list_user_chats(user_id)
        
        # Convert ObjectIds to strings and format response
        formatted_chats = []
        for chat in chats:
            chat['_id'] = str(chat['_id'])
            formatted_chats.append(chat)
            
        return jsonable_encoder({"chats": formatted_chats})
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching chats: {str(e)}"
        )

# Update the route in routes.py
@router.post("/chats/{chat_id}/generate-test")
async def generate_test_from_chat(chat_id: str):
    chat = await get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    test = await generate_language_test(
        chat["messages"],
        chat["language"],
        chat["level"],
        chat["user_id"],
        str(chat["_id"])  # Convert ObjectId to string
    )
    
    # Save test to database
    test_id = await create_test(test.dict())
    
    # Update progress
    progress_data = await get_user_progress(chat["user_id"], chat["language"])
    if progress_data:
        progress_data["xp_points"] += 5
        await update_user_progress(progress_data)
    
    return {
        "test_id": test_id,
        "test": test
    }

@router.post("/tests/{test_id}/submit")
async def submit_test_results(test_id: str, results: dict):
    test = await get_test(test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
        
    await update_test_results(test_id, results)
    
    # Award XP for completing test
    progress_data = await get_user_progress(test["user_id"], test["language"])
    if progress_data:
        progress_data["xp_points"] += 20  # Bonus XP for completing test
        await update_user_progress(progress_data)
    
    return {"message": "Test results saved successfully"}

@router.get("/users/{user_id}/tests")
async def get_user_tests(user_id: str):
    try:
        tests = await list_user_tests(user_id)
        
        # Convert ObjectIds to strings and format response
        formatted_tests = []
        for test in tests:
            test['_id'] = str(test['_id'])
            formatted_tests.append(test)
            
        return jsonable_encoder({"tests": formatted_tests})
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching tests: {str(e)}"
        )