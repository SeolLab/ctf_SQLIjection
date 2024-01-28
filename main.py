from flask import Flask, render_template, request, redirect, url_for, session, make_response, flash, jsonify
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import io
import re
import base64
from datetime import datetime, timedelta
import secrets
import os
from models import db, User

load_dotenv()

app = Flask(__name__)
secret_key = secrets.token_hex(16)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

username = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
dbname = os.getenv('DB_NAME')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{username}:{password}@{host}/{dbname}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


with app.app_context():
    db.create_all()


def init_db():
    with app.app_context():
        db.create_all()

        # 데이터베이스에서 동일한 username과 password를 가진 사용자 찾기
        existing_user = User.query.filter_by(username='관리자', password='비오비').first()

        # 사용자가 존재하지 않는 경우에만 새로운 사용자 추가
        if existing_user is None:
            admin = User(username='관리자', password='비오비')
            db.session.add(admin)
            db.session.commit()



def input_filter(input_value):
    # 정규 표현식을 사용하여 입력값 필터링
    patterns = [r'\.\.\/|\.\./', r'(and|or|not)\s+']
    for pattern in patterns:
        if re.search(pattern, input_value, re.I):
            return True
    return False


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        last_failed_login = session.get('last_failed_login')
        failed_attempts = session.get('failed_attempts', 0)

        if last_failed_login:
            last_failed_login = datetime.strptime(last_failed_login, "%Y-%m-%d %H:%M:%S")
            time_since_last_fail = datetime.now() - last_failed_login

            if failed_attempts >= 5 and time_since_last_fail < timedelta(minutes=1):
                flash("로그인 시도가 너무 많습니다. 1분 후에 다시 시도해주세요.")
                return redirect(url_for('login'))

            # 1분이 지나면 실패 횟수 초기화
            if time_since_last_fail >= timedelta(minutes=1):
                session['failed_attempts'] = 0
                failed_attempts = 0

        username = request.form['username']
        password = request.form['password']

        if input_filter(username) or input_filter(password):
            flash("Invalid input.")
            return redirect(url_for('login'))

        connection = db.engine.connect()
        query = plt.text(f"SELECT username, password FROM user WHERE username = '{username}' AND password = '{password}'")
        result = connection.execute(query)
        user = result.fetchone()
        connection.close()

        print(user)


        if user:
            # 로그인 성공
            session['user_id'] = user.id
            session.pop('failed_attempts', None)
            session.pop('last_failed_login', None)
            resp = make_response(redirect(url_for('admin')))
            resp.set_cookie('username', username)
            print(query)
            return resp
        else:
            # 로그인 실패 처리 및 실패 횟수 업데이트
            failed_attempts += 1
            session['failed_attempts'] = failed_attempts
            session['last_failed_login'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if failed_attempts < 5:
                flash(f"틀렸습니다. 다시 시도해주세요! ({failed_attempts}/5)")
                print(query)
            else:
                flash("로그인 시도가 너무 많습니다. 1분 후에 다시 시도해주세요")

            return redirect(url_for('login'))

    return render_template('login.html')






@app.route('/logout')
def logout():
    session.pop('user_id', None)
    resp = make_response(redirect('/login'))
    resp.delete_cookie('username')
    return resp

@app.route('/admin')
def admin():
    # 현재 로그인된 사용자 확인
    user_id = session.get('user_id')

    if user_id:
        # 로그인한 사용자에게만 대시보드 보여주기
        img = io.BytesIO()
        plt.plot([1, 2, 3, 4])
        plt.ylabel('Sample Numbers')
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()

        login_message = '관리자 페이지로 접속해 로그인 한 후 Flag를 획득하세요'
        return render_template('admin.html', plot_url=plot_url, login_message=login_message)
    else:
        # 로그인하지 않은 사용자는 로그인 페이지로 리다이렉트
        flash("로그인이 필요합니다.")
        return redirect(url_for('login'))

@app.route('/')
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