from app import app, db, login_manager
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(100))
    username = db.Column(db.String(1000))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create():
    with app.app_context():
        db.create_all()
        if not User.query.all():
            users = [
                {'username': 'user1', 'password': 'password1'},
                {'username': 'user2', 'password': 'password2'},
                {'username': 'user3', 'password': 'password3'},
                {'username': 'user4', 'password': 'password4'},
                {'username': 'user5', 'password': 'password5'},
                {'username': 'user6', 'password': 'password6'},
                {'username': 'user7', 'password': 'password7'},
                {'username': 'user8', 'password': 'password8'},
                {'username': 'user9', 'password': 'password9'},
                {'username': 'admin', 'password': 'admin'},
            ]
            for user_data in users:
                user = User(**user_data)
                db.session.add(user)
            db.session.commit()
