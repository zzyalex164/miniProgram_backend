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

img_folder = "img"

ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg", "gif"]


def set_password(password):
    return generate_password_hash(password)


def check_password(password, hash):
    return check_password_hash(hash, password)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1] in ALLOWED_EXTENSIONS


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
    if "file" not in request.files:
        return jsonify({"msg": "No File Part"})
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"msg": "No Selected File"})
    if file and allowed_file(file.filename):
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        ext = file.filename.rsplit(".", 1)[1].lower()
        filename = f"{user_id}_{timestamp}.{ext}"
        save_path = os.path.join(img_folder, filename)
        file.save(save_path)
        img_id = str(uuid.uuid4())
        img_info = OralImages(id=img_id, user_id=user_id, img_path=save_path)
        db.session.add(img_info)
        db.session.commit()
        return jsonify({"msg": "Upload Success", "flag": True})
    else:
        return jsonify({"msg": "Upload Failed", "flag": False})


@app.route("/api/get_images", methods=["POST"])
def get_images():
    user_id = request.form["user_id"]
    img_list = OralImages.query.filter_by(user_id=user_id).all()
    img_list = [
        {"img_id": img.id, "img_path": img.upload_time, "checked": img.img_desc is None}
        for img in img_list
    ]
    return jsonify({"msg": "Get Images Success", "img_list": img_list, "flag": True})


@app.route("/api/get_image/<img_id>", methods=["GET"])
def get_image(img_id):
    img_info = OralImages.query.filter_by(id=img_id).first()
    return send_from_directory(img_info.img_path)


if __name__ == "__main__":
    app.run(host=sys.argv[1], port=sys.argv[2])
