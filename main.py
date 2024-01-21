from flask import Flask, request, redirect, url_for, render_template
from models import db, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yourdatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            # 로그인 성공시 처리 (예: 홈페이지로 리디렉션)
            return redirect(url_for('home'))
        else:
            # 로그인 실패시 처리
            return 'Invalid credentials'
    return render_template('login.html')

@app.route('/')
def home():
    return '관리자 페이지로 접속해 로그인 한 후 Flag를 획득하세요'


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.form['username']
    password = request.form['password']
    User.add_user(username, password)
    return redirect(url_for('index'))

@app.route('/users')
def users():
    user_list = User.get_all_users()
    return render_template('users.html', users=user_list)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
