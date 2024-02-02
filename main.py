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
from sqlalchemy import text



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


def init_db():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # 데이터베이스에서 동일한 username과 password를 가진 사용자 찾기
        existing_user = User.query.filter_by(username='관리자', password='경찰청피싱').first()

        # 사용자가 존재하지 않는 경우에만 새로운 사용자 추가
        if existing_user is None:
            admin = User(username='관리자', password='경찰청피싱')
            db.session.add(admin)
            db.session.commit()




def input_filter(input_value):
    # 정규 표현식을 사용하여 입력값 필터링
    patterns = [r'\.\.\/|\.\./', r'(and|or|not)\s+']
    for pattern in patterns:
        if re.search(pattern, input_value, re.I):
            return True
    return False

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         last_failed_login = session.get('last_failed_login')
#         failed_attempts = session.get('failed_attempts', 0)
#
#         if last_failed_login:
#             last_failed_login = datetime.strptime(last_failed_login, "%Y-%m-%d %H:%M:%S")
#             time_since_last_fail = datetime.now() - last_failed_login
#
#
#
#             if failed_attempts >= 5 and time_since_last_fail < timedelta(minutes=1):
#                 flash("로그인 시도가 너무 많습니다. 1분 후에 다시 시도해주세요.")
#                 return redirect(url_for('login'))
#
#             # 1분이 지나면 실패 횟수 초기화
#             if time_since_last_fail >= timedelta(minutes=1):
#                 session['failed_attempts'] = 0
#                 failed_attempts = 0
#
#
#
#         username = request.form['username']
#         password = request.form['password']
#
#         if input_filter(username) or input_filter(password):
#             flash("Invalid input. and, or, not, . 문자를 사용할 수 없습니다.")
#             return redirect(url_for('login'))
#
#         # Prepare the SQL query using `text`
#         query = text(f"SELECT * FROM user WHERE username = '{username}' AND password = '{password}'")
#
#         # Obtain a connection from the engine
#         connection = db.engine.connect()
#
#         # Execute the query using the connection, passing parameters as a dictionary
#         result = connection.execute(query)
#         user = result.fetchone()
#
#         # Close the connection
#         connection.close()
#
#         print(user)
#
#         if user:
#             session['user_id'] = user.id
#             session.pop('failed_attempts', None)
#             session.pop('last_failed_login', None)
#             # resp = make_response(redirect(url_for('admin')))
#             resp = make_response(redirect(url_for('admin' if username == '관리자' else 'user')))    ## resp = make_response(redirect(url_for('admin')))
#             resp.set_cookie('username', username)
#             return resp
#         else:
#
#             # 로그인 실패 처리 및 실패 횟수 업데이트
#             failed_attempts += 1
#             session['failed_attempts'] = failed_attempts
#             session['last_failed_login'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#
#             if failed_attempts < 5:
#                 flash(f"틀렸습니다. 다시 시도해주세요! ({failed_attempts}/5)")
#                 print(query)
#             else:
#                 flash("로그인 시도가 너무 많습니다. 1분 후에 다시 시도해주세요")
#
#             return redirect(url_for('login'))
#
#     return render_template('login.html')




