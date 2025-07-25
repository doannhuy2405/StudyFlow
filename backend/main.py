import jwt
import os
import bcrypt 
import uvicorn
import firebase_admin
import uuid
import asyncio
import mimetypes
import pytz # type: ignore
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Depends, Request, APIRouter, UploadFile, File, APIRouter
from pymongo import MongoClient, ReturnDocument, errors, DESCENDING
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from firebase_admin import auth, credentials
from datetime import datetime, timedelta, timezone
from bson import ObjectId, json_util
from models import UserLogin
from fastapi.responses import FileResponse, JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient # type: ignore
from collections import defaultdict
from typing import List, Optional, Any
from bson.errors import InvalidId
from bson import ObjectId
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from apscheduler.schedulers.asyncio import AsyncIOScheduler # type: ignore
from apscheduler.triggers.cron import CronTrigger # type: ignore


#-----------------------------------------------------Database-----------------------------------------------
# Load biến môi trường
load_dotenv()

# Kết nối MongoDB
MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
if not MONGO_URI:
    raise ValueError("MONGO_URI không được tìm thấy trong biến môi trường!")

try:
    
    # Database chính cho người dùng
    db = client["mydatabase"]
    
    # Database riêng cho admin
    db_admin = client["admin"]      
    
    # Collection users
    users_collection = db["users"]
    
    # Collection admin
    admin_collection = db_admin["admin"]
    adminstats_collection = db_admin["adminstats"]
    
    # Collection hệ thống
    topics_collection = db["topics"]
    lessons_collection = db["lessons"]
    dailylogs_collection = db["dailylogs"]
    reminders_collection = db["reminders"]
    settings_collection = db["settings"]
    userstats_collection = db["userstats"]
    studysessions_collection = db["studysessions"]
    activitylogs_collection = db["activitylogs"]
    notifications_collection = db["notifications"]
    reminderlogs_collection = db["reminderlogs"]
    
    print("✅ Kết nối MongoDB thành công!")
except Exception as e:
    raise ValueError(f"Lỗi kết nối MongoDB: {e}")

#-------------------------------Authentication APIs-------------------------------------------------

# Múi giờ Việt Nam
scheduler = AsyncIOScheduler(timezone="Asia/Ho_Chi_Minh")
VN_TZ = timezone(timedelta(hours=7))

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                request.state.user_id = payload.get("user_id")
                request.state.role = payload.get("role")
            except JWTError:
                request.state.user_id = None
                request.state.role = None
        else:
            request.state.user_id = None
            request.state.role = None

        response = await call_next(request)
        return response

# Xóa app cũ nếu tồn tại
if firebase_admin._DEFAULT_APP_NAME in firebase_admin._apps:
    firebase_admin.delete_app(firebase_admin.get_app())

# Khởi tạo FastAPI
app = FastAPI()

# Gắn middleware
app.add_middleware(AuthMiddleware)


# Lấy đường dẫn từ biến môi trường
firebase_cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if not firebase_cred_path:
    raise ValueError("⚠️ Không tìm thấy biến môi trường GOOGLE_APPLICATION_CREDENTIALS!")

# Khởi tạo Firebase Admin SDK
cred = credentials.Certificate(firebase_cred_path)
firebase_admin.initialize_app(cred)

# Thêm vào startup
print("🔥 Khởi tạo Firebase...")
print(f"🔹 Path: {firebase_cred_path}")
print(f"🔹 App: {firebase_admin.get_app().name}")

# Schema nhận token từ frontend
class GoogleLoginRequest(BaseModel):
    token: str

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# ALGORITHM
ALGORITHM = "HS256"

# Load SECRET_KEY
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY không được tìm thấy trong biến môi trường!")

# Schema dữ liệu người dùng
class UserRegister(BaseModel):
    fullname: str
    email: str
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

# Hàm hash password
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Hàm kiểm tra password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        print("🔹 Kiểm tra mật khẩu:", plain_password)
        print("🔹 Mật khẩu hash:", hashed_password)

        # Kiểm tra xem hashed_password có bị mất ký tự không
        if not hashed_password.startswith("$2b$"):
            print("⚠️ Mật khẩu hash không hợp lệ!")
            return False

        result = bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        print("🔹 Kết quả kiểm tra:", result)
        return result
    except Exception as e:
        print("❌ Lỗi khi kiểm tra mật khẩu:", e)
        return False


