from main import app, db
from models import User

def init_db():
    with app.app_context():
        db.create_all()

        admin = User(username='관리자', password='비오비')
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    init_db()
