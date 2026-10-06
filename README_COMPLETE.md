# Peer-to-Peer Engagement Attribution & Collaborative Learning Analytics Model

## 📋 Project Overview

A comprehensive web-based system for tracking peer-to-peer interactions, collaboration frequency, and contribution levels in educational environments. Built with Flask, MongoDB, and Bootstrap 5.

## 🎯 Features

### Student Features
- ✅ **Dashboard** - View engagement scores and metrics
- ✅ **Log Contributions** - Track 5 types of contributions with quality scores
- ✅ **Log Collaborations** - Record peer interactions
- ✅ **Rate Peers** - Provide ratings (1-10 scale)
- ✅ **View History** - See all contributions and collaborations

### Educator Features
- ✅ **Analytics Dashboard** - Department-level insights
- ✅ **Student Rankings** - View ranked performance
- ✅ **Top Performers** - Identify high-achieving students
- ✅ **Student Profiles** - Detailed individual assessments
- ✅ **Department Comparison** - Cross-department analytics

### Scoring Algorithm
**Weighted Multi-Factor Scoring:**
- Contribution Score (40%) - Quantity and quality of contributions
- Collaboration Score (30%) - Peer interaction frequency
- Consistency Score (20%) - Regular participation
- Peer Recognition Score (10%) - Ratings from peers

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- MongoDB 4.0 or higher

### Step 1: Install MongoDB


**Windows:**
Download from https://www.mongodb.com/try/download/community

### Step 2: Create Project Structure

```
peer_engagement_system/
├── app.py
├── config.py
├── database.py
├── models.py
├── auth.py
├── scoring_engine.py
├── analytics.py
├── requirements.txt
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── student_dashboard.html
│   ├── student_contributions.html
│   ├── add_contribution.html
│   ├── student_collaborations.html
│   ├── add_collaboration.html
│   ├── rate_peer.html
│   ├── educator_dashboard.html
│   ├── department_analytics.html
│   ├── student_rankings.html
│   └── student_profile.html
└── static/
    └── css/
        └── style.css
```

### Step 3: Install Dependencies

```bash
cd peer_engagement_system
pip install -r requirements.txt
or
pip install pymongo bcrypt tabulate python-dateutil Flask Flask-Session
```

### Step 4: Start MongoDB


### Step 5: Run the Application

```bash
python app.py
```

### Step 6: Access the Application

Open your browser and navigate to: **http://localhost:5004**

## 📖 Usage Guide

### For Students

1. **Register**
   - Click "Register" in navbar
   - Enter username, email, password
   - Select "Student" role
   - Enter your department
   - Click "Register"

2. **Login**
   - Use your registered email and password
   - Click "Login"

3. **Add Contribution**
   - Go to "Contributions" menu
   - Click "Add New"
   - Select contribution type
   - Enter description
   - Set quality score (1-10)
   - Submit

4. **Log Collaboration**
   - Go to "Collaborations" menu
   - Click "Add New"
   - Select peer from dropdown
   - Choose interaction type
   - Add details (optional)
   - Submit

5. **Rate a Peer**
   - Dashboard → "Rate a Peer"
   - Select peer username
   - Set rating (1-10)
   - Add comment (optional)
   - Submit

### For Educators

1. **Register as Educator**
   - Click "Register"
   - Select "Educator" role
   - Complete registration

2. **View Analytics**
   - Login to access Analytics Dashboard
   - View department comparisons
   - Check top performers

3. **View Rankings**
   - Click "Rankings" in menu
   - Filter by department (optional)
   - View sorted student list

4. **View Student Profile**
   - Click on any student name
   - View detailed metrics
   - See contribution breakdown

## 🔧 Configuration

Edit `config.py` to customize:

```python
# MongoDB Connection
MONGODB_URI = "mongodb://localhost:27017"
DATABASE_NAME = "peer_engagement_db"

# Scoring Weights
SCORING_WEIGHTS = {
    'contribution': 0.4,     # 40%
    'collaboration': 0.3,    # 30%
    'consistency': 0.2,      # 20%
    'peer_recognition': 0.1  # 10%
}

# Contribution Types and Base Scores
CONTRIBUTION_TYPES = {
    'code_commit': 10,
    'discussion': 5,
    'peer_review': 8,
    'resource_sharing': 6,
    'documentation': 7
}
```

## 📊 Database Schema

### Collections

1. **users**
   - username, email, password_hash, role, department, engagement_score, created_at

2. **contributions**
   - user_id, contribution_type, description, quality_score, timestamp

3. **collaborations**
   - user1_id, user2_id, interaction_type, details, timestamp

4. **peer_ratings**
   - rater_user_id, rated_user_id, rating, comment, timestamp

5. **sessions**
   - user_id, token, created_at, expires_at

## 🎨 Technology Stack

**Backend:**
- Python 3.8+
- Flask 3.0
- MongoDB (PyMongo)
- bcrypt (password hashing)

**Frontend:**
- HTML5
- Bootstrap 5.3
- Font Awesome 6.4
- Custom CSS

## 🐛 Troubleshooting

### MongoDB Connection Error
```bash
# Check if MongoDB is running
sudo systemctl status mongod

# Start MongoDB
sudo systemctl start mongod
```

### Module Import Errors
```bash
pip install -r requirements.txt --force-reinstall
```

### Port Already in Use
```bash
# Change port in app.py
app.run(debug=True, host='0.0.0.0', port=5001)
```

## 📄 License

Educational project - Free to use and modify.

## 👥 Credits

Developed as a college project for Peer-to-Peer Engagement Attribution & Collaborative Learning Analytics.

---

**Version:** 1.0.0  
**Last Updated:** December 2025
