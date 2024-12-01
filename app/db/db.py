import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.collection import Collection
from bson import ObjectId
from app.models.user import User

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = AsyncIOMotorClient(MONGO_URI)
db = client["lingua-main"]
users = db["users"]
chats = db["chats"]
progress = db["progress"]

def get_users():
    return users

def get_chats():
    return chats

async def create_chat(chat_data: dict) -> str:
    result = await chats.insert_one(chat_data)
    return str(result.inserted_id)

async def get_chat(chat_id: str):
    return await chats.find_one({"_id": chat_id})

async def update_chat(chat_id: str, update_data: dict):
    await chats.update_one(
        {"_id": chat_id},
        {"$set": update_data}
    )

async def list_user_chats(user_id: str):
    cursor = chats.find({"user_id": user_id})
    return await cursor.to_list(length=None)

async def get_user_progress(user_id: str, language: str):
    return await progress.find_one({"user_id": user_id, "language": language})

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