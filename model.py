from app import db
import datetime


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.String(32), primary_key=True)
    username = db.Columb(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(64), unique=True, index=True)
    wechat_openid = db.Column(db.String(64), unique=True, index=True)
    admin = db.Column(db.Boolean, default=False)


class OralImages(db.Model):
    __tablename__ = "oral_images"

    id = db.Column(db.String(32), primary_key=True)
    user_id = db.Column(db.String(32), db.ForeignKey("user.id"))
    img_path = db.Column(db.String(128))
    upload_time = db.Column(db.DateTime, default=datetime.datetime.now)
    img_desc = db.Column(db.String(128))
    check_time = db.Column(db.DateTime)
