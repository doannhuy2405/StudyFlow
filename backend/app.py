# backend/app.py
from fastapi import FastAPI

app = FastAPI()

# Các routes sẽ được import sau
from routes import *