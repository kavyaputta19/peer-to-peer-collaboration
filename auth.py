from models import User
from datetime import datetime, timedelta
from bson import ObjectId
import secrets

class AuthManager:
    def __init__(self, db_instance):
        self.db_instance = db_instance
        self.sessions = db_instance.get_collection('sessions')
        self.current_session = None
    
    def register(self, username, email, password, role='student', department=''):
       
        # Validate inputs
        if not username or not email or not password:
            return False, "All fields are required"
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
        
        # Check if user already exists
        if User.find_by_email(email, self.db_instance):
            return False, "Email already registered"
        
        if User.find_by_username(username, self.db_instance):
            return False, "Username already taken"
        
        # Create new user
        try:
            user = User(username, email, password, role, department)
            user_id = user.save(self.db_instance)
            return True, f"User registered successfully! ID: {user_id}"
        except Exception as e:
            return False, f"Registration failed: {e}"
    
    def login(self, email, password):
       
        if not email or not password:
            return False, "Email and password are required", None
        
        user = User.find_by_email(email, self.db_instance)
        
        if not user:
            return False, "Invalid email or password", None
        
        # Verify password
        if not User.verify_password(password, user['password_hash']):
            return False, "Invalid email or password", None
        
        # Create session
        try:
            session_token = secrets.token_hex(32)
            session_data = {
                'user_id': user['_id'],
                'token': session_token,
                'created_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(hours=1)
            }
            self.sessions.insert_one(session_data)
            self.current_session = session_data
            
            return True, "Login successful", user
        except Exception as e:
            return False, f"Login failed: {e}", None
    
    def logout(self):
      
        if self.current_session:
            try:
                self.sessions.delete_one({'token': self.current_session['token']})
            except Exception:
                pass
            self.current_session = None
            return True, "Logged out successfully"
        return False, "No active session"
    
    def is_authenticated(self):
       
        if not self.current_session:
            return False
        
        # Check if session is expired
        if datetime.now() > self.current_session['expires_at']:
            self.logout()
            return False
        
        return True
    
    def get_current_user(self):
        
        if self.is_authenticated():
            return User.find_by_id(self.current_session['user_id'], self.db_instance)
        return None
    
    def cleanup_expired_sessions(self):
        
        try:
            self.sessions.delete_many({'expires_at': {'$lt': datetime.now()}})
        except Exception:
            pass