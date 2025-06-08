from fastapi import APIRouter, HTTPException, Depends
from database import users_collection
from models import UserLogin, UserSignUp
from auth import verify_password, create_access_token, hash_password
import asyncio

router = APIRouter()

# Đăng nhập
@router.post("/login")
async def login(user: UserLogin):
    existing_user = await users_collection.find_one({"username": user.username})
    if not existing_user or not verify_password(user.password, existing_user["password"]):
        raise HTTPException(status_code=400, detail="Sai tên đăng nhập hoặc mật khẩu!")

    token = create_access_token({"username": user.username})
    return {"message": "Đăng nhập thành công!", "token": token, "user": {
        "fullname": existing_user["fullname"],
        "email": existing_user["email"],
        "username": existing_user["username"]
    }}

# Đăng ký
@router.post("/register")
async def register(user: UserSignUp):
    existing_user = await users_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Tên đăng nhập đã tồn tại!")

    hashed_pw = hash_password(user.password)  # Mã hóa mật khẩu
    new_user = {
        "fullname": user.fullname,
        "email": user.email,
        "username": user.username,
        "password": hashed_pw
    }
    await users_collection.insert_one(new_user)
    
    # Tạo token để đăng nhập luôn
    token = create_access_token({"username": user.username})
    
    return {"message": "Đăng ký thành công!", "token": token, "user": {
            "fullname": user.fullname,
            "email": user.email,
            "username": user.username
    }}