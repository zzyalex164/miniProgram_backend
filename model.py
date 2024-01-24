from app import db


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.String(32), primary_key=True)
    username = db.Columb(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(64), unique=True, index=True)
    wechat_openid = db.Column(db.String(64), unique=True, index=True)
    admin = db.Column(db.Boolean, default=False)
