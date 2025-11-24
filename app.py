from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from database import init_database, get_songs_by_mood, init_users_table, create_user, verify_user, get_user_by_email
import os
from functools import wraps
import hashlib
import secrets
import time

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Initialize databases on startup
init_database()
init_users_table()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('signin'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signin')
def signin():
    return render_template('signin.html')

@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot_password.html')

@app.route('/dashboard')
@login_required
def dashboard():
    username = session.get('username', 'User')
    return render_template('dashboard.html', username=username)

@app.route('/quiz')
@login_required
def quiz():
    return render_template('quiz.html')

@app.route('/images')
@login_required
def images():
    return render_template('images.html')

@app.route('/puzzle')
@login_required
def puzzle():
    return render_template('puzzle.html')

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Validation
        if not username or len(username) < 2:
            return jsonify({'success': False, 'message': 'Username must be at least 2 characters'})
        
        if not email or '@' not in email:
            return jsonify({'success': False, 'message': 'Please enter a valid email address'})
        
        if not password or len(password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters'})
        
        # Check if user already exists
        if get_user_by_email(email):
            return jsonify({'success': False, 'message': 'Email already registered'})
        
        # Create user
        user_id = create_user(username, email, password)
        if user_id:
            return jsonify({'success': True, 'message': 'Registration successful!'})
        else:
            return jsonify({'success': False, 'message': 'Registration failed. Please try again.'})
            
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({'success': False, 'message': 'An error occurred. Please try again.'})

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password are required'})
        
        # Verify user
        user = verify_user(email, password)
        if user:
            session.permanent = True
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['email'] = user['email']
            return jsonify({'success': True, 'message': 'Login successful!'})
        else:
            return jsonify({'success': False, 'message': 'Invalid email or password'})
            
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'success': False, 'message': 'An error occurred. Please try again.'})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/get_recommendations', methods=['POST'])
@login_required
def get_recommendations():
    try:
        data = request.get_json()
        mood = data.get('mood', '')
        module_type = data.get('module_type', '')
        
        if not mood:
            return jsonify({'success': False, 'error': 'No mood detected'})
        
        # Get song recommendations
        songs = get_songs_by_mood(mood)
        
        return jsonify({
            'success': True,
            'dominant_mood': mood,
            'module_type': module_type,
            'songs': songs
        })
        
    except Exception as e:
        print(f"Recommendations error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/reset_password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'success': False, 'message': 'Email is required'})
        
        user = get_user_by_email(email)
        if user:
            # In production, send actual reset email
            return jsonify({'success': True, 'message': 'Password reset instructions sent to your email!'})
        else:
            return jsonify({'success': False, 'message': 'Email not found in our system'})
            
    except Exception as e:
        print(f"Reset password error: {e}")
        return jsonify({'success': False, 'message': 'An error occurred. Please try again.'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)