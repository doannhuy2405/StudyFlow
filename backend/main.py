import jwt
import os
import bcrypt 
import uvicorn
import firebase_admin
import json
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Depends, Request, APIRouter, Header, Body
from pymongo import MongoClient, ReturnDocument
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from firebase_admin import auth, credentials
from datetime import datetime, timedelta
from bson import ObjectId, json_util
from models import UserLogin
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient # type: ignore
from collections import defaultdict
from typing import List, Optional
from bson.errors import InvalidId
from bson import ObjectId
from starlette.middleware.base import BaseHTTPMiddleware


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
    collection = db["reports"]
    
    print("✅ Kết nối MongoDB thành công!")
except Exception as e:
    raise ValueError(f"Lỗi kết nối MongoDB: {e}")

#-------------------------------Authentication APIs-------------------------------------------------

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
def create_token(data: dict, expires_delta: timedelta = timedelta(hours=6)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")


# API Đăng ký người dùng
@app.post("/auth/register")
async def register(user: UserRegister):
    print("Dữ liệu từ frontend:", user.dict())  # In dữ liệu nhận được từ frontend

    # Kiểm tra email và username đã tồn tại chưa
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email đã tồn tại!")
    if users_collection.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username đã tồn tại!")

    # Băm mật khẩu
    hashed_password = hash_password(user.password)
    
    new_user = {
        "fullname": user.fullname,
        "email": user.email,
        "username": user.username,
        "password": hashed_password,
    }
    users_collection.insert_one(new_user)
    
    # Tạo Token ngay sau khi đăng ký
    token_data = {"username": user.username, "email": user.email}
    token = create_token(token_data)

    return {
        "message": "Đăng ký thành công!",
        "token": token,
        "username": user.username,
        "fullname": user.fullname,
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
        data = await request.json()
        id_token = data.get("token")
        
        if not id_token:
            raise HTTPException(status_code=400, detail="Thiếu token Google")

        # 1. Xác thực với Firebase
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token["uid"]
        email = decoded_token.get("email")
        name = decoded_token.get("name", "Người dùng Google")
        picture = decoded_token.get("picture", "")
        
        if not email:
            raise HTTPException(status_code=400, detail="Token không chứa email")

        # 2. Tạo/Tìm user trong MongoDB (sử dụng upsert)
        user_data = {
            "uid": uid,
            "email": email,
            "username": email.split("@")[0],  # Tạo username từ email
            "fullname": name,
            "photo": picture,
            "last_login": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        # Sử dụng find_one_and_update với upsert
        result = await users_collection.find_one_and_update(
            {"email": email},
            {
                "$set": user_data,
                "$setOnInsert": {
                    "created_at": datetime.utcnow(),
                    "roles": ["user"],
                    "password": ""  # Trường password rỗng cho user Google
                }
            },
            upsert=True,
            return_document=ReturnDocument.AFTER
        )

        if not result:
            raise HTTPException(status_code=500, detail="Không thể lưu user vào database")

        # 3. Tạo JWT token
        token_data = {
            "sub": str(result["_id"]),
            "username": result["username"],
            "email": email,
            "exp": datetime.utcnow() + timedelta(hours=6)
        }
        token = jwt.encode(token_data, SECRET_KEY, algorithm="HS256")

        return {
            "success": True,
            "token": token,
            "user": {
                "id": str(result["_id"]),
                "username": result["username"],
                "email": email,
                "fullname": name,
                "photo": picture
            }
        }

    except Exception as e:
        print(f"🔥 Lỗi: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")
    

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
    status: str = "Chưa hoàn thành"


class TopicCreate(BaseModel):
    name: str
    description: str
    lessons: List[LessonItem] = []
    
class LessonUpdate(BaseModel):
    name: Optional[str] = None
    note: Optional[str] = ""
    planned_date: Optional[str] = ""
    status: Optional[str] = "chưa hoàn thành"
    topic_id: Optional[str] = None


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
    status: str = "Chưa hoàn thành"


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
    result = await topics_collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Topic not found")
    return {"msg": "Deleted"}


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
async def add_lesson(topic_id: str, lesson: LessonCreate, request: Request):
    user_id = request.state.user_id  # 👈 Lấy user từ middleware
    if not user_id:
        raise HTTPException(status_code=401, detail="Chưa xác thực người dùng")

    lesson_dict = lesson.model_dump()
    lesson_dict["topic_id"] = ObjectId(topic_id)
    lesson_dict["user_id"] = ObjectId(user_id) 

    if "status" not in lesson_dict or not lesson_dict["status"]:
        lesson_dict["status"] = "chưa hoàn thành"

    result = await lessons_collection.insert_one(lesson_dict)
    return {"id": str(result.inserted_id)}


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


# Thiết lập thói quen học tập
@app.post("/habits")
async def setup_habits(habit: HabitSetup):
    await settings_collection.update_one(
        {"user_id": habit.user_id},
        {"$set": habit.dict()},
        upsert=True
    )
    return {"msg": "Thiết lập thói quen thành công"}


# Lấy dữ liệu thói quen học
@app.get("/habits")
async def get_habits(user_id: str):
    habit = await settings_collection.find_one({"user_id": user_id})
    if habit:
        habit["_id"] = str(habit["_id"])
    return habit or {"msg": "Không có dữ liệu"}


# Bắt đầu đồng hồ đo thời gian thực tế
@app.post("/timetracking/start")
async def start_tracking(request: Request):
    user_id = request.state.user_id
    if not user_id:
        raise HTTPException(status_code=401, detail="Chưa xác thực người dùng")

    session = {
        "user_id": user_id,
        "start": datetime.utcnow()
    }
    await studysessions_collection.insert_one(session)
    return {"msg": "Tracking started"}





# Dừng đồng hộ và lưu thời gian học
@app.post("/timetracking/stop")
async def stop_tracking(request: Request):
    user_id = request.state.user_id
    if not user_id:
        raise HTTPException(status_code=401, detail="Chưa xác thực người dùng")

    session = await studysessions_collection.find_one(
        {"user_id": ObjectId(user_id)},
        sort=[("start", -1)]
    )
    if not session:
        raise HTTPException(status_code=404, detail="No active session")

    end_time = datetime.utcnow()
    duration = (end_time - session["start"]).total_seconds()
    await studysessions_collection.update_one(
        {"_id": session["_id"]},
        {"$set": {"end": end_time, "duration": duration}}
    )
    return {"duration": duration}



# Bắt đầu đồng hồ đếm ngược
@app.post("/pomodoro/start")
async def start_pomodoro(request: Request):
    user_id = request.state.user_id
    if not user_id:
        raise HTTPException(status_code=401, detail="Chưa xác thực")

    start_time = datetime.utcnow()
    end_time = start_time + timedelta(minutes=2)
    duration = 25 * 60  # giây

    session = {
        "user_id": user_id,
        "start": start_time,
        "end": end_time,
        "duration": duration,
        "type": "pomodoro"
    }

    await studysessions_collection.insert_one(session)

    return {
        "msg": "Đã bắt đầu Pomodoro và lưu vào lịch sử",
        "start": start_time,
        "duration_minutes": 25
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
    return sessions


# Tạo nhật ký học tập hàng ngày
@app.post("/journals")
async def create_journal(journal: JournalCreate):
    journal_dict = journal.dict()
    journal_dict["date"] = datetime.utcnow()
    await dailylogs_collection.insert_one(journal_dict)
    return {"msg": "Journal saved"}


# Lấy danh sách nhật ký
@app.get("/journals")
async def get_journals(user_id: str):
    return await dailylogs_collection.find({"user_id": user_id}).to_list(100)


# Gửi đánh giá học tập hàng ngày
@app.post("/evaluations")
async def create_evaluation(evaluation: EvaluationCreate):
    evaluation_dict = evaluation.dict()
    evaluation_dict["date"] = datetime.utcnow()
    await activitylogs_collection.insert_one(evaluation_dict)
    return {"msg": "Evaluation saved"}


# Xem đánh giá học tập 
@app.get("/evaluations")
async def get_evaluations(user_id: str):
    return await activitylogs_collection.find({"user_id": user_id}).to_list(100)


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
@router.get("/admin/statistics/users")
async def total_users():
    cursor = users_collection.find({})
    users = await cursor.to_list(length=None)
    print("🔍 Có tổng", len(users), "user(s) trong DB:")
    for u in users:
        print(" -", u.get("username"), "| ID:", u.get("_id"))
    return {"total_users": len(users)}


# Tổng số giờ học 
@router.get("/admin/statistics/hours")
async def total_hours():
    cursor = studysessions_collection.find({"duration": {"$exists": True}})
    total_minutes = sum([doc["duration"] async for doc in cursor])  # duration = phút
    total_hours = total_minutes // 60
    remaining_minutes = total_minutes % 60
    return {
        "total_hours": total_hours,
        "total_minutes": remaining_minutes
    }


# Tổng số bài học hoàn thành
@router.get("/admin/statistics/lessons")
async def total_completed_lessons():
    count = await lessons_collection.count_documents({"status": "completed"})
    return {"total_lessons": count}


# Mức độ hoạt động trung bình theo ngày / tuần
@router.get("/admin/statistics/active-level")
async def active_level():
    # Lấy các phiên học có timestamp
    cursor = studysessions_collection.find({"timestamp": {"$exists": True}})
    activity_by_date = defaultdict(int)

    async for doc in cursor:
        ts = doc.get("timestamp")
        if ts:
            # Chuyển timestamp sang dạng ngày (yyyy-mm-dd)
            date = ts.date() if isinstance(ts, datetime) else datetime.fromisoformat(ts).date()
            activity_by_date[date] += 1

    total_days = len(activity_by_date)
    total_sessions = sum(activity_by_date.values())

    # Trung bình theo ngày & tuần
    daily_avg = round(total_sessions / total_days, 2) if total_days else 0
    weekly_avg = round(daily_avg * 7, 2)

    return {
        "avg_per_day": daily_avg,
        "avg_per_week": weekly_avg
    }
    

app.include_router(router)


# Đặt giờ nhắc mặc định cho hệ thống
@app.post("/admin/reminder/default")
async def set_default_reminder(reminder: ReminderSetting):
    await reminders_collection.update_one({"type": "default"}, {"$set": {"time": reminder.time}}, upsert=True)
    return {"msg": "Reminder set"}

# Lấy cấu hình nhắc mặc định hiện tại
@app.get("/admin/reminder/default")
async def get_default_reminder():
    reminder = await reminders_collection.find_one({"type": "default"})
    return reminder or {"msg": "No default reminder"}

#-------------------------------Admin APIs------------------------------------------------------

if __name__ == "__main__": 
    # Chạy Server
    uvicorn.run(app, host="0.0.0.0", port=5000)