# 힌트 버전
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
                # 로그인 시도가 5회 초과하고 1분 미만일 때, lockout 상태를 True로 설정하여 경고 메시지를 표시합니다.
                return render_template('login.html', lockout=True)

            if time_since_last_fail >= timedelta(minutes=1):
                session['failed_attempts'] = 0
                failed_attempts = 0

        username = request.form['username']
        password = request.form['password']

        if input_filter(username) or input_filter(password):
            flash("Invalid input. and, or, not, . 문자를 사용할 수 없습니다.")
            return redirect(url_for('login'))

        # Prepare the SQL query using `text`
        query = text(f"SELECT * FROM user WHERE username = '{username}' AND password = '{password}'")
        # Obtain a connection from the engine
        connection = db.engine.connect()
        # Execute the query using the connection, passing parameters as a dictionary
        result = connection.execute(query)
        user = result.fetchone()
        # Close the connection
        connection.close()
        print(user)

        if user:
            session['user_id'] = user.id
            session.pop('failed_attempts', None)
            session.pop('last_failed_login', None)
            resp = make_response(redirect(url_for('admin' if user.username == '관리자' else 'user')))
            resp.set_cookie('username', username)
            return resp
        else:
            failed_attempts += 1
            session['failed_attempts'] = failed_attempts
            session['last_failed_login'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if failed_attempts >= 5:
                # 로그인 시도가 5회 실패한 경우 lockout 상태를 True로 설정하지만, 여기서는 메시지를 flash하고 리다이렉트
                flash("로그인 시도가 너무 많습니다. 1분 후에 다시 시도해주세요")
                return redirect(url_for('login'))

            flash(f"틀렸습니다. 다시 시도해주세요! ({failed_attempts}/5)")

            return redirect(url_for('login'))

    # GET 요청 또는 로그인 실패 후 lockout 상태가 아닌 경우
    return render_template('login.html', lockout=False)



# 사용자 페이지 라우트
@app.route('/user')
def user():
    if session.get('user_id'):
        # 사용자 페이지 관련 로직 (예: 사용자 정보 표시)
        return render_template('user.html')
    else:
        # 로그인하지 않은 사용자는 로그인 페이지로 리다이렉트
        flash("로그인이 필요합니다.")
        return redirect(url_for('login'))



@app.route('/flushdb', methods=['GET', 'POST'])
def flushdb():
    if request.method == 'POST':
        last_failed_login = session.get('last_failed_login')
        failed_attempts = session.get('failed_attempts', 0)

        if last_failed_login:
            last_failed_login = datetime.strptime(last_failed_login, "%Y-%m-%d %H:%M:%S")
            time_since_last_fail = datetime.now() - last_failed_login

            if failed_attempts >= 5 and time_since_last_fail < timedelta(minutes=1):
                flash("로그인 시도가 너무 많습니다. 1분 후에 다시 시도해주세요.")
                return redirect(url_for('flushdb'))

            if time_since_last_fail >= timedelta(minutes=1):
                session['failed_attempts'] = 0
                failed_attempts = 0

        username = request.form['username']
        password = request.form['password']

        if input_filter(username) or input_filter(password):
            flash("Invalid input. and, or, not, . 문자를 사용할 수 없습니다.")
            return redirect(url_for('flushdb'))

        # '관리자' 사용자의 정보를 가져옴
        admin_user = User.query.filter_by(username='관리자').first()

        if admin_user and username == admin_user.username and password == admin_user.password:
            # 로그인 성공
            session['user_id'] = admin_user.id
            session['logged_in'] = True
            session.pop('failed_attempts', None)
            session.pop('last_failed_login', None)
            resp = make_response(redirect(url_for('board')))
            resp.set_cookie('username', username)
            return resp
        else:
            # 로그인 실패 처리 및 실패 횟수 업데이트
            failed_attempts += 1
            session['failed_attempts'] = failed_attempts
            session['last_failed_login'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if failed_attempts < 5:
                flash(f"틀렸습니다. 다시 시도해주세요! ({failed_attempts}/5)")
            else:
                flash("로그인 시도가 너무 많습니다. 1분 후에 다시 시도해주세요")

            return redirect(url_for('flushdb'))

    return render_template('flushdb.html')






@app.route('/board')
def board():
    # '관리자' 사용자의 정보를 가져옴
    admin_user = User.query.filter_by(username='관리자').first()

    # 세션에서 로그인 상태 확인
    if session.get('logged_in'):
        # 로그인한 사용자에게는 특별한 게시글 표시
        posts = [
            {"title": "BoB12_1STAR{I_FINALLY_DEFEATED_THE_BLACK_HACKERS}",  "subject": "N/A", "phone":"N/A", "character":"N/A", "date_posted": "N/A"}
        ]
    elif session.get('user_id'):
        # 일반 사용자에게는 기본 게시글 목록 표시
        if session['user_id'] == admin_user.id:
            posts = [
                {"title": "보안컨설팅 경연단계 진출자 개인정보1", "subject": "김재윤", "phone":"010-0000-0000", "character":"개보법 마스터", "date_posted": "2024-01-11"},
                {"title": "보안컨설팅 경연단계 진출자 개인정보2", "subject": "박윤진", "phone":"010-0000-0000", "character":"디자인 마스터", "date_posted": "2024-01-12"},
                {"title": "보안컨설팅 경연단계 진출자 개인정보3", "subject": "신윤제", "phone":"010-0000-0000", "character":"자동차 마스터", "date_posted": "2024-01-22"},
                {"title": "보안컨설팅 경연단계 진출자 개인정보4", "subject": "설기현", "phone":"010-4445-7736", "character":"마스터키 설", "date_posted": "2024-01-12"},
                {"title": "보안컨설팅 경연단계 진출자 개인정보5", "subject": "이선민", "phone":"010-0000-0000", "character":"비주얼 마스터", "date_posted": "2024-01-31"},
                {"title": "보안컨설팅 경연단계 진출자 개인정보6", "subject": "이유경", "phone":"010-0000-0000", "character":"웹해킹 마스터", "date_posted": "2024-01-23"},
                {"title": "보안컨설팅 경연단계 진출자 개인정보7", "subject": "임홍록", "phone":"010-0000-0000", "character":"관리를 가장한 기술 마스터", "date_posted": "2024-01-22"},
                {"title": "보안컨설팅 경연단계 진출자 개인정보8", "subject": "최원겸", "phone":"010-0000-0000", "character":"모든게 마스터", "date_posted": "2024-01-13"}
            ]
        else:
            # 로그인하지 않은 사용자는 로그인 페이지로 리다이렉트
            flash("로그인이 필요합니다.")
            return redirect(url_for('login'))
    else:
        # 로그인하지 않은 사용자는 로그인 페이지로 리다이렉트
        flash("로그인이 필요합니다.")
        return redirect(url_for('login'))

    return render_template('board.html', posts=posts)







@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # 기존 회원가입 로직

        # # reCAPTCHA 검증
        # recaptcha_response = request.form['g-recaptcha-response']
        # secret_key = '1234'  ## 비밀키
        # captcha_payload = {
        #     'secret': secret_key,
        #     'response': recaptcha_response
        # }
        # r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=captcha_payload)
        # captcha_result = r.json()
        #
        # if not captcha_result['success']:
        #     # reCAPTCHA 검증 실패 처리
        #     flash("캡차 인증에 실패했습니다. 다시 시도해주세요.")
        #     return redirect(url_for('signup'))
        #
        # # reCAPTCHA 검증 성공 시 나머지 로직 처리

        username = request.form['username']
        password = request.form['password']
        # 새로운 사용자 인스턴스 생성
        new_user = User(username=username, password=password)
        # 데이터베이스에 사용자 추가
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')


# from flask import jsonify
# @app.route('/check-username', methods=['POST'])
# def check_username():
#     data = request.get_json()
#     username = data['username']
#     existing_user = User.query.filter_by(username=username).first()
#
#     return jsonify({'exists': existing_user is not None})


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
        # plt.savefig(img, format='png')
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
    return render_template('index.html')


# @app.route('/add_user', methods=['POST'])
# def add_user():
#     username = request.form['username']
#     password = request.form['password']
#     User.add_user(username, password)
#     return redirect(url_for('index'))



if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
