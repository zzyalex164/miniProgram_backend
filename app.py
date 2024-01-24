from flask import Flask, request, jsonify, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from config import *
from model import *
import pymysql
import uuid
import datetime
import sys

pymysql.install_as_MySQLdb()

app = Flask(__name__)

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"mysql://{mysql_username}:{mysql_password}@{mysql_address}/oral"

db = SQLAlchemy(app)

wechat_login_api = "https://api.weixin.qq.com/sns/jscode2session?appid={}&secret={}&js_code={}&grant_type=authorization_code"


def set_password(password):
    return generate_password_hash(password)


def check_password(password, hash):
    return check_password_hash(hash, password)


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    if data is None:
        return jsonify({"msg": "No Data", "flag": False})
    username = data["name"]
    password = data["password"]
    user_info = User.query.filter_by(username=username).first()
    if user_info is None:
        return jsonify({"msg": "Username Not Exists", "flag": False})
    else:
        if check_password(password, user_info.password_hash):
            return jsonify(
                {
                    "msg": "Login Success",
                    "user_id": user_info.id,
                    "admin": user_info.admin,
                    "flag": True,
                }
            )
        else:
            return jsonify({"msg": "Password Error", "flag": False})


@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    if data is None:
        return jsonify({"msg": "No Data", "flag": False})
    username = data["username"]
    password = data["password"]
    email = data["email"]
    password_hash = set_password(password)
    user_info = User.query.filter_by(username=username).first()
    if user_info is None:
        user_id = str(uuid.uuid4())
        user_info = User(
            id=user_id, username=username, password_hash=password_hash, email=email
        )
        db.session.add(user_info)
        db.session.commit()
        return jsonify({"msg": "Register Success", "flag": True})
    else:
        return jsonify({"msg": "Username Already Exists", "flag": False})


@app.route("/api/wechat_login", methods=["POST"])
def wechat_login():
    openid = request.headers["x-wx-openid"]
    if openid:
        user_info = User.query.filter_by(wechat_openid=openid).first()
        if user_info is None:
            user_id = str(uuid.uuid4())
            user_info = User(id=user_id, wechat_openid=openid)
            db.session.add(user_info)
            db.session.commit()
        return jsonify(
            {
                "msg": "Login Success",
                "user_id": user_info.id,
                "admin": user_info.admin,
                "flag": True,
            }
        )
    else:
        return jsonify({"msg": "Login Failed", "flag": False})


@app.route("/api/upload", methods=["POST"])
def upload():
    data = request.get_json()
    if data is None:
        return jsonify({"msg": "No Data", "flag": False})
    user_id = data["user_id"]
    file_id = data["file_id"]
    id = str(uuid.uuid4())
    img_info = OralImages(id=id, user_id=user_id, file_id=file_id)
    db.session.add(img_info)
    db.session.commit()
    return jsonify({"msg": "Upload Success", "flag": True})


@app.route("/api/get_images", methods=["GET"])
def get_images(user_id):
    user_id = request.args.get("user_id", None)
    if user_id is None:
        return jsonify({"msg": "No User ID", "flag": False})
    img_list = OralImages.query.filter_by(user_id=user_id).all()
    img_list = [
        {
            "file_id": img.file_id,
            "img_path": img.upload_time,
            "checked": img.img_desc is None,
        }
        for img in img_list
    ]
    return jsonify({"msg": "Get Images Success", "img_list": img_list, "flag": True})


@app.route("/api/get_image", methods=["GET"])
def get_image():
    img_id = request.args.get("img_id", None)
    if img_id is None:
        return jsonify({"msg": "No Image ID", "flag": False})
    img_info = OralImages.query.filter_by(id=img_id).first()
    img_info = {"file_id": img_info.file_id, "description": img_info.description}
    return jsonify({"msg": "Get Image Success", "img_info": img_info, "flag": True})


if __name__ == "__main__":
    app.run(host=sys.argv[1], port=sys.argv[2])
