from motor.motor_asyncio import AsyncIOMotorClient # type: ignore
import os

MONGO_URI = "mongodb://localhost:27017"  # Đổi thành URI MongoDB nếu cần
DB_NAME = "StudyFlow"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
users_collection = db["users"]
