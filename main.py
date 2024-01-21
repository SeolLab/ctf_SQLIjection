from flask import Flask, request, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yourdatabase.db'
db = SQLAlchemy(app)

# @app.route('/add_user/<username>/<email>')
# def add_user(username, email):
#     new_user = User(username=username, email=email)
#     db.session.add(new_user)
#     db.session.commit()
#     return f"User {username} added."
#
# @app.route('/get_users')
# def get_users():
#     users = User.query.all()
#     return str(users)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if user and user.password == password:
        return redirect(url_for('homepage'))
    return 'Invalid credentials'

@app.route('/home')
def home():
    return render_template('index.html',
                           message='Hello, This is home!')



@app.route('/home/homepage')
def homepage():
    return 'Welcome to the homepage!'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
