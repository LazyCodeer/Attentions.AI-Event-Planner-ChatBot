# main.py
from fastapi import FastAPI, HTTPException
import re
from fastapi.middleware.cors import CORSMiddleware

# from .database import (
#     users_collection,
#     chats_collection,
#     store_user_preference,
#     get_user_preferences,
#     close_db,
# )
from database import (
    users_collection,
    chats_collection,
    store_user_preference,
    get_user_preferences,
    close_db,
)
from auth_utils import hash_password, verify_password
from schemas import UserCreate, UserLogin, UserOut, ChatMessage
from datetime import datetime
from bson import ObjectId

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Email validation regex pattern
EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")


# Dependency: Get User by Username
def get_user(email: str):
    return users_collection.find_one({"email": email})


# User Registration Endpoint
@app.post("/register", response_model=UserOut)
async def register_user(user: UserCreate):

    # Check valid email
    if not EMAIL_REGEX.match(user.email):
        raise HTTPException(status_code=400, detail="Invalid email address")

    if len(user.password) < 8:
        raise HTTPException(
            status_code=400, detail="Password must be at least 8 characters long"
        )

    if len(user.contact) != 10:
        raise HTTPException(
            status_code=400, detail="Contact number must be 10 digits long"
        )

    if get_user(user.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(user.password)
    user_data = {
        "name": user.name,
        "email": user.email,
        "password": hashed_password,
    }
    result = users_collection.insert_one(user_data)
    new_user = users_collection.find_one({"_id": result.inserted_id})
    return UserOut(
        id=str(new_user["_id"]),
        msg="You have successfully registered",
        name=new_user["name"],
        email=new_user["email"],
    )


# User Login Endpoint
@app.post("/login", response_model=UserOut)
async def login_user(user: UserLogin):

    # Check valid email
    if not EMAIL_REGEX.match(user.email):
        raise HTTPException(status_code=400, detail="Invalid email address")

    user_db = get_user(user.email)
    if not user_db or not verify_password(user.password, user_db["password"]):
        raise HTTPException(
            status_code=401, detail="User does not exist or password is incorrect"
        )

    return UserOut(
        id=str(user_db["_id"]),
        msg="You have successfully logged in",
        name=user_db["name"],
        email=user_db["email"],
    )


# Store Chat Message
@app.post("/chat/")
async def store_chat_message(chat: ChatMessage):
    chat_data = {
        "user_id": chat.user_id,
        "message": chat.message,
        "timestamp": chat.timestamp or datetime.utcnow().isoformat(),
    }
    result = chats_collection.insert_one(chat_data)
    if result.acknowledged:
        return {"status": "Message stored successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to store message")


# Add User Preference
@app.post("/preferences/")
async def add_user_preference(
    user_id: str, preference_type: str, preference_value: str
):
    store_user_preference(user_id, preference_type, preference_value)
    return {"status": "Preference stored successfully"}


# Get User Preferences
@app.get("/preferences/{user_id}")
async def get_preferences(user_id: str):
    preferences = get_user_preferences(user_id)
    return {"preferences": preferences}


# Shutdown event to close DB connections
@app.on_event("shutdown")
def shutdown_event():
    close_db()
