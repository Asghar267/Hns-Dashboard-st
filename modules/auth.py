"""
Authentication Module
Enhanced security with session management
"""

import streamlit as st
import hashlib
import json
import os
from datetime import datetime, timedelta

import secrets

CREDENTIALS_FILE = "config/credentials.json"
SESSIONS_FILE = "config/sessions.json"
SESSION_TIMEOUT_DAYS = 7

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_credentials() -> dict:
    """Load credentials file (creates default if missing)."""
    if not os.path.exists(CREDENTIALS_FILE):
        initialize_credentials()
    with open(CREDENTIALS_FILE, 'r') as f:
        return json.load(f)

def save_credentials(data: dict) -> None:
    """Persist credentials file."""
    os.makedirs("config", exist_ok=True)
    with open(CREDENTIALS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def list_users() -> list:
    """Return list of user records."""
    data = load_credentials()
    return data.get("users", [])

def upsert_user(user: dict) -> None:
    """Insert or update a user record by username."""
    data = load_credentials()
    users = data.get("users", [])
    updated = False
    for i, u in enumerate(users):
        if u.get("username") == user.get("username"):
            users[i] = {**u, **user}
            updated = True
            break
    if not updated:
        users.append(user)
    data["users"] = users
    save_credentials(data)

def delete_user(username: str) -> None:
    """Remove a user by username."""
    data = load_credentials()
    users = [u for u in data.get("users", []) if u.get("username") != username]
    data["users"] = users
    save_credentials(data)

def initialize_credentials():
    """Initialize credentials file with default admin user"""
    os.makedirs("config", exist_ok=True)
    
    default_credentials = {
        "users": [
            {
                "username": "Hnsadmin",
                "password_hash": hash_password("root123"),
                "role": "admin",
                "created_at": datetime.now().isoformat()
            }
        ]
    }
    
    with open(CREDENTIALS_FILE, 'w') as f:
        json.dump(default_credentials, f, indent=2)

def verify_credentials(username: str, password: str) -> bool:
    """Verify username and password"""
    try:
        credentials_data = load_credentials()
        for user in credentials_data.get("users", []):
            if user["username"] == username:
                return user["password_hash"] == hash_password(password)
        
        return False
    except Exception as e:
        st.error(f"Authentication error: {e}")
        return False


def get_user_record(username: str) -> dict:
    """Fetch user record by username"""
    try:
        credentials_data = load_credentials()
        for user in credentials_data.get("users", []):
            if user.get("username") == username:
                return user
    except Exception:
        return {}
    return {}

def load_sessions() -> dict:
    """Load persistent sessions."""
    if not os.path.exists(SESSIONS_FILE):
        return {}
    try:
        with open(SESSIONS_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

def save_session(username: str) -> str:
    """Create and save a new session token."""
    token = secrets.token_urlsafe(32)
    sessions = load_sessions()
    sessions[token] = {
        "username": username,
        "created_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(days=SESSION_TIMEOUT_DAYS)).isoformat()
    }
    os.makedirs("config", exist_ok=True)
    with open(SESSIONS_FILE, 'w') as f:
        json.dump(sessions, f, indent=2)
    return token

def validate_session(token: str) -> str:
    """Validate token and return username if valid."""
    sessions = load_sessions()
    if token not in sessions:
        return None
    
    sess = sessions[token]
    expires_at = datetime.fromisoformat(sess["expires_at"])
    if datetime.now() > expires_at:
        del sessions[token]
        with open(SESSIONS_FILE, 'w') as f:
            json.dump(sessions, f, indent=2)
        return None
        
    return sess["username"]

def check_session_timeout():
    """Check if session has timed out"""
    if 'last_activity' in st.session_state:
        last_activity = st.session_state.last_activity
        if datetime.now() - last_activity > timedelta(days=SESSION_TIMEOUT_DAYS):
            return True
    return False

def authenticate_user():
    """Display login form and handle authentication with refresh persistence"""
    # Check for existing session token in URL
    if not st.session_state.get("authenticated", False):
        token = st.query_params.get("session")
        if token:
            username = validate_session(token)
            if username:
                user_rec = get_user_record(username)
                if user_rec:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.user = user_rec
                    st.session_state.last_activity = datetime.now()
                    st.rerun()

    st.markdown("""
        <div style='text-align: center; padding: 50px;'>
            <h1>🔐 HNS Sales Dashboard</h1>
            <p>Please login to continue</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            st.subheader("Login")
            username_input = st.text_input("👤 Username", autocomplete="username")
            password_input = st.text_input("🔒 Password", type="password", autocomplete="current-password")
            submit = st.form_submit_button("Login", width="stretch")
            
            if submit:
                if verify_credentials(username_input, password_input):
                    st.session_state.authenticated = True
                    st.session_state.username = username_input
                    st.session_state.user = get_user_record(username_input)
                    st.session_state.last_activity = datetime.now()
                    
                    # Store session token for refresh persistence
                    token = save_session(username_input)
                    st.query_params["session"] = token
                    
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")


def logout_user():
    """Logout user and clear session/token"""
    if "session" in st.query_params:
        token = st.query_params["session"]
        sessions = load_sessions()
        if token in sessions:
            del sessions[token]
            with open(SESSIONS_FILE, 'w') as f:
                json.dump(sessions, f, indent=2)
        del st.query_params["session"]
        
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.user = None
    st.session_state.last_activity = None
    st.success("✅ Logged out successfully!")


def update_activity():
    """Update last activity timestamp"""
    st.session_state.last_activity = datetime.now()
