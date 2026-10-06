from bson import ObjectId

class Analytics:
    def __init__(self, db_instance, scoring_engine):
        self.db_instance = db_instance
        self.scoring_engine = scoring_engine
        self.users_collection = db_instance.get_collection('users')
        self.contributions_collection = db_instance.get_collection('contributions')
        self.collaborations_collection = db_instance.get_collection('collaborations')
    
    def generate_student_rankings(self, department=None):
       
        query = {'role': 'student'}
        if department:
            query['department'] = department
        
        try:
            users = list(self.users_collection.find(query))
            
            # Update all scores
            for user in users:
                self.scoring_engine.update_user_engagement_score(user['_id'])
            
            # Fetch updated users and sort by engagement score
            users = list(self.users_collection.find(query).sort('engagement_score', -1))
            
            rankings = []
            for rank, user in enumerate(users, 1):
                rankings.append({
                    'rank': rank,
                    'username': user['username'],
                    'department': user.get('department', 'N/A'),
                    'engagement_score': user.get('engagement_score', 0)
                })
            
            return rankings
        except Exception as e:
            print(f"Error generating rankings: {e}")
            return []
    
    def get_department_analytics(self, department):
     
        try:
            students = list(self.users_collection.find({
                'role': 'student',
                'department': department
            }))
            
            if not students:
                return None
            
            total_students = len(students)
            total_engagement = sum(student.get('engagement_score', 0) for student in students)
            avg_engagement = total_engagement / total_students if total_students > 0 else 0
            
            # Count contributions
            student_ids = [student['_id'] for student in students]
            total_contributions = self.contributions_collection.count_documents({
                'user_id': {'$in': student_ids}
            })
            
            # Count collaborations
            total_collaborations = self.collaborations_collection.count_documents({
                '$or': [
                    {'user1_id': {'$in': student_ids}},
                    {'user2_id': {'$in': student_ids}}
                ]
            })
            
            return {
                'department': department,
                'total_students': total_students,
                'average_engagement_score': round(avg_engagement, 2),
                'total_contributions': total_contributions,
                'total_collaborations': total_collaborations,
                'avg_contributions_per_student': round(total_contributions / total_students, 2) if total_students > 0 else 0,
                'avg_collaborations_per_student': round(total_collaborations / total_students, 2) if total_students > 0 else 0
            }
        except Exception as e:
            print(f"Error getting department analytics: {e}")
            return None
    
    def get_all_departments_analytics(self):
       
        try:
            departments = self.users_collection.distinct('department', {'role': 'student'})
            
            analytics_data = []
            for dept in departments:
                if dept and dept.strip():
                    dept_analytics = self.get_department_analytics(dept)
                    if dept_analytics:
                        analytics_data.append(dept_analytics)
            
            return analytics_data
        except Exception as e:
            print(f"Error getting all departments analytics: {e}")
            return []
    
    def get_student_profile(self, user_id):
       
        try:
            user = self.users_collection.find_one({'_id': ObjectId(user_id)})
            
            if not user or user['role'] != 'student':
                return None
            
            # Get detailed scores
            score_data = self.scoring_engine.calculate_total_engagement_score(user_id)
            
            # Get contribution breakdown
            contributions = list(self.contributions_collection.find({'user_id': ObjectId(user_id)}))
            contribution_breakdown = {}
            for contrib in contributions:
                contrib_type = contrib['contribution_type']
                contribution_breakdown[contrib_type] = contribution_breakdown.get(contrib_type, 0) + 1
            
            # Get collaboration count
            collaborations_count = self.collaborations_collection.count_documents({
                '$or': [
                    {'user1_id': ObjectId(user_id)},
                    {'user2_id': ObjectId(user_id)}
                ]
            })
            
            return {
                'username': user['username'],
                'email': user['email'],
                'department': user.get('department', 'N/A'),
                'total_score': score_data['total_score'],
                'engagement_level': score_data['engagement_level'],
                'contribution_score': score_data['contribution_score'],
                'collaboration_score': score_data['collaboration_score'],
                'consistency_score': score_data['consistency_score'],
                'peer_recognition_score': score_data['peer_recognition_score'],
                'total_contributions': len(contributions),
                'contribution_breakdown': contribution_breakdown,
                'total_collaborations': collaborations_count
            }
        except Exception as e:
            print(f"Error getting student profile: {e}")
            return None
    
    def get_top_performers(self, limit=10):
        
        try:
            top_students = list(self.users_collection.find(
                {'role': 'student'}
            ).sort('engagement_score', -1).limit(limit))
            
            performers = []
            for student in top_students:
                performers.append({
                    'username': student['username'],
                    'department': student.get('department', 'N/A'),
                    'engagement_score': student.get('engagement_score', 0)
                })
            
            return performers
        except Exception as e:
            print(f"Error getting top performers: {e}")
            return []