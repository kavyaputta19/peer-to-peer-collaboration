#!/usr/bin/env python3


import sys
import os

# Import all modules
try:
    from database import get_db
    from auth import AuthManager
    from models import Contribution, Collaboration, PeerRating, User
    from scoring_engine import ScoringEngine
    from analytics import Analytics
    from dashboard import Dashboard
    from config import CONTRIBUTION_TYPES
    from tabulate import tabulate
except ImportError as e:
    print(f"\\n✗ Import Error: {e}")
    print("\\nPlease install required packages:")
    print("pip install pymongo bcrypt tabulate python-dateutil")
    sys.exit(1)

class PeerEngagementSystem:
    def __init__(self):
        # Initialize database
        try:
            import database
            database.db_instance = get_db()
            self.db = database.db_instance
        except Exception as e:
            print(f"\\n✗ Failed to initialize database: {e}")
            print("\\nPlease ensure MongoDB is running on localhost:27017")
            sys.exit(1)
        
        # Initialize managers
        self.auth = AuthManager(self.db)
        self.scoring_engine = ScoringEngine(self.db)
        self.analytics = Analytics(self.db, self.scoring_engine)
        self.dashboard = Dashboard(self.auth, self.analytics)
        self.running = True
    
    def display_banner(self):
      
        print("\\n" + "="*70)
        print("  PEER-TO-PEER ENGAGEMENT ATTRIBUTION SYSTEM")
        print("  Collaborative Learning Analytics Model")
        print("="*70)
    
    def main_menu(self):
       
        print("\\n" + "─"*70)
        print("  MAIN MENU")
        print("─"*70)
        print("\\n1. Register")
        print("2. Login")
        print("3. Exit")
        
        choice = input("\\nSelect option: ").strip()
        return choice
    
    def authenticated_menu(self):
       
        current_user = self.auth.get_current_user()
        
        if not current_user:
            print("\\nSession expired. Please login again.")
            self.auth.logout()
            return
        
        print(f"\\n{'─'*70}")
        print(f"  Welcome, {current_user['username']} ({current_user['role'].upper()})")
        print(f"{'─'*70}")
        
        if current_user['role'] == 'student':
            self.student_menu()
        elif current_user['role'] == 'educator':
            self.educator_menu()
    
    def student_menu(self):
       
        while True:
            print("\\n1. View My Dashboard")
            print("2. Log Contribution")
            print("3. Log Collaboration")
            print("4. Rate a Peer")
            print("5. View My Contributions")
            print("6. View My Collaborations")
            print("7. Logout")
            
            choice = input("\\nSelect option: ").strip()
            
            if choice == '1':
                self.dashboard.student_dashboard()
            elif choice == '2':
                self.log_contribution()
            elif choice == '3':
                self.log_collaboration()
            elif choice == '4':
                self.rate_peer()
            elif choice == '5':
                self.view_my_contributions()
            elif choice == '6':
                self.view_my_collaborations()
            elif choice == '7':
                success, message = self.auth.logout()
                print(f"\\n{message}")
                break
            else:
                print("\\nInvalid option!")
    
    def educator_menu(self):
       
        while True:
            print("\\n1. View Analytics Dashboard")
            print("2. View All Students")
            print("3. Logout")
            
            choice = input("\\nSelect option: ").strip()
            
            if choice == '1':
                self.dashboard.educator_dashboard()
            elif choice == '2':
                self.view_all_students()
            elif choice == '3':
                success, message = self.auth.logout()
                print(f"\\n{message}")
                break
            else:
                print("\\nInvalid option!")
    
    def register_user(self):
       
        print("\\n" + "─"*70)
        print("  USER REGISTRATION")
        print("─"*70)
        
        username = input("\\nEnter username: ").strip()
        email = input("Enter email: ").strip()
        password = input("Enter password: ").strip()
        
        print("\\nSelect role:")
        print("1. Student")
        print("2. Educator")
        role_choice = input("Enter choice (1/2): ").strip()
        
        if role_choice not in ['1', '2']:
            print("\\nInvalid role selection!")
            return
        
        role = 'student' if role_choice == '1' else 'educator'
        
        department = ''
        if role == 'student':
            department = input("Enter department: ").strip()
        
        success, message = self.auth.register(username, email, password, role, department)
        print(f"\\n{message}")
    
    def login_user(self):
       
        print("\\n" + "─"*70)
        print("  USER LOGIN")
        print("─"*70)
        
        email = input("\\nEnter email: ").strip()
        password = input("Enter password: ").strip()
        
        success, message, user = self.auth.login(email, password)
        print(f"\\n{message}")
        
        if success:
            self.authenticated_menu()
    
    def log_contribution(self):
       
        current_user = self.auth.get_current_user()
        
        if not current_user:
            print("\\nPlease login first!")
            return
        
        print("\\n" + "─"*70)
        print("  LOG CONTRIBUTION")
        print("─"*70)
        
        print("\\nContribution Types:")
        contribution_types_list = list(CONTRIBUTION_TYPES.items())
        for i, (key, value) in enumerate(contribution_types_list, 1):
            print(f"{i}. {key.replace('_', ' ').title()} (Base Score: {value})")
        
        choice = input("\\nSelect contribution type (1-5): ").strip()
        
        if not choice.isdigit() or not (1 <= int(choice) <= len(contribution_types_list)):
            print("\\nInvalid choice!")
            return
        
        contribution_type = contribution_types_list[int(choice) - 1][0]
        description = input("Enter description: ").strip()
        
        if not description:
            print("\\nDescription cannot be empty!")
            return
        
        quality = input("Enter quality score (1-10, default 5): ").strip()
        quality_score = int(quality) if quality.isdigit() and 1 <= int(quality) <= 10 else 5
        
        try:
            contribution = Contribution(
                current_user['_id'],
                contribution_type,
                description,
                quality_score
            )
            contrib_id = contribution.save(self.db)
            print(f"\\n✓ Contribution logged successfully! ID: {contrib_id}")
        except Exception as e:
            print(f"\\n✗ Error logging contribution: {e}")
    
    def log_collaboration(self):
       
        current_user = self.auth.get_current_user()
        
        if not current_user:
            print("\\nPlease login first!")
            return
        
        print("\\n" + "─"*70)
        print("  LOG COLLABORATION")
        print("─"*70)
        
        peer_username = input("\\nEnter peer's username: ").strip()
        
        if not peer_username:
            print("\\nPeer username cannot be empty!")
            return
        
        # Find peer
        users_collection = self.db.get_collection('users')
        peer = users_collection.find_one({'username': peer_username, 'role': 'student'})
        
        if not peer:
            print(f"\\nStudent '{peer_username}' not found.")
            return
        
        if str(peer['_id']) == str(current_user['_id']):
            print("\\nYou cannot collaborate with yourself!")
            return
        
        interaction_type = input("Enter interaction type (e.g., pair programming, discussion): ").strip()
        if not interaction_type:
            print("\\nInteraction type cannot be empty!")
            return
        
        details = input("Enter details (optional): ").strip()
        
        try:
            collaboration = Collaboration(
                current_user['_id'],
                peer['_id'],
                interaction_type,
                details
            )
            collab_id = collaboration.save(self.db)
            print(f"\\n✓ Collaboration logged successfully! ID: {collab_id}")
        except Exception as e:
            print(f"\\n✗ Error logging collaboration: {e}")
    
    def rate_peer(self):
        
        current_user = self.auth.get_current_user()
        
        if not current_user:
            print("\\nPlease login first!")
            return
        
        print("\\n" + "─"*70)
        print("  RATE A PEER")
        print("─"*70)
        
        peer_username = input("\\nEnter peer's username: ").strip()
        
        if not peer_username:
            print("\\nPeer username cannot be empty!")
            return
        
        # Find peer
        users_collection = self.db.get_collection('users')
        peer = users_collection.find_one({'username': peer_username, 'role': 'student'})
        
        if not peer:
            print(f"\\nStudent '{peer_username}' not found.")
            return
        
        if str(peer['_id']) == str(current_user['_id']):
            print("\\nYou cannot rate yourself!")
            return
        
        rating = input("Enter rating (1-10): ").strip()
        
        if not rating.isdigit() or not (1 <= int(rating) <= 10):
            print("\\nInvalid rating! Must be between 1 and 10.")
            return
        
        comment = input("Enter comment (optional): ").strip()
        
        try:
            peer_rating = PeerRating(
                current_user['_id'],
                peer['_id'],
                int(rating),
                comment
            )
            rating_id = peer_rating.save(self.db)
            print(f"\\n✓ Peer rating submitted successfully! ID: {rating_id}")
        except Exception as e:
            print(f"\\n✗ Error submitting rating: {e}")
    
    def view_my_contributions(self):
       
        current_user = self.auth.get_current_user()
        
        if not current_user:
            print("\\nPlease login first!")
            return
        
        contributions = Contribution.find_by_user(current_user['_id'], self.db)
        
        if not contributions:
            print("\\nYou have no contributions yet.")
            return
        
        print("\\n" + "─"*70)
        print("  MY CONTRIBUTIONS")
        print("─"*70)
        
        table_data = [
            [
                contrib['contribution_type'].replace('_', ' ').title(),
                contrib['description'][:40] + '...' if len(contrib['description']) > 40 else contrib['description'],
                contrib['quality_score'],
                contrib['timestamp'].strftime('%Y-%m-%d %H:%M')
            ]
            for contrib in contributions
        ]
        
        print(tabulate(table_data, 
                      headers=["Type", "Description", "Quality", "Date"],
                      tablefmt="grid"))
    
    def view_my_collaborations(self):
        
        current_user = self.auth.get_current_user()
        
        if not current_user:
            print("\\nPlease login first!")
            return
        
        collaborations = Collaboration.find_by_user(current_user['_id'], self.db)
        
        if not collaborations:
            print("\\nYou have no collaborations yet.")
            return
        
        print("\\n" + "─"*70)
        print("  MY COLLABORATIONS")
        print("─"*70)
        
        users_collection = self.db.get_collection('users')
        table_data = []
        
        for collab in collaborations:
            # Determine the peer
            if str(collab['user1_id']) == str(current_user['_id']):
                peer_id = collab['user2_id']
            else:
                peer_id = collab['user1_id']
            
            peer = users_collection.find_one({'_id': peer_id})
            peer_name = peer['username'] if peer else 'Unknown'
            
            table_data.append([
                peer_name,
                collab['interaction_type'],
                collab['details'][:30] + '...' if len(collab['details']) > 30 else collab['details'],
                collab['timestamp'].strftime('%Y-%m-%d %H:%M')
            ])
        
        print(tabulate(table_data, 
                      headers=["Peer", "Type", "Details", "Date"],
                      tablefmt="grid"))
    
    def view_all_students(self):
        
        current_user = self.auth.get_current_user()
        
        if not current_user or current_user['role'] != 'educator':
            print("\\nAccess denied!")
            return
        
        users_collection = self.db.get_collection('users')
        students = list(users_collection.find({'role': 'student'}))
        
        if not students:
            print("\\nNo students found.")
            return
        
        print("\\n" + "─"*70)
        print("  ALL STUDENTS")
        print("─"*70)
        
        table_data = [
            [
                student['username'],
                student['email'],
                student.get('department', 'N/A'),
                f"{student.get('engagement_score', 0)}/100"
            ]
            for student in students
        ]
        
        print(tabulate(table_data,
                      headers=["Username", "Email", "Department", "Engagement Score"],
                      tablefmt="grid"))
    
    def run(self):
       
        self.display_banner()
        print("\\n✓ System initialized successfully!")
        
        while self.running:
            try:
                if not self.auth.is_authenticated():
                    choice = self.main_menu()
                    
                    if choice == '1':
                        self.register_user()
                    elif choice == '2':
                        self.login_user()
                    elif choice == '3':
                        print("\\nThank you for using Peer Engagement System. Goodbye!")
                        self.running = False
                    else:
                        print("\\nInvalid option!")
                else:
                    self.authenticated_menu()
            except KeyboardInterrupt:
                print("\\n\\nOperation cancelled by user.")
                continue
            except Exception as e:
                print(f"\\n✗ An error occurred: {e}")
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    try:
        app = PeerEngagementSystem()
        app.run()
    except KeyboardInterrupt:
        print("\\n\\nApplication interrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\\n\\n✗ Fatal Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)