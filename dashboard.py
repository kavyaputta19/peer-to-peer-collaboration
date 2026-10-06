from tabulate import tabulate
from config import CONTRIBUTION_TYPES

class Dashboard:
    def __init__(self, auth_manager, analytics):
        self.auth_manager = auth_manager
        self.analytics = analytics
        self.current_user = None
    
    def student_dashboard(self):
       
        self.current_user = self.auth_manager.get_current_user()
        
        if not self.current_user:
            print("\\nPlease login first!")
            return
        
        print(f"\\n{'='*60}")
        print(f"  STUDENT ENGAGEMENT DASHBOARD - {self.current_user['username']}")
        print(f"{'='*60}")
        
        # Get student profile
        profile = self.analytics.get_student_profile(self.current_user['_id'])
        
        if not profile:
            print("\\nNo profile data available.")
            return
        
        print(f"\\nDepartment: {profile['department']}")
        print(f"Email: {profile['email']}")
        print(f"\\n{'─'*60}")
        print("  ENGAGEMENT METRICS")
        print(f"{'─'*60}")
        
        metrics_data = [
            ["Total Engagement Score", f"{profile['total_score']}/100"],
            ["Engagement Level", profile['engagement_level']],
            ["Contribution Score", f"{profile['contribution_score']}/100"],
            ["Collaboration Score", f"{profile['collaboration_score']}/100"],
            ["Consistency Score", f"{profile['consistency_score']}/100"],
            ["Peer Recognition Score", f"{profile['peer_recognition_score']}/100"]
        ]
        print(tabulate(metrics_data, tablefmt="simple"))
        
        print(f"\\n{'─'*60}")
        print("  ACTIVITY SUMMARY")
        print(f"{'─'*60}")
        
        activity_data = [
            ["Total Contributions", profile['total_contributions']],
            ["Total Collaborations", profile['total_collaborations']]
        ]
        print(tabulate(activity_data, tablefmt="simple"))
        
        if profile['contribution_breakdown']:
            print(f"\\n{'─'*60}")
            print("  CONTRIBUTION BREAKDOWN")
            print(f"{'─'*60}")
            breakdown_data = [[k.replace('_', ' ').title(), v] 
                            for k, v in profile['contribution_breakdown'].items()]
            print(tabulate(breakdown_data, headers=["Type", "Count"], tablefmt="simple"))
    
    def educator_dashboard(self):
       
        self.current_user = self.auth_manager.get_current_user()
        
        if not self.current_user or self.current_user['role'] != 'educator':
            print("\\nAccess denied. Educator access only.")
            return
        
        print(f"\\n{'='*60}")
        print(f"  EDUCATOR ANALYTICS DASHBOARD")
        print(f"{'='*60}")
        
        while True:
            print("\\n1. View Department Analytics")
            print("2. View Student Rankings")
            print("3. View Top Performers")
            print("4. View All Departments Comparison")
            print("5. Search Student Profile")
            print("0. Back to Main Menu")
            
            choice = input("\\nSelect option: ").strip()
            
            if choice == '1':
                self._view_department_analytics()
            elif choice == '2':
                self._view_student_rankings()
            elif choice == '3':
                self._view_top_performers()
            elif choice == '4':
                self._view_all_departments()
            elif choice == '5':
                self._search_student_profile()
            elif choice == '0':
                break
            else:
                print("Invalid option!")
    
    def _view_department_analytics(self):
       
        department = input("\\nEnter department name: ").strip()
        
        if not department:
            print("Department name cannot be empty!")
            return
        
        analytics_data = self.analytics.get_department_analytics(department)
        
        if not analytics_data:
            print(f"\\nNo data found for department: {department}")
            return
        
        print(f"\\n{'─'*60}")
        print(f"  DEPARTMENT ANALYTICS: {department}")
        print(f"{'─'*60}")
        
        data = [
            ["Total Students", analytics_data['total_students']],
            ["Average Engagement Score", f"{analytics_data['average_engagement_score']}/100"],
            ["Total Contributions", analytics_data['total_contributions']],
            ["Total Collaborations", analytics_data['total_collaborations']],
            ["Avg Contributions/Student", analytics_data['avg_contributions_per_student']],
            ["Avg Collaborations/Student", analytics_data['avg_collaborations_per_student']]
        ]
        print(tabulate(data, tablefmt="simple"))
    
    def _view_student_rankings(self):
        
        department = input("\\nEnter department (press Enter for all): ").strip()
        department = department if department else None
        
        rankings = self.analytics.generate_student_rankings(department)
        
        if not rankings:
            print("\\nNo students found.")
            return
        
        print(f"\\n{'─'*60}")
        print(f"  STUDENT RANKINGS")
        if department:
            print(f"  Department: {department}")
        print(f"{'─'*60}")
        
        table_data = [[r['rank'], r['username'], r['department'], f"{r['engagement_score']}/100"] 
                     for r in rankings[:20]]
        print(tabulate(table_data, headers=["Rank", "Username", "Department", "Score"], 
                      tablefmt="grid"))
    
    def _view_top_performers(self):
       
        limit = input("\\nNumber of top performers to display (default 10): ").strip()
        limit = int(limit) if limit.isdigit() and int(limit) > 0 else 10
        
        top_performers = self.analytics.get_top_performers(limit)
        
        if not top_performers:
            print("\\nNo data available.")
            return
        
        print(f"\\n{'─'*60}")
        print(f"  TOP {limit} PERFORMERS")
        print(f"{'─'*60}")
        
        table_data = [[i+1, p['username'], p['department'], f"{p['engagement_score']}/100"] 
                     for i, p in enumerate(top_performers)]
        print(tabulate(table_data, headers=["Rank", "Username", "Department", "Score"], 
                      tablefmt="grid"))
    
    def _view_all_departments(self):
       
        all_analytics = self.analytics.get_all_departments_analytics()
        
        if not all_analytics:
            print("\\nNo data available.")
            return
        
        print(f"\\n{'─'*80}")
        print(f"  ALL DEPARTMENTS COMPARISON")
        print(f"{'─'*80}")
        
        table_data = [
            [
                a['department'],
                a['total_students'],
                f"{a['average_engagement_score']}/100",
                a['total_contributions'],
                a['avg_contributions_per_student']
            ]
            for a in all_analytics
        ]
        print(tabulate(table_data, 
                      headers=["Department", "Students", "Avg Score", "Contributions", "Avg Contrib/Student"],
                      tablefmt="grid"))
    
    def _search_student_profile(self):
        
        username = input("\\nEnter student username: ").strip()
        
        if not username:
            print("Username cannot be empty!")
            return
        
        users_collection = self.analytics.db_instance.get_collection('users')
        user = users_collection.find_one({'username': username, 'role': 'student'})
        
        if not user:
            print(f"\\nStudent '{username}' not found.")
            return
        
        profile = self.analytics.get_student_profile(user['_id'])
        
        if not profile:
            print(f"\\nCould not retrieve profile for '{username}'.")
            return
        
        print(f"\\n{'─'*60}")
        print(f"  STUDENT PROFILE: {profile['username']}")
        print(f"{'─'*60}")
        
        print(f"\\nDepartment: {profile['department']}")
        print(f"Email: {profile['email']}")
        print(f"\\nTotal Score: {profile['total_score']}/100")
        print(f"Engagement Level: {profile['engagement_level']}")
        
        print(f"\\n{'─'*60}")
        print("  DETAILED SCORES")
        print(f"{'─'*60}")
        
        scores_data = [
            ["Contribution Score", f"{profile['contribution_score']}/100"],
            ["Collaboration Score", f"{profile['collaboration_score']}/100"],
            ["Consistency Score", f"{profile['consistency_score']}/100"],
            ["Peer Recognition Score", f"{profile['peer_recognition_score']}/100"]
        ]
        print(tabulate(scores_data, tablefmt="simple"))
        
        print(f"\\nTotal Contributions: {profile['total_contributions']}")
        print(f"Total Collaborations: {profile['total_collaborations']}")