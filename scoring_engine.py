from models import Contribution, Collaboration, PeerRating
from config import SCORING_WEIGHTS, CONTRIBUTION_TYPES
from bson import ObjectId
from datetime import datetime, timedelta

class ScoringEngine:
    def __init__(self, db_instance):
        self.db_instance = db_instance
        self.weights = SCORING_WEIGHTS
        self.contribution_types = CONTRIBUTION_TYPES
    
    def calculate_contribution_score(self, user_id):
       
        contributions = Contribution.find_by_user(user_id, self.db_instance)
        
        if not contributions:
            return 0
        
        total_score = 0
        for contrib in contributions:
            base_score = self.contribution_types.get(contrib['contribution_type'], 5)
            quality_multiplier = contrib['quality_score'] / 5.0
            total_score += base_score * quality_multiplier
        
        # Normalize to 0-100 scale
        max_possible = len(contributions) * 10 * 2
        normalized_score = (total_score / max_possible * 100) if max_possible > 0 else 0
        
        return min(normalized_score, 100)
    
    def calculate_collaboration_score(self, user_id):
        
        collaborations = Collaboration.find_by_user(user_id, self.db_instance)
        
        if not collaborations:
            return 0
        
        # Count unique collaborators
        unique_collaborators = set()
        for collab in collaborations:
            if str(collab['user1_id']) == str(user_id):
                unique_collaborators.add(str(collab['user2_id']))
            else:
                unique_collaborators.add(str(collab['user1_id']))
        
        # Score based on frequency and diversity
        frequency_score = min(len(collaborations) * 5, 50)
        diversity_score = min(len(unique_collaborators) * 10, 50)
        
        return frequency_score + diversity_score
    
    def calculate_consistency_score(self, user_id):
       
        contributions = Contribution.find_by_user(user_id, self.db_instance)
        
        if not contributions:
            return 0
        
        # Check activity over last 30 days
        now = datetime.now()
        thirty_days_ago = now - timedelta(days=30)
        
        # Group by week
        weekly_activity = {}
        for contrib in contributions:
            if contrib['timestamp'] >= thirty_days_ago:
                week_num = (now - contrib['timestamp']).days // 7
                weekly_activity[week_num] = weekly_activity.get(week_num, 0) + 1
        
        # Score based on number of active weeks
        active_weeks = len(weekly_activity)
        consistency_score = (active_weeks / 4.0) * 100
        
        return min(consistency_score, 100)
    
    def calculate_peer_recognition_score(self, user_id):
       
        ratings = PeerRating.find_by_rated_user(user_id, self.db_instance)
        
        if not ratings:
            return 0
        
        # Average rating (1-10 scale)
        total_rating = sum(rating['rating'] for rating in ratings)
        avg_rating = total_rating / len(ratings)
        
        # Normalize to 0-100 scale
        normalized_score = (avg_rating / 10.0) * 100
        
        return normalized_score
    
    def calculate_total_engagement_score(self, user_id):
       
        contribution_score = self.calculate_contribution_score(user_id)
        collaboration_score = self.calculate_collaboration_score(user_id)
        consistency_score = self.calculate_consistency_score(user_id)
        peer_recognition_score = self.calculate_peer_recognition_score(user_id)
        
        # Apply weights
        total_score = (
            contribution_score * self.weights['contribution'] +
            collaboration_score * self.weights['collaboration'] +
            consistency_score * self.weights['consistency'] +
            peer_recognition_score * self.weights['peer_recognition']
        )
        
        return {
            'total_score': round(total_score, 2),
            'contribution_score': round(contribution_score, 2),
            'collaboration_score': round(collaboration_score, 2),
            'consistency_score': round(consistency_score, 2),
            'peer_recognition_score': round(peer_recognition_score, 2),
            'engagement_level': self._get_engagement_level(total_score)
        }
    
    def _get_engagement_level(self, score):
       
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Average"
        elif score >= 20:
            return "Below Average"
        else:
            return "Poor"
    
    def update_user_engagement_score(self, user_id):
      
        try:
            score_data = self.calculate_total_engagement_score(user_id)
            users_collection = self.db_instance.get_collection('users')
            users_collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'engagement_score': score_data['total_score']}}
            )
            return score_data
        except Exception as e:
            print(f"Error updating engagement score: {e}")
            return None