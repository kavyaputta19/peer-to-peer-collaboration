from datetime import datetime
from bson import ObjectId

import bcrypt

class User:
    def __init__(self, username, email, password, role='student', department=''):
        self.username = username
        self.email = email
        self.password_hash = self._hash_password(password)
        self.role = role
        self.department = department
        self.created_at = datetime.now()
        self.engagement_score = 0
    
    def _hash_password(self, password):
       
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    @staticmethod
    def verify_password(password, password_hash):
        
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash)
        except Exception:
            return False
    
    def save(self, db_instance):
      
        users_collection = db_instance.get_collection('users')
        user_data = {
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'role': self.role,
            'department': self.department,
            'created_at': self.created_at,
            'engagement_score': self.engagement_score
        }
        try:
            result = users_collection.insert_one(user_data)
            return result.inserted_id
        except Exception as e:
            raise Exception(f"Error saving user: {e}")
    
    @staticmethod
    def find_by_email(email, db_instance):
      
        users_collection = db_instance.get_collection('users')
        return users_collection.find_one({'email': email})
    
    @staticmethod
    def find_by_username(username, db_instance):
       
        users_collection = db_instance.get_collection('users')
        return users_collection.find_one({'username': username})
    
    @staticmethod
    def find_by_id(user_id, db_instance):
       
        users_collection = db_instance.get_collection('users')
        try:
            return users_collection.find_one({'_id': ObjectId(user_id)})
        except Exception:
            return None

class Contribution:
    def __init__(self, user_id, contribution_type, description, quality_score=5):
        self.user_id = ObjectId(user_id) if not isinstance(user_id, ObjectId) else user_id
        self.contribution_type = contribution_type
        self.description = description
        self.quality_score = max(1, min(10, quality_score))  # Ensure 1-10 range
        self.timestamp = datetime.now()
    
    def save(self, db_instance):
      
        contributions_collection = db_instance.get_collection('contributions')
        contribution_data = {
            'user_id': self.user_id,
            'contribution_type': self.contribution_type,
            'description': self.description,
            'quality_score': self.quality_score,
            'timestamp': self.timestamp
        }
        result = contributions_collection.insert_one(contribution_data)
        return result.inserted_id
    
    @staticmethod
    def find_by_user(user_id, db_instance):
        
        contributions_collection = db_instance.get_collection('contributions')
        try:
            user_oid = ObjectId(user_id) if not isinstance(user_id, ObjectId) else user_id
            return list(contributions_collection.find({'user_id': user_oid}))
        except Exception:
            return []

class Collaboration:
    def __init__(self, user1_id, user2_id, interaction_type, details=''):
        self.user1_id = ObjectId(user1_id) if not isinstance(user1_id, ObjectId) else user1_id
        self.user2_id = ObjectId(user2_id) if not isinstance(user2_id, ObjectId) else user2_id
        self.interaction_type = interaction_type
        self.details = details
        self.timestamp = datetime.now()
    
    def save(self, db_instance):
     
        collaborations_collection = db_instance.get_collection('collaborations')
        collaboration_data = {
            'user1_id': self.user1_id,
            'user2_id': self.user2_id,
            'interaction_type': self.interaction_type,
            'details': self.details,
            'timestamp': self.timestamp
        }
        result = collaborations_collection.insert_one(collaboration_data)
        return result.inserted_id
    
    @staticmethod
    def find_by_user(user_id, db_instance):
       
        collaborations_collection = db_instance.get_collection('collaborations')
        try:
            user_oid = ObjectId(user_id) if not isinstance(user_id, ObjectId) else user_id
            return list(collaborations_collection.find({
                '$or': [
                    {'user1_id': user_oid},
                    {'user2_id': user_oid}
                ]
            }))
        except Exception:
            return []

class PeerRating:
    def __init__(self, rater_user_id, rated_user_id, rating, comment=''):
        self.rater_user_id = ObjectId(rater_user_id) if not isinstance(rater_user_id, ObjectId) else rater_user_id
        self.rated_user_id = ObjectId(rated_user_id) if not isinstance(rated_user_id, ObjectId) else rated_user_id
        self.rating = max(1, min(10, rating))  # Ensure 1-10 range
        self.comment = comment
        self.timestamp = datetime.now()
    
    def save(self, db_instance):
       
        ratings_collection = db_instance.get_collection('peer_ratings')
        rating_data = {
            'rater_user_id': self.rater_user_id,
            'rated_user_id': self.rated_user_id,
            'rating': self.rating,
            'comment': self.comment,
            'timestamp': self.timestamp
        }
        result = ratings_collection.insert_one(rating_data)
        return result.inserted_id
    
    @staticmethod
    def find_by_rated_user(user_id, db_instance):
       
        ratings_collection = db_instance.get_collection('peer_ratings')
        try:
            user_oid = ObjectId(user_id) if not isinstance(user_id, ObjectId) else user_id
            return list(ratings_collection.find({'rated_user_id': user_oid}))
        except Exception:
            return []