import jwt
import os
import bcrypt 
import uvicorn
import firebase_admin
import json
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Depends, Request
from pymongo import MongoClient, ReturnDocument
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from firebase_admin import auth, credentials
from datetime import datetime
from bson import ObjectId, json_util
from models import UserLogin
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient # type: ignore

#------------------------------Database---------------------------------------------------------
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

# Xóa app cũ nếu tồn tại
if firebase_admin._DEFAULT_APP_NAME in firebase_admin._apps:
    firebase_admin.delete_app(firebase_admin.get_app())

# Khởi tạo FastAPI
app = FastAPI()

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
def create_token(data: dict, expires_delta: timedelta = timedelta(hours=1)):
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

    # phải await find_one
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

    db_user = await users_collection.find_one({"username": user.username})
    if db_user and verify_password(user.password, db_user["password"]):
        token_data = {"username": db_user["username"], "role": "user"}
        token = create_token(token_data)

        return {
            "token": token,
            "user": {
                "username": db_user["username"],
                "fullname": db_user.get("fullname", ""),
                "role": "user"
            }
        }

    raise HTTPException(status_code=400, detail="Sai tài khoản hoặc mật khẩu!")


    # Kiểm tra trong bảng người dùng thường
    db_user = users_collection.find_one({"username": user.username})
    if db_user and verify_password(user.password, db_user["password"]):
        token_data = {"username": db_user["username"], "role": "user"}
        token = create_token(token_data)

        return {
            "token": token,
            "user": {
                "username": db_user["username"],
                "fullname": db_user.get("fullname", ""),
                "role": "user"
            }
        }

    # Không tìm thấy tài khoản
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
    
    
# Endpoint đăng nhập Google
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
        result = users_collection.find_one_and_update(
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
            "exp": datetime.utcnow() + timedelta(days=1)
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
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


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
        user = await users_collection.find_one({"username": username})  # ✅ thêm await
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

        await users_collection.update_one({"username": username}, {"$set": update_data})  # ✅ thêm await
        return {"message": "Cập nhật thông tin thành công"}
    except HTTPException as e:
        raise e
    except Exception as e:
        print("❌ Lỗi cập nhật:", e)
        raise HTTPException(status_code=500, detail="Lỗi server khi cập nhật thông tin người dùng")


#-------------------------------User APIs------------------------------------------------------

# Schema dữ liệu do chức năng người dùng thực hiện
class TopicCreate(BaseModel):
    name: str
    description: str
    user_id: str

class LessonCreate(BaseModel):
    topic_id: str
    name: str
    note: str
    due_date: str
    status: str

class HabitSetup(BaseModel):
    user_id: str
    study_days: list
    rest_days: list

class JournalCreate(BaseModel):
    user_id: str
    content: str

class EvaluationCreate(BaseModel):
    user_id: str
    rating: int
    comment: str

class ReminderSetting(BaseModel):
    time: str
    
# Lấy danh sách chủ đề
@app.get("/topics")
async def get_topics():
    return await topics_collection.find().to_list(100)

# Tạo chủ đề học mới
@app.post("/topics")
async def create_topic(topic: TopicCreate):
    result = await topics_collection.insert_one(topic.dict())
    return {"id": str(result.inserted_id)}

# Cập nhật thông tin chủ đề
@app.put("/topics/{id}")
async def update_topic(id: str, topic: TopicCreate):
    result = await topics_collection.update_one({"_id": ObjectId(id)}, {"$set": topic.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Topic not found")
    return {"msg": "Updated successfully"}

# Xóa chủ đề học
@app.delete("/topics/{id}")
async def delete_topic(id: str):
    result = await topics_collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Topic not found")
    return {"msg": "Deleted"}

# Lấy danh sách bài học trong chủ đề
@app.get("/topics/{topic_id}/lessons")
async def get_lessons(topic_id: str):
    return await lessons_collection.find({"topic_id": topic_id}).to_list(100)

# Thêm bài học vào chủ đề
@app.post("/topics/{topic_id}/lessons")
async def add_lesson(topic_id: str, lesson: LessonCreate):
    lesson_dict = lesson.dict()
    lesson_dict["topic_id"] = topic_id
    result = await lessons_collection.insert_one(lesson_dict)
    return {"id": str(result.inserted_id)}

# Sửa bài học
@app.put("/lessons/{id}")
async def update_lesson(id: str, lesson: LessonCreate):
    result = await lessons_collection.update_one({"_id": ObjectId(id)}, {"$set": lesson.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return {"msg": "Lesson updated"}

# Xóa bài học
@app.delete("/lessons/{id}")
async def delete_lesson(id: str):
    result = await lessons_collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return {"msg": "Lesson deleted"}

# Thiết lập thói quen học tập
@app.post("/habits")
async def setup_habits(habit: HabitSetup):
    await settings_collection.update_one({"user_id": habit.user_id}, {"$set": habit.dict()}, upsert=True)
    return {"msg": "Habits set"}

# Lấy dữ liệu thói quen học
@app.get("/habits")
async def get_habits(user_id: str):
    return await settings_collection.find_one({"user_id": user_id})

# Bắt đầu đồng hồ đo thời gian thực tế
@app.post("/timetracking/start")
async def start_tracking(user_id: str):
    session = {"user_id": user_id, "start": datetime.utcnow()}
    await studysessions_collection.insert_one(session)
    return {"msg": "Tracking started"}

# Dừng đồng hộ và lưu thời gian học
@app.post("/timetracking/stop")
async def stop_tracking(user_id: str):
    session = await studysessions_collection.find_one({"user_id": user_id}, sort=[("start", -1)])
    if not session:
        raise HTTPException(status_code=404, detail="No active session")
    end_time = datetime.utcnow()
    duration = (end_time - session["start"]).total_seconds()
    await studysessions_collection.update_one({"_id": session["_id"]}, {"$set": {"end": end_time, "duration": duration}})
    return {"duration": duration}

# Bắt đầu đồng hồ đếm ngược
@app.post("/pomodoro/start")
async def start_pomodoro(user_id: str):
    return {"msg": "Pomodoro started"}  # Placeholder

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

# Thống kê tổng số người dùng
@app.get("/admin/statistics/users")
async def total_users():
    count = await users_collection.count_documents({})
    return {"total_users": count}

# Thống kê tổng số giờ học toàn hệ thống
@app.get("/admin/statistics/hours")
async def total_hours():
    cursor = studysessions_collection.find({"duration": {"$exists": True}})
    total = sum([doc["duration"] async for doc in cursor])
    return {"total_hours": total}

# Thống kê tổng số bài học đã hoàn thành
@app.get("/admin/statistics/lessons")
async def total_completed_lessons():
    count = await lessons_collection.count_documents({"status": "completed"})
    return {"total_completed_lessons": count}

# Mức độ hoạt động trung bình theo ngày/tuần
@app.get("/admin/statistics/active-level")
async def active_level():
    # Placeholder logic
    return {"daily_avg": 3.5, "weekly_avg": 24.5}

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