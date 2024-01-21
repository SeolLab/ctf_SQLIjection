from flask import Flask, render_template, request, redirect, url_for, session, make_response
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()


def init_db():
    with app.app_context():
        db.create_all()

        admin = User(username='관리자', password='비오비')
        db.session.add(admin)
        db.session.commit()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        print(f"username: {username}")
        print(f"password: {password}")

        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            # 로그인 성공시 처리 (예: 홈페이지로 리디렉션)
            print("로그인 성공")
            session['user_id'] = user.id
            resp = make_response(redirect('/home'))
            resp.set_cookie('username', username)
            return resp
        else:
            # 로그인 실패시 처리
            return 'Invalid credentials'
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    resp = make_response(redirect('/login'))
    resp.delete_cookie('username')
    return resp

@app.route('/')
def dashboard():
    if 1:
        # 데이터 시각화 생성
        img = io.BytesIO()
        plt.plot([1, 2, 3, 4])
        plt.ylabel('Sample Numbers')
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()

        # 로그인 후 메시지 추가
        login_message = '관리자 페이지로 접속해 로그인 한 후 Flag를 획득하세요'
        return render_template('dashboard.html', plot_url=plot_url, login_message=login_message)
    else:
        return redirect(url_for('login'))

@app.route('/home')
def home():
    return '관리자 페이지로 접속해 로그인 한 후 Flag를 획득하세요'


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
    init_db()
    app.run(host='0.0.0.0', port=5000)
