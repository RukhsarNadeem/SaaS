from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'  # Change this to a strong secret key!

DATA_FILE = 'student_data.json'
USERS_FILE = 'users.json'

# Initialize JSON file if not exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

# Initialize users file with default allowed users if not exists
if not os.path.exists(USERS_FILE):
    default_users = [
        {"username": "admin", "password": "admin123", "role": "teacher", "name": "Admin Teacher"},
        {"username": "student1", "password": "pass123", "role": "student", "name": "Student One"},
        {"username": "student2", "password": "pass456", "role": "student", "name": "Student Two"}
    ]
    with open(USERS_FILE, 'w') as f:
        json.dump(default_users, f, indent=4)

def is_logged_in():
    return 'user' in session

# AUTH ROUTES
@app.route('/')
def home():
    if not is_logged_in():
        return redirect(url_for('login'))
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if is_logged_in():
        return redirect(url_for('index'))

    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        with open(USERS_FILE, 'r') as f:
            users = json.load(f)

        user = next((u for u in users if u['username'] == username and u['password'] == password), None)

        if user:
            session['user'] = {
                'username': user['username'],
                'name': user['name'],
                'role': user['role']
            }
            return jsonify({"success": True, "message": f"Welcome, {user['name']}!"})
        else:
            return jsonify({"success": False, "message": "Invalid username or password."}), 401

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# MAIN APP ROUTES (PROTECTED)
@app.route('/dashboard')
def index():
    if not is_logged_in():
        return redirect(url_for('login'))
    return render_template('index.html', user=session['user'])

@app.route('/add_student', methods=['POST'])
def add_student():
    if not is_logged_in():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    new_student = {
        "name": data['name'],
        "department": data['department'],
        "roll_number": data['roll_number']
    }

    with open(DATA_FILE, 'r') as f:
        students = json.load(f)

    students.append(new_student)

    with open(DATA_FILE, 'w') as f:
        json.dump(students, f, indent=4)

    return jsonify({"message": "Student added successfully!"})

@app.route('/get_students')
def get_students():
    if not is_logged_in():
        return jsonify({"error": "Unauthorized"}), 401

    with open(DATA_FILE, 'r') as f:
        students = json.load(f)
    return jsonify(students)

@app.route('/get_session_user')
def get_session_user():
    if not is_logged_in():
        return jsonify({"error": "Not logged in"}), 401
    return jsonify(session['user'])

# ADMIN: MANAGE USERS (teacher only)
@app.route('/get_users')
def get_users():
    if not is_logged_in() or session['user']['role'] != 'teacher':
        return jsonify({"error": "Unauthorized"}), 403

    with open(USERS_FILE, 'r') as f:
        users = json.load(f)

    safe_users = [{"username": u['username'], "name": u['name'], "role": u['role']} for u in users]
    return jsonify(safe_users)

@app.route('/add_user', methods=['POST'])
def add_user():
    if not is_logged_in() or session['user']['role'] != 'teacher':
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()

    with open(USERS_FILE, 'r') as f:
        users = json.load(f)

    if any(u['username'] == data['username'] for u in users):
        return jsonify({"success": False, "message": "Username already exists!"}), 400

    new_user = {
        "username": data['username'],
        "password": data['password'],
        "role": data['role'],
        "name": data['name']
    }
    users.append(new_user)

    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

    return jsonify({"success": True, "message": f"User '{data['username']}' added successfully!"})

@app.route('/delete_user', methods=['POST'])
def delete_user():
    if not is_logged_in() or session['user']['role'] != 'teacher':
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    username_to_delete = data.get('username')

    if username_to_delete == session['user']['username']:
        return jsonify({"success": False, "message": "You cannot delete your own account!"}), 400

    with open(USERS_FILE, 'r') as f:
        users = json.load(f)

    users = [u for u in users if u['username'] != username_to_delete]

    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

    return jsonify({"success": True, "message": f"User '{username_to_delete}' removed."})

if __name__ == '__main__':
    app.run(debug=True)