# Hàm tạo JWT token
def create_token(data: dict, expires_delta: timedelta = timedelta(hours=24)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")


# API Đăng ký người dùng
@app.post("/auth/register")
async def register(user: UserRegister):
    print("Dữ liệu từ frontend:", user.dict())

    # Kiểm tra email và username đã tồn tại chưa - THÊM AWAIT
    if await users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email đã tồn tại!")
    if await users_collection.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username đã tồn tại!")

    # Băm mật khẩu
    hashed_password = hash_password(user.password)
    
    new_user = {
        "fullname": user.fullname,
        "email": user.email,
        "username": user.username,
        "password": hashed_password,
        "created_at": datetime.utcnow(),  # Thêm ngày tạo
        "updated_at": datetime.utcnow(),  # Thêm ngày cập nhật
        "roles": ["user"],  # Thêm role mặc định
        "active": True      # Kích hoạt tài khoản
    }
    
    # THÊM AWAIT cho insert_one
    result = await users_collection.insert_one(new_user)
    
    # Tạo Token với đầy đủ thông tin hơn
    token_data = {
        "user_id": str(result.inserted_id),  # Thêm user_id
        "username": user.username,
        "email": user.email,
        "roles": ["user"]
    }
    token = create_token(token_data)

    return {
        "success": True,  # Thêm trạng thái thành công
        "message": "Đăng ký thành công!",
        "token": token,
        "user": {
            "id": str(result.inserted_id),
            "username": user.username,
            "email": user.email,
            "fullname": user.fullname,
            "role": "user"
        }
    }


# API Đăng nhập người dùng
@app.post("/auth/login")
async def login(user: UserLogin):
    print("Đăng nhập:", user.dict())

    # Kiểm tra tài khoản admin
    admin = await admin_collection.find_one({"username": user.username})
    if admin and verify_password(user.password, admin["password"]):
        token_data = {"username": admin["username"], "role": "admin"}
        token = create_token(token_data)
        return {
            "token": token,
            "user": {
                "username": admin["username"],
                "fullname": admin.get("fullname", "Admin"),
                "role": "admin"
            }
        }

    # Kiểm tra tài khoản người dùng thường
    db_user = await users_collection.find_one({"username": user.username})
    if db_user and verify_password(user.password, db_user["password"]):

        # Kiểm tra nếu tài khoản bị khóa
        if db_user.get("locked", False):
            raise HTTPException(status_code=403, detail="Tài khoản của bạn đã bị khóa")

        token_data = {
            "user_id": str(db_user["_id"]),
            "username": db_user["username"],
            "role": "user"
        }

        token = create_token(token_data)

        return {
            "token": token,
            "user": {
                "id": str(db_user["_id"]),
                "username": db_user["username"],
                "fullname": db_user.get("fullname", ""),
                "role": "user"
            }
        }

    raise HTTPException(status_code=400, detail="Sai tài khoản hoặc mật khẩu!")

    
# Endpoint kiểm tra thông tin 
@app.get("/auth/check-user-by-email/{email}")
async def check_user_by_email(email: str):
    user = users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/auth/check-user-by-uid/{uid}")
async def check_user_by_uid(uid: str):
    user = users_collection.find_one({"uid": uid})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user    
    
    
# API đăng nhập Google
@app.post("/auth/google-login")
async def google_login(request: Request):
    try:
        # 1. Lấy và xác thực token Google
        data = await request.json()
        id_token = data.get("token")
        if not id_token:
            raise HTTPException(status_code=400, detail="Thiếu token Google")

        decoded_token = auth.verify_id_token(id_token)
        email = decoded_token.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Token không hợp lệ")

        # 2. Tìm hoặc tạo user với đầy đủ thông tin BẮT BUỘC
        user_data = {
            "email": email,
            "fullname": decoded_token.get("name", email.split("@")[0]),
            "photo": decoded_token.get("picture", ""),
            "provider": "google",
            "last_login": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "roles": ["user"],  # THÊM ROLE MẶC ĐỊNH
            "active": True,     # KÍCH HOẠT TÀI KHOẢN
            "verified": True    # COI NHƯ ĐÃ XÁC THỰC EMAIL
        }

        result = await users_collection.find_one_and_update(
            {"email": email},
            {
                "$set": user_data,
                "$setOnInsert": {
                    "username": f"user_{ObjectId()}",  # USERNAME UNIQUE NGẪU NHIÊN
                    "created_at": datetime.utcnow()
                }
            },
            upsert=True,
            return_document=ReturnDocument.AFTER
        )

        # 3. Tạo token với đủ thông tin NHƯ ĐĂNG NHẬP THƯỜNG
        token_payload = {
            "user_id": str(result["_id"]),
            "username": result["username"],
            "email": email,
            "roles": ["user"],
            "provider": "google"
        }
        token = jwt.encode(token_payload, SECRET_KEY, algorithm="HS256")

        return {
            "success": True,
            "token": token,
            "user": {
                "id": str(result["_id"]),
                "username": result["username"],
                "email": email,
                "fullname": user_data["fullname"],
                "role": "user",
                "photo": user_data["photo"],
                "provider": "google"
            }
        }

    except Exception as e:
        print(f"[GOOGLE LOGIN ERROR] {str(e)}")
        raise HTTPException(status_code=500, detail="Lỗi đăng nhập bằng Google")
    

#Endpoint kiểm tra user
@app.get("/auth/debug/user/{email}")
async def debug_user(email: str):
    user = users_collection.find_one({"email": email})
    if not user:
        return {"error": "User not found"}
    return user


# Cấu hình OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Hàm giải mã token
def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError as e:
        print("❌ Lỗi giải mã token:", str(e))
        raise HTTPException(status_code=401, detail="Invalid token")
    

# API lấy thông tin người dùng
@app.get("/auth/profile")
async def get_user_profile(token: str = Depends(oauth2_scheme)):
    username = decode_token(token)
    
    user = await users_collection.find_one({"username": username})  
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "username": user.get("username", ""),
        "fullname": user.get("fullname", ""),
        "email": user.get("email", ""),
        "photo": user.get("photo", ""),
    }


# API lấy thông tin admin
@app.get("/auth/admin/profile")
async def get_admin_profile():
    admin = await admin_collection.find_one({"username": "admin"})
    
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    return {
        "fullname": admin.get("fullname", "Quản trị viên"),
        "username": admin.get("username", "admin"),
        "email": admin.get("email", "admin@studyflow.com"),
        "role": admin.get("role", "admin"),
        "created_at": admin.get("created_at", datetime.utcnow())
    }


# API cập nhật thông tin người dùng
@app.put("/auth/profile")
async def update_user_profile(request: Request, token: str = Depends(oauth2_scheme)):
    try:
        username = decode_token(token)
        user = await users_collection.find_one({"username": username}) 
        if not user:
            raise HTTPException(status_code=404, detail="Người dùng không tồn tại")

        data = await request.json()
        email = data.get("email")
        password = data.get("password")
        photo = data.get("photo")

        update_data = {}

        if email and email != user.get("email"):
            update_data["email"] = email
        if password:
            hashed_password = hash_password(password)
            if hashed_password != user.get("password"):
                update_data["password"] = hashed_password
        if photo and photo != user.get("photo"):
            update_data["photo"] = photo

        if not update_data:
            raise HTTPException(status_code=400, detail="Không có thay đổi để cập nhật")

        await users_collection.update_one({"username": username}, {"$set": update_data})  
        return {"message": "Cập nhật thông tin thành công"}
    except HTTPException as e:
        raise e
    except Exception as e:
        print("❌ Lỗi cập nhật:", e)
        raise HTTPException(status_code=500, detail="Lỗi server khi cập nhật thông tin người dùng")


