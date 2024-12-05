import os
from dotenv import load_dotenv
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from app.models.user import User

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = AsyncIOMotorClient(MONGO_URI)
db = client["lingua-main"]
users = db["users"]
chats = db["chats"]
progress = db["progress"]
tests = db["tests"]

def get_users():
    return users

def get_chats():
    return chats

async def create_chat(chat_data: dict) -> str:
    result = await chats.insert_one(chat_data)
    return str(result.inserted_id)

async def get_chat(chat_id: str):
    try:
        if not chat_id:
            raise ValueError("Chat ID cannot be empty")
            
        # Convert string ID to ObjectId
        chat_id_obj = ObjectId(chat_id) if isinstance(chat_id, str) else chat_id
        
        # Find chat document
        chat = await chats.find_one({"_id": chat_id_obj})
        
        if chat:
            # Convert ObjectId to string for serialization
            chat['_id'] = str(chat['_id'])
            return chat
            
        return None
        
    except Exception as e:
        print(f"Error getting chat {chat_id}: {str(e)}")
        raise e

async def update_chat(chat_id: str, update_data: dict):
    try:
        # Convert string ID to ObjectId for MongoDB
        chat_id_obj = ObjectId(chat_id)
        
        # Validate update data
        if not update_data:
            raise ValueError("Update data cannot be empty")
            
        # Perform update
        result = await chats.update_one(
            {"_id": chat_id_obj},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            print(f"No document updated for chat_id: {chat_id}")
            return False
            
        return True
        
    except Exception as e:
        print(f"Error updating chat {chat_id}: {str(e)}")
        raise e

async def list_user_chats(user_id: str):
    cursor = chats.find({"user_id": user_id})
    return await cursor.to_list(length=None)

async def get_user_progress(user_id: str, language: str):
    return await progress.find_one({"user_id": user_id, "language": language}, {'_id': 0})

async def update_user_progress(progress_data: dict):
    return await progress.update_one(
        {"user_id": progress_data["user_id"], "language": progress_data["language"]},
        {"$set": progress_data},
        upsert=True
    )

async def create_user(user: User) -> str:
    result = await users.insert_one(user.dict())
    return str(result.inserted_id)

async def get_user_by_firebase_uid(firebase_uid: str):
    return await users.find_one({"firebase_uid": firebase_uid})

async def update_user(firebase_uid: str, update_data: dict):
    await users.update_one(
        {"firebase_uid": firebase_uid},
        {"$set": update_data}
    )

async def delete_user(firebase_uid: str):
    await users.delete_one({"firebase_uid": firebase_uid})

async def create_test(test_data: dict) -> str:
    result = await tests.insert_one(test_data)
    return str(result.inserted_id)

async def get_test(test_id: str):
    if isinstance(test_id, str):
        test_id = ObjectId(test_id)
    return await tests.find_one({"_id": test_id})

async def list_user_tests(user_id: str):
    cursor = tests.find({"user_id": user_id})
    return await cursor.to_list(length=None)

async def update_test_results(test_id: str, results: dict):
    await tests.update_one(
        {"_id": ObjectId(test_id)},
        {"$set": {"results": results, "completed_at": datetime.now()}}
    )