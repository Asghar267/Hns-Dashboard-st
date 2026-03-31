from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import hashlib
import json
import os

# Configuration
SECRET_KEY = "hns_secret_key_change_in_production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 week
CREDENTIALS_FILE = "config/credentials.json"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter(prefix="/auth", tags=["auth"])

class Token(BaseModel):
    access_token: str
    token_type: str
    username: str
    role: str

class User(BaseModel):
    username: str
    role: str
    allowed_branches: Optional[List[int]] = None
    allowed_tabs: Optional[List[str]] = None

class UserCreate(User):
    password: Optional[str] = None

def save_credentials(data: dict):
    with open(CREDENTIALS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def hash_password_legacy(password: str) -> str:
    """Legacy SHA-256 hashing for compatibility with existing users"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password, hashed_password):
    # Check if it's a legacy SHA-256 hash or a bcrypt hash
    if len(hashed_password) == 64:  # SHA-256 hex digest is 64 chars
        return hash_password_legacy(plain_password) == hashed_password
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def load_credentials():
    if not os.path.exists(CREDENTIALS_FILE):
        os.makedirs("config", exist_ok=True)
        default_creds = {
            "users": [
                {
                    "username": "Hnsadmin",
                    "password_hash": hash_password_legacy("root123"),
                    "role": "admin"
                }
            ]
        }
        with open(CREDENTIALS_FILE, 'w') as f:
            json.dump(default_creds, f, indent=2)
    
    with open(CREDENTIALS_FILE, 'r') as f:
        return json.load(f)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    creds = load_credentials()
    user = next((u for u in creds["users"] if u["username"] == form_data.username), None)
    
    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]}, 
        expires_delta=access_token_expires
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "username": user["username"],
        "role": user["role"]
    }

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return User(username=username, role=payload.get("role", "user"))
    except JWTError:
        raise credentials_exception

@router.get("/users", response_model=List[User])
async def get_users(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    creds = load_credentials()
    return [User(**u) for u in creds["users"]]

@router.post("/users")
async def upsert_user(user_data: UserCreate, current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    creds = load_credentials()
    users = creds.get("users", [])
    
    existing_user_idx = next((i for i, u in enumerate(users) if u["username"] == user_data.username), None)
    
    user_dict = user_data.dict(exclude={"password"})
    if user_data.password:
        user_dict["password_hash"] = get_password_hash(user_data.password)
    
    if existing_user_idx is not None:
        # Update existing
        users[existing_user_idx].update({k: v for k, v in user_dict.items() if v is not None})
        if user_data.password:
            users[existing_user_idx]["password_hash"] = get_password_hash(user_data.password)
    else:
        # Create new
        if not user_data.password:
            raise HTTPException(status_code=400, detail="Password required for new user")
        user_dict["password_hash"] = get_password_hash(user_data.password)
        users.append(user_dict)
    
    creds["users"] = users
    save_credentials(creds)
    return {"message": "User saved successfully"}

@router.delete("/users/{username}")
async def delete_user(username: str, current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if username == current_user.username:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
        
    creds = load_credentials()
    users = [u for u in creds.get("users", []) if u["username"] != username]
    creds["users"] = users
    save_credentials(creds)
    return {"message": "User deleted successfully"}