#-------------------------------User APIs------------------------------------------------------

# Schema dữ liệu do chức năng người dùng thực hiện
class LessonItem(BaseModel):
    name: str
    note: Optional[str] = ''
    due_date: Optional[str] = ''
    status: str = "not_done"
    documents: List[dict] = []

class TopicCreate(BaseModel):
    name: str
    description: str
    lessons: List[LessonItem] = []


class HabitSetup(BaseModel):
    user_id: str
    study_days: list[str]
    rest_days: list[str]

class JournalCreate(BaseModel):
    user_id: str
    content: str

class EvaluationCreate(BaseModel):
    user_id: str
    rating: int
    comment: str

class ReminderSetting(BaseModel):
    time: str

class LessonCreate(BaseModel):
    name: str
    note: Optional[str] = ''
    due_date: Optional[str] = ''
    status: str = "not_done"
    documents: List[dict] = []

# Model cho tài liệu
class DocumentInfo(BaseModel):
    id: str
    original_name: str
    saved_name: str
    file_path: str
    content_type: str
    size: int
    uploaded_at: str

# Model cập nhật bài học (bổ sung documents)
class LessonUpdate(BaseModel):
    name: Optional[str] = None
    note: Optional[str] = None
    due_date: Optional[str] = None
    status: Optional[str] = None
    documents: Optional[List[DocumentInfo]] = None
    

def convert_objectid(doc):
    doc["_id"] = str(doc["_id"])
    if "user_id" in doc and isinstance(doc["user_id"], ObjectId):
        doc["user_id"] = str(doc["user_id"])
    if "lessons" in doc:
        for lesson in doc["lessons"]:
            if "_id" in lesson:
                lesson["_id"] = str(lesson["_id"])
            if "topic_id" in lesson and isinstance(lesson["topic_id"], ObjectId):
                lesson["topic_id"] = str(lesson["topic_id"])
    return doc


# Lấy danh sách chủ đề
@app.get("/topics")
async def get_topics(request: Request):
    user_id = request.state.user_id
    if not user_id:
        raise HTTPException(status_code=401, detail="Chưa xác thực người dùng")

    raw_topics = await topics_collection.find({"user_id": ObjectId(user_id)}).to_list(100)
    return [convert_objectid(topic) for topic in raw_topics]


# Tạo chủ đề học mới
@app.post("/topics")
async def create_topic(topic: TopicCreate, request: Request):
    print("Dữ liệu JSON nhận được:", await request.json())

    # Lấy user_id từ token request
    user_id = request.state.user_id
    if not user_id:
        raise HTTPException(status_code=401, detail="Chưa xác thực người dùng")

    try:
        user_obj_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="user_id không hợp lệ")

    # Chuyển sang dict, bỏ lessons
    topic_dict = topic.dict()
    lessons = topic_dict.pop("lessons", [])

    topic_dict["user_id"] = user_obj_id
    topic_dict["created_at"] = datetime.utcnow()

    # Thêm topic
    result = await topics_collection.insert_one(topic_dict)
    topic_id = result.inserted_id

    # Gán topic_id + user_id cho từng bài học rồi insert
    for lesson in lessons:
        if not lesson.get("name", "").strip():
            raise HTTPException(status_code=400, detail="Mỗi bài học phải có tên")
        
        lesson["topic_id"] = topic_id
        lesson["user_id"] = user_obj_id
        await lessons_collection.insert_one(lesson)

    return {"id": str(topic_id), "message": "Tạo chủ đề thành công"}


# Cập nhật thông tin chủ đề
@app.put("/topics/{id}")
async def update_topic(id: str, topic: TopicCreate):
    try:
        oid = ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID không hợp lệ")

    result = await topics_collection.update_one({"_id": oid}, {"$set": topic.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Không tìm thấy chủ đề")
    return {"msg": "Cập nhật thành công"}


# Xóa chủ đề học
@app.delete("/topics/{id}")
async def delete_topic(id: str):
    try:
        topic_id = ObjectId(id)
    except errors.InvalidId:
        raise HTTPException(status_code=400, detail="Invalid topic ID")

    # Xóa chủ đề
    result = await topics_collection.delete_one({"_id": topic_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Topic not found")

    # 👉 Xóa tất cả bài học thuộc chủ đề
    await lessons_collection.delete_many({"topic_id": topic_id})

    return {"msg": "Topic and associated lessons deleted"}



def serialize_lesson(lesson):
    lesson["id"] = str(lesson["_id"])
    lesson["topic_id"] = str(lesson["topic_id"])
    lesson["user_id"] = str(lesson["user_id"])
    del lesson["_id"]
    return lesson


# Lấy danh sách bài học trong chủ đề
@app.get("/topics/{topic_id}/lessons")
async def get_lessons(topic_id: str, request: Request): 
    user_id = request.state.user_id
    if not user_id:
        raise HTTPException(status_code=401, detail="Chưa xác thực người dùng")

    lessons = await lessons_collection.find({
        "topic_id": ObjectId(topic_id),
        "user_id": ObjectId(user_id)
    }).to_list(100)

    lessons = [serialize_lesson(lesson) for lesson in lessons]  
    return lessons


# Thêm bài học vào chủ đề
@app.post("/topics/{topic_id}/lessons")
async def create_lesson(topic_id: str, request: Request, lesson: LessonCreate):
    user_id = request.state.user_id
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    new_lesson = {
        "user_id": ObjectId(user_id),
        "topic_id": ObjectId(topic_id),
        "name": lesson.name,
        "note": lesson.note,
        "due_date": lesson.due_date,
        "status": lesson.status,
        "documents": [],
        "created_at": datetime.now(VN_TZ)
    }

    result = await lessons_collection.insert_one(new_lesson)
    created_lesson = await lessons_collection.find_one({"_id": result.inserted_id})

    created_lesson["_id"] = str(created_lesson["_id"])
    created_lesson["topic_id"] = str(created_lesson["topic_id"])
    created_lesson["user_id"] = str(created_lesson["user_id"])

    return {"message": "Lesson created", "lesson": created_lesson}



# Sửa bài học
@app.put("/lessons/{id}")
async def update_lesson(id: str, lesson_data: dict):
    update_fields = {k: v for k, v in lesson_data.items() if v is not None}
    if not update_fields:
        raise HTTPException(status_code=400, detail="No data provided for update")

    result = await lessons_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": update_fields}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Lesson not found")

    return {"msg": "Lesson updated"}


# Xóa bài học
@app.delete("/lessons/{id}")
async def delete_lesson(id: str):
    try:
        lesson_id = ObjectId(id)
    except errors.InvalidId: # type: ignore
        raise HTTPException(status_code=400, detail="Invalid lesson ID")

    result = await lessons_collection.delete_one({"_id": lesson_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    return {"msg": "Lesson deleted successfully"}


# Bắt đầu đồng hồ đo thời gian thực tế
@app.post("/timetracking/start")
async def start_tracking(request: Request):
    """Bắt đầu session học tập mới"""
    user_id = request.state.user_id
    if not user_id:
        raise HTTPException(status_code=401, detail="Chưa xác thực người dùng")

    try:
        obj_user_id = ObjectId(user_id)
    except errors.InvalidId:
        raise HTTPException(status_code=400, detail="ID người dùng không hợp lệ")

    # Kiểm tra session đang chạy
    existing_session = await studysessions_collection.find_one({
        "user_id": obj_user_id,
        "end": {"$exists": False}
    })

    if existing_session:
        # Trả về thông tin session hiện tại thay vì thông báo lỗi
        return {
            "session_id": str(existing_session["_id"]),
            "start": existing_session["start"],
            "is_running": True
        }

    # Tạo session mới
    session_data = {
        "user_id": obj_user_id,
        "start": datetime.now(VN_TZ),
        "type": "study"  # Loại session
    }

    result = await studysessions_collection.insert_one(session_data)
    
    return {
        "session_id": str(result.inserted_id),
        "start": session_data["start"],
        "is_running": True
    }


# Dừng đồng hộ và lưu thời gian học
@app.post("/timetracking/stop")
async def stop_tracking(request: Request):
    """Dừng session học tập hiện tại"""
    user_id = request.state.user_id
    if not user_id:
        raise HTTPException(status_code=401, detail="Chưa xác thực người dùng")

    # Tìm session chưa kết thúc gần nhất
    session = await studysessions_collection.find_one({
        "user_id": ObjectId(user_id),
        "end": {"$exists": False}
    }, sort=[("start", -1)])

    if not session:
        raise HTTPException(status_code=404, detail="Không có session nào đang chạy")

    end_time = datetime.now(VN_TZ)
    start_time = session["start"].astimezone(VN_TZ) if session["start"].tzinfo else session["start"].replace(tzinfo=timezone.utc).astimezone(VN_TZ)
    
    duration = (end_time - start_time).total_seconds()

    # Cập nhật session
    await studysessions_collection.update_one(
        {"_id": session["_id"]},
        {"$set": {
            "end": end_time,
            "duration": duration,
            "status": "completed"
        }}
    )

    return {
        "session_id": str(session["_id"]),
        "start": start_time,
        "end": end_time,
        "duration": duration,
        "type": session.get("type", "study")
    }


# Bắt đầu đồng hồ đếm ngược
@app.post("/pomodoro/start")
async def start_pomodoro(request: Request):
    """Bắt đầu session Pomodoro mới"""
    user_id = request.state.user_id
    if not user_id:
        raise HTTPException(status_code=401, detail="Chưa xác thực người dùng")

    # Kiểm tra xem có session nào đang chạy không
    existing_session = await studysessions_collection.find_one({
        "user_id": ObjectId(user_id),
        "end": {"$exists": False}
    })

    if existing_session:
        await studysessions_collection.update_one(
            {"_id": existing_session["_id"]},
            {"$set": {"end": datetime.now(VN_TZ), "status": "interrupted"}}
        )

    start_time = datetime.now(VN_TZ)
    duration = 50 * 60  # 50 phút

    session_data = {
        "user_id": ObjectId(user_id),
        "start": start_time,
        "type": "pomodoro",
        "duration": duration,
        "status": "running"
    }

    result = await studysessions_collection.insert_one(session_data)
    
    return {
        "session_id": str(result.inserted_id),
        "start": start_time,
        "duration": duration,
        "type": "pomodoro"
    }


# Dừng Pomodoro
@app.post("/pomodoro/stop")
async def stop_pomodoro(request: Request):
    """Dừng session Pomodoro hiện tại"""
    user_id = request.state.user_id
    if not user_id:
        raise HTTPException(status_code=401, detail="Chưa xác thực người dùng")

    # Tìm session Pomodoro chưa kết thúc gần nhất
    session = await studysessions_collection.find_one({
        "user_id": ObjectId(user_id),
        "end": {"$exists": False},
        "type": "pomodoro"
    }, sort=[("start", -1)])

    if not session:
        raise HTTPException(status_code=404, detail="Không có session Pomodoro nào đang chạy")

    end_time = datetime.now(VN_TZ)
    start_time = session["start"].astimezone(VN_TZ) if session["start"].tzinfo else session["start"].replace(tzinfo=timezone.utc).astimezone(VN_TZ)
    
    duration = (end_time - start_time).total_seconds()

    # Cập nhật session Pomodoro
    await studysessions_collection.update_one(
        {"_id": session["_id"]},
        {"$set": {
            "end": end_time,
            "duration": duration,
            "status": "completed"
        }}
    )

    return {
        "session_id": str(session["_id"]),
        "start": start_time,
        "end": end_time,
        "duration": duration,
        "type": session.get("type", "pomodoro")
    }


# Kiểm tra session đang hoạt động
@app.get("/timetracking/active")
async def get_active_session(request: Request):
    """Lấy session đang hoạt động"""
    user_id = request.state.user_id
    if not user_id:
        raise HTTPException(status_code=401, detail="Chưa xác thực người dùng")

    session = await studysessions_collection.find_one({
        "user_id": ObjectId(user_id),
        "end": {"$exists": False}
    }, sort=[("start", -1)])

    if not session:
        raise HTTPException(status_code=404, detail="Không có session nào đang chạy")

    return {
        "session_id": str(session["_id"]),
        "start": session["start"],
        "type": session.get("type", "study")
    }


# Lấy danh sách thời gian đã học
@app.get("/timetracking/history")
async def get_tracking_history(request: Request):
    user_id = request.state.user_id
    if not user_id:
        raise HTTPException(status_code=401, detail="Chưa xác thực người dùng")

    sessions = await studysessions_collection.find({
        "user_id": ObjectId(user_id)
    }).to_list(100)

    for s in sessions:
        s["_id"] = str(s["_id"])
        s["user_id"] = str(s["user_id"])
        
        # Chuyển đổi múi giờ cho các trường thời gian
        if "start" in s:
            if s["start"].tzinfo is None:  # Nếu không có múi giờ
                s["start"] = s["start"].replace(tzinfo=timezone.utc).astimezone(VN_TZ)
            else:  # Nếu đã có múi giờ
                s["start"] = s["start"].astimezone(VN_TZ)
                
        if "end" in s and s["end"] is not None:
            if s["end"].tzinfo is None:
                s["end"] = s["end"].replace(tzinfo=timezone.utc).astimezone(VN_TZ)
            else:
                s["end"] = s["end"].astimezone(VN_TZ)
    
    return sessions


# Thống kê tổng quan
@app.get("/statistics/user/summary")
async def get_user_summary(request: Request):
    user_id = request.state.user_id
    if not user_id:
        raise HTTPException(status_code=401, detail="Chưa xác thực người dùng")

    try:
        obj_user_id = ObjectId(user_id)
    except:
        raise HTTPException(status_code=400, detail="ID người dùng không hợp lệ")

    # Pipeline tính thời gian học (giữ nguyên)
    pipeline = [
        {"$match": {
            "user_id": obj_user_id,
            "end": {"$exists": True},
            "duration": {"$gt": 0}
        }},
        {"$group": {
            "_id": None,
            "total_seconds": {"$sum": "$duration"},
            "sessions_count": {"$sum": 1},
            "study_dates": {"$addToSet": {
                "$dateToString": {
                    "format": "%Y-%m-%d",
                    "date": {"$toDate": "$start"},
                    "timezone": "+07"
                }
            }}
        }},
        {"$project": {
            "_id": 0,
            "total_hours": {"$round": [{"$divide": ["$total_seconds", 3600]}, 2]},
            "sessions_count": 1,
            "study_dates": 1
        }}
    ]

    # Pipeline tính số bài học đã hoàn thành (THÊM VÀO)
    completed_lessons_pipeline = [
        {"$match": {
            "user_id": obj_user_id,
            "status": "done"
        }},
        {"$count": "completed_lessons"}
    ]

    # Pipeline tính chủ đề hoàn thành (giữ nguyên)
    topics_pipeline = [
        {"$match": {"user_id": obj_user_id}},
        {"$lookup": {
            "from": "lessons",
            "localField": "_id",
            "foreignField": "topic_id",
            "as": "lessons"
        }},
        {"$addFields": {
            "total_lessons": {"$size": "$lessons"},
            "completed_lessons": {
                "$size": {
                    "$filter": {
                        "input": "$lessons",
                        "as": "lesson",
                        "cond": {"$eq": ["$$lesson.status", "done"]}
                    }
                }
            }
        }},
        {"$match": {
            "$expr": {
                "$and": [
                    {"$gt": ["$total_lessons", 0]},
                    {"$eq": ["$total_lessons", "$completed_lessons"]}
                ]
            }
        }},
        {"$count": "completed_topics"}
    ]

    # Thực hiện các pipeline (sửa lại để thêm completed_lessons)
    stats_result, completed_lessons, completed_topics = await asyncio.gather(
        studysessions_collection.aggregate(pipeline).to_list(1),
        lessons_collection.aggregate(completed_lessons_pipeline).to_list(1),
        topics_collection.aggregate(topics_pipeline).to_list(1)
    )

    stats = stats_result[0] if stats_result else {
        "total_hours": 0,
        "sessions_count": 0,
        "study_dates": []
    }

    # Tính streak
    streak = 0
    today = datetime.now(VN_TZ).date()
    current_date = today
    study_dates_set = {datetime.strptime(d, "%Y-%m-%d").date() for d in stats["study_dates"]}
    
    while current_date in study_dates_set:
        streak += 1
        current_date -= timedelta(days=1)

    # Kết quả trả về 
    return {
        "total_hours": stats["total_hours"],
        "completed_lessons": completed_lessons[0]["completed_lessons"] if completed_lessons else 0,
        "completed_topics": completed_topics[0]["completed_topics"] if completed_topics else 0,
        "streak": streak,
        "study_days_count": len(stats["study_dates"])
    }


# Biểu đồ thống kê 
@app.get("/statistics/user/graph")
async def get_user_graph(request: Request, period: str = "7days"):
    user_id = request.state.user_id
    if not user_id:
        raise HTTPException(status_code=401, detail="Chưa xác thực người dùng")

    try:
        obj_user_id = ObjectId(user_id)
    except:
        raise HTTPException(status_code=400, detail="ID người dùng không hợp lệ")

    # Xác định khoảng thời gian
    end_date = datetime.now(VN_TZ)
    if period == "7days":
        start_date = end_date - timedelta(days=7)
    elif period == "30days":
        start_date = end_date - timedelta(days=30)
    else:  # Mặc định 7 ngày
        start_date = end_date - timedelta(days=7)

    # Pipeline aggregation hiệu quả hơn
    pipeline = [
        {"$match": {
            "user_id": obj_user_id,
            "end": {"$exists": True},
            "start": {"$gte": start_date, "$lte": end_date}
        }},
        {"$group": {
            "_id": {
                "$dateToString": {
                    "format": "%Y-%m-%d",
                    "date": "$start",
                    "timezone": "+07"
                }
            },
            "total_minutes": {"$sum": {"$divide": ["$duration", 60]}},
            "sessions_count": {"$sum": 1}  # Thêm số session mỗi ngày nếu cần
        }},
        {"$project": {
            "date": "$_id",
            "minutes": {"$round": ["$total_minutes", 1]},
            "sessions": "$sessions_count",
            "_id": 0
        }},
        {"$sort": {"date": 1}}
    ]

    daily_stats = await studysessions_collection.aggregate(pipeline).to_list(None)

    # Điền đầy đủ các ngày kể cả không có dữ liệu
    date_range = [
        (start_date + timedelta(days=x)).date().isoformat() 
        for x in range((end_date.date() - start_date.date()).days + 1)
    ]

    # Tạo dict để truy xuất nhanh
    stats_dict = {stat["date"]: stat for stat in daily_stats}

    return [
        {
            "date": date,
            "minutes": stats_dict.get(date, {}).get("minutes", 0),
            "sessions": stats_dict.get(date, {}).get("sessions", 0)  # Thêm nếu cần
        }
        for date in date_range
    ]


# Lấy danh sách bài học theo ngày
@app.get("/lessons/scheduled")
async def get_scheduled_lessons(request: Request):
    # Middleware sẽ tự động kiểm tra token
    user_id = request.state.user_id  
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    lessons = await lessons_collection.find({
        "user_id": ObjectId(user_id),
        "due_date": {"$exists": True, "$ne": ""}
    }).to_list(1000)
    
    return [convert_objectid(lesson) for lesson in lessons]


 # Lấy danh sách bài học có ngày học dự kiến
@app.get("/lessons")
async def get_all_lessons(request: Request):
    user_id = request.state.user_id
    if not user_id:
        raise HTTPException(status_code=401, detail="Chưa xác thực người dùng")

    lessons = await lessons_collection.find({
        "user_id": ObjectId(user_id),
        "due_date": {"$ne": ""}  # Chỉ lấy bài có due_date
    }).to_list(1000)

    return [serialize_lesson(lesson) for lesson in lessons]


# Cấu hình thư mục upload
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.post("/topics/{topic_id}/lessons/{lesson_id}/upload")
async def upload_document_to_lesson(
    topic_id: str,
    lesson_id: str,
    request: Request,
    files: List[UploadFile] = File(...),  
):
    """Upload nhiều tài liệu vào bài học"""
    user_id = request.state.user_id
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Kiểm tra bài học tồn tại
    lesson = await lessons_collection.find_one({
        "_id": ObjectId(lesson_id),
        "topic_id": ObjectId(topic_id),
        "user_id": ObjectId(user_id)
    })
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Tạo thư mục lưu trữ
    topic_dir = os.path.join(UPLOAD_DIR, f"topics_{topic_id}")
    lesson_dir = os.path.join(topic_dir, f"lessons_{lesson_id}")
    os.makedirs(lesson_dir, exist_ok=True)

    uploaded_documents = []
    
    for file in files:
        try:
            # Tạo tên file duy nhất
            file_ext = Path(file.filename).suffix.lower()
            unique_filename = f"{uuid.uuid4().hex}{file_ext}"
            file_path = os.path.join(lesson_dir, unique_filename)

            # Lưu file vật lý
            file_size = 0
            with open(file_path, "wb") as buffer:
                while chunk := await file.read(1024 * 1024):  
                    file_size += len(chunk)
                    buffer.write(chunk)

            # Tạo document info
            document_info = DocumentInfo(
                id=str(uuid.uuid4()),
                original_name=file.filename,
                saved_name=unique_filename,
                file_path=f"/uploads/topics_{topic_id}/lessons_{lesson_id}/{unique_filename}",
                content_type=file.content_type or "application/octet-stream",
                size=file_size,
                uploaded_at=datetime.now().isoformat()
            )
            
            uploaded_documents.append(document_info.dict())

        except Exception as e:
            # Nếu có lỗi, tiếp tục với các file khác
            print(f"Error uploading file {file.filename}: {str(e)}")
            continue

    # Cập nhật vào bài học (thêm tất cả documents cùng lúc)
    if uploaded_documents:
        update_result = await lessons_collection.update_one(
            {"_id": ObjectId(lesson_id)},
            {"$push": {"documents": {"$each": uploaded_documents}}}
        )

    return JSONResponse(
        status_code=201,
        content={
            "message": f"Upload thành công {len(uploaded_documents)}/{len(files)} file",
            "uploaded_documents": uploaded_documents
        }
    )
    

# Lấy danh sách tài liệu trong bài học 
@app.get("/topics/{topic_id}/lessons/{lesson_id}/documents")
async def list_lesson_documents(
    topic_id: str,
    lesson_id: str,
    request: Request
):
    """Lấy danh sách tài liệu của bài học"""
    user_id = request.state.user_id
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    lesson = await lessons_collection.find_one(
        {
            "_id": ObjectId(lesson_id),
            "topic_id": ObjectId(topic_id),
            "user_id": ObjectId(user_id)
        },
        {"documents": 1}
    )

    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    return lesson.get("documents", [])


# Xem thông tin chi tiết của tài liệu
@app.get("/topics/{topic_id}/lessons/{lesson_id}/documents/{document_id}")
async def get_document_info(
    topic_id: str,
    lesson_id: str,
    document_id: str,
    request: Request
):
    """Lấy thông tin chi tiết của một tài liệu"""
    user_id = request.state.user_id
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    lesson = await lessons_collection.find_one(
        {
            "_id": ObjectId(lesson_id),
            "topic_id": ObjectId(topic_id),
            "user_id": ObjectId(user_id),
            "documents.id": document_id
        },
        {"documents.$": 1}
    )

    if not lesson or not lesson.get("documents"):
        raise HTTPException(status_code=404, detail="Document not found")

    return lesson["documents"][0]


# Xem tài liệu
@app.get("/topics/{topic_id}/lessons/{lesson_id}/documents/{document_id}/preview")
async def preview_document(topic_id: str, lesson_id: str, document_id: str):
    topic_path = f"uploads/topics_{topic_id}/lessons_{lesson_id}"
    
    lesson = await lessons_collection.find_one({"_id": ObjectId(lesson_id)})
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    matched_doc = next((doc for doc in lesson.get("documents", []) if doc["id"] == document_id), None)
    if not matched_doc:
        raise HTTPException(status_code=404, detail="Document not found")

    file_path = os.path.join(topic_path, matched_doc["saved_name"])

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File does not exist")

    # --- Xác định MIME type từ phần mở rộng ---
    ext = os.path.splitext(matched_doc["saved_name"])[1].lower()
    if ext == ".pdf":
        media_type = "application/pdf"
    elif ext in [".jpg", ".jpeg"]:
        media_type = "image/jpeg"
    elif ext == ".png":
        media_type = "image/png"
    elif ext == ".gif":
        media_type = "image/gif"
    else:
        media_type = "application/octet-stream"  # fallback
    
    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=matched_doc["original_name"],
        headers={"Content-Disposition": f'inline; filename="{matched_doc["original_name"]}"'}
    )

# Xóa tài liệu
@app.delete("/topics/{topic_id}/lessons/{lesson_id}/documents/{document_id}")
async def delete_document(
    topic_id: str,
    lesson_id: str,
    document_id: str,
    request: Request
):
    """Xóa tài liệu khỏi bài học"""
    user_id = request.state.user_id
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Lấy thông tin document trước khi xóa
    document = await get_document_info(topic_id, lesson_id, document_id, request)
    
    # Xóa document khỏi database
    update_result = await lessons_collection.update_one(
        {
            "_id": ObjectId(lesson_id),
            "topic_id": ObjectId(topic_id),
            "user_id": ObjectId(user_id)
        },
        {"$pull": {"documents": {"id": document_id}}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Document not found in lesson")

    # Xóa file vật lý
    file_path = os.path.join(
        UPLOAD_DIR,
        f"topics_{topic_id}",
        f"lessons_{lesson_id}",
        document["saved_name"]
    )
    
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Error deleting file: {str(e)}")

    return {"message": "Xóa tài liệu thành công!"}


# Lấy ID người dùng
async def get_current_user(request: Request):
    user_id = request.state.user_id
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user


# Thông báo học tập
@app.get("/notifications")
async def get_user_notifications(current_user: dict = Depends(get_current_user)):
    try:
        user_id = str(current_user["_id"])
        notifications = await notifications_collection.find(
            {"user_id": user_id}
        ).sort("timestamp", DESCENDING).to_list(20)

        result = []
        for n in notifications:
            try:
                timestamp = n.get("timestamp")
                if isinstance(timestamp, datetime):
                    # Đảm bảo có timezone (UTC)
                    if timestamp.tzinfo is None:
                        timestamp = timestamp.replace(tzinfo=timezone.utc)
                    # Format chuẩn ISO 8601 + hậu tố Z
                    timestamp_str = timestamp.isoformat().replace("+00:00", "Z")
                else:
                    timestamp_str = str(timestamp)
            except Exception as e:
                print("Lỗi timestamp:", n.get("timestamp"), "|", str(e))
                timestamp_str = str(n.get("timestamp")) 
                
            result.append({
                "message": n.get("message", "Không có nội dung"),
                "timestamp": timestamp_str
            })

        return result

    except Exception as e:
        print("Lỗi route /notifications:", str(e))
        raise HTTPException(status_code=500, detail="Lỗi server khi lấy thông báo")



#-------------------------------User APIs------------------------------------------------------


#-------------------------------Admin APIs------------------------------------------------------

router = APIRouter()

# Lấy danh sách người dùng
@app.get("/admin/users")
async def get_users(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Không có quyền truy cập")

        users_cursor = users_collection.find({})
        users = await users_cursor.to_list(length=None)
        for user in users:
            user["_id"] = str(user["_id"])
        return users

    except JWTError:
        raise HTTPException(status_code=401, detail="Token không hợp lệ")



# Thêm người dùng thủ công từ admin
@app.post("/admin/users")
async def create_user(user: dict, token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Không có quyền truy cập")
    
    existing = await users_collection.find_one({
        "$or": [{"username": user["username"]}, {"email": user["email"]}]
    })
    if existing:
        raise HTTPException(status_code=400, detail="Username hoặc email đã tồn tại")
    
    user["password"] = bcrypt.hashpw(user["password"].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user["locked"] = False
    user["created_at"] = datetime.utcnow()

    result = await users_collection.insert_one(user)
    user["_id"] = str(result.inserted_id)

    return user


# Xóa người dùng từ admin
@app.delete("/admin/users/{id}")
async def delete_user(id: str, token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Không có quyền truy cập")

    try:
        result = await users_collection.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="User không tồn tại")
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Khóa tài khoản người dùng
@app.patch("/admin/users/{id}/lock")
async def lock_user(id: str, token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Không có quyền truy cập")

    result = await users_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"locked": True}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User không tồn tại")
    return {"status": "locked"}


# Mở khóa tài khoản người dùng
@app.patch("/admin/users/{id}/unlock")
async def unlock_user(id: str, token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Không có quyền truy cập")

    result = await users_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"locked": False}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User không tồn tại")
    return {"status": "unlocked"}


# Tổng số người dùng
@app.get("/admin/statistics/users")
async def total_users():
    cursor = users_collection.find({})
    users = await cursor.to_list(length=None)
    print("🔍 Có tổng", len(users), "user(s) trong DB:")
    for u in users:
        print(" -", u.get("username"), "| ID:", u.get("_id"))
    return {"total_users": len(users)}


# Tổng số giờ học 
@app.get("/admin/statistics/hours")
async def get_total_hours():
    pipeline = [
        {"$match": {
            "end": {"$exists": True},
            "duration": {"$gt": 0}
        }},
        {"$group": {
            "_id": None,
            "total_seconds": {"$sum": "$duration"}
        }},
        {"$project": {
            "_id": 0,
            "total_hours": {"$round": [{"$divide": ["$total_seconds", 3600]}, 2]}
        }}
    ]
    result = await studysessions_collection.aggregate(pipeline).to_list(1)
    return result[0] if result else {"total_hours": 0}


# Tổng số bài học hoàn thành
@app.get("/admin/statistics/lessons")
async def get_total_completed_lessons():
    count = await lessons_collection.count_documents({
        "status": {
            "$regex": "^\\s*done\\s*$",
            "$options": "i"
        }
    })
    return {"total_completed_lessons": count}


# Mức độ hoạt động trung bình theo ngày / tuần
@app.get("/admin/statistics/active-level")
async def get_active_level():
    now = datetime.now(VN_TZ)
    start_of_week = now - timedelta(days=now.weekday())  # Thứ 2 đầu tuần
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)

    daily_hours = await studysessions_collection.aggregate([
        {"$match": {"start": {"$gte": start_of_day}}},
        {"$project": {"duration": {"$divide": [{"$subtract": ["$end", "$start"]}, 1000 * 60 * 60]}}},
        {"$group": {"_id": None, "total": {"$sum": "$duration"}}}
    ]).to_list(1)

    weekly_hours = await studysessions_collection.aggregate([
        {"$match": {"start": {"$gte": start_of_week}}},
        {"$project": {"duration": {"$divide": [{"$subtract": ["$end", "$start"]}, 1000 * 60 * 60]}}},
        {"$group": {"_id": None, "total": {"$sum": "$duration"}}}
    ]).to_list(1)

    daily_avg = round(daily_hours[0]["total"], 2) if daily_hours else 0
    weekly_avg = round(weekly_hours[0]["total"], 2) if weekly_hours else 0

    return {
        "daily_avg": daily_avg,
        "weekly_avg": weekly_avg
    }


# Hàm gửi thông báo giả lập
async def notify_user(user, message):
    print(f"Gửi đến {user['fullname']}: {message}")
    await notifications_collection.insert_one({
        "user_id": str(user["_id"]),
        "message": message,
        "timestamp": datetime.utcnow()
    })
    

# Job gửi nhắc học mỗi phút
@app.on_event("startup")
async def start_scheduler():
    @scheduler.scheduled_job(CronTrigger(minute="*", timezone="Asia/Ho_Chi_Minh"))
    async def send_daily_reminders():
        now = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh"))
        today_str = now.strftime("%Y-%m-%d")

        # Lấy giờ nhắc từ DB
        reminder = await reminders_collection.find_one({"type": "default"})
        if not reminder:
            print("⚠️ Không có cấu hình giờ nhắc.")
            return

        reminder_time = reminder.get("time")
        if not reminder_time:
            return

        current_time_str = now.strftime("%H:%M")
        if current_time_str != reminder_time:
            return

        # Kiểm tra log riêng từng giờ
        log_key = f"{today_str}_{reminder_time}"
        sent_log = await db["reminder_logs"].find_one({"key": log_key})
        if sent_log:
            print(f"🔁 Đã gửi nhắc học lúc {reminder_time} hôm nay rồi.")
            return

        # Gửi thông báo cho tất cả user
        users = await users_collection.find().to_list(None)
        for user in users:
            await notify_user(user, "⏰ Đã đến giờ học rồi!")

        # Đánh dấu là đã gửi hôm nay tại giờ đó
        await db["reminder_logs"].insert_one({
            "key": log_key,
            "date": today_str,
            "time": reminder_time,
            "sent_at": now
        })
        print(f"Đã gửi nhắc học lúc {current_time_str}")

    scheduler.start()



# Lấy giờ nhắc học mặc định
@app.get("/admin/reminder/default")
async def get_default_reminder(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Không có quyền truy cập")

    reminder = await reminders_collection.find_one({"type": "default"})
    return {"time": reminder.get("time") if reminder else None}


# Cập nhật giờ nhắc học mặc định
@app.post("/admin/reminder/default")
async def update_default_reminder(data: dict, token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Không có quyền truy cập")

    new_time = data.get("time")
    if not new_time:
        raise HTTPException(status_code=400, detail="Thiếu thời gian")

    await reminders_collection.update_one(
        {"type": "default"},
        {"$set": {"time": new_time}},
        upsert=True
    )
    return {"message": "Cập nhật thành công"}

#-------------------------------Admin APIs------------------------------------------------------

if __name__ == "__main__": 
    # Chạy Server
    uvicorn.run(app, host="0.0.0.0", port=5000)