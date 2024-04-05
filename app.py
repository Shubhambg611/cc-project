from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure secret key

# MongoDB connection setup (replace with your actual connection details)
MONGO_URI = "mongodb+srv://sbgadhave611:Shubham%40001@cluster0.2ggcabp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client['your_database_name']
users_collection = db['users']
tasks_collection = db['tasks']

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.password_hash = user_data['password_hash']

@login_manager.user_loader
def load_user(user_id):
    user_data = users_collection.find_one({'_id': ObjectId(user_id)})
    if user_data:
        return User(user_data)
    return None

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user_data = users_collection.find_one({'username': username})
        if user_data and check_password_hash(user_data['password_hash'], password):
            user = User(user_data)
            login_user(user)
            return redirect(url_for('tasks'))  # Redirect to tasks page on successful login
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        existing_user = users_collection.find_one({'username': username})
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'error')
        else:
            password_hash = generate_password_hash(password)
            user_data = {'username': username, 'password_hash': password_hash}
            users_collection.insert_one(user_data)
            flash('Account created successfully. Please log in.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/tasks')
@login_required
def tasks():
    # Get tasks for the current user from MongoDB
    user_tasks = tasks_collection.find({'user_id': current_user.id})
    tasks_list = list(user_tasks)
    return render_template('tasks.html', tasks=tasks_list)

@app.route('/add_task', methods=['GET', 'POST'])
@login_required
def add_task():
    if request.method == 'POST':
        task_title = request.form.get('task_title')
        task_description = request.form.get('task_description')

        # Store task in MongoDB for the current user
        task_data = {'user_id': current_user.id, 'title': task_title, 'description': task_description}
        tasks_collection.insert_one(task_data)

        flash('Task added successfully.', 'success')

    return render_template('add_task.html')

@app.route('/delete_task/<task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    tasks_collection.delete_one({'_id': ObjectId(task_id)})
    flash('Task deleted successfully.', 'success')
    return redirect(url_for('tasks'))

if __name__ == '__main__':
    app.run(debug=True)
