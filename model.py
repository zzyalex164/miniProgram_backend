from app import db
import datetime


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.String(32), primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(64), unique=True, index=True)
    wechat_openid = db.Column(db.String(64), unique=True, index=True)
    admin = db.Column(db.Boolean, default=False)


class OralImages(db.Model):
    __tablename__ = "oral_images"

    user_id = db.Column(db.String(32), db.ForeignKey("user.id"))
    file_id = db.Column(db.String(32), primary_key=True)
    upload_time = db.Column(db.DateTime, default=datetime.datetime.now)
    description = db.Column(db.String(128))
    check_time = db.Column(db.DateTime)
