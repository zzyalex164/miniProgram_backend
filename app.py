from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from config import *
from datetime import datetime
import pymysql
import uuid
import sys
import smtplib
import requests
import email
import secrets
import json


pymysql.install_as_MySQLdb()


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql://{mysql_username}:{mysql_password}@{mysql_address}/oral"
)

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.String(128), primary_key=True)
    username = db.Column(db.String(128), unique=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(128), unique=True)
    wechat_openid = db.Column(db.String(128), unique=True)
    admin = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(128))
    telephone = db.Column(db.String(128))
    department = db.Column(db.String(128))
    introduction = db.Column(db.String(255))


class OralReport(db.Model):
    __tablename__ = "report"

    user_id = db.Column(db.String(128), db.ForeignKey("user.id"))
    report_id = db.Column(db.String(128), primary_key=True)
    upload_time = db.Column(db.DateTime, default=datetime.now)
    description = db.Column(db.String(255))
    check_time = db.Column(db.DateTime)


class OralImage(db.Model):
    __tablename__ = "image"

    image_id = db.Column(db.String(128), primary_key=True)
    report_id = db.Column(db.String(128), db.ForeignKey("report.report_id"))


def set_password(password):
    return generate_password_hash(password)


def check_password(password, hash):
    return check_password_hash(hash, password)


def generate_random_int(digits):
    min_value = 10 ** (digits - 1)
    max_value = 10**digits - 1
    return secrets.randbelow(max_value - min_value + 1) + min_value


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    if data is None:
        return jsonify({"msg": "No Data", "flag": False})
    username = data["username"]
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
    file_ids = data["file_ids"]
    report_id = str(uuid.uuid4())
    report_info = OralReport(user_id=user_id, report_id=report_id)
    db.session.add(report_info)
    for file_id in file_ids:
        img_info = OralImage(image_id=file_id, report_id=report_id)
        db.session.add(img_info)
    db.session.commit()
    return jsonify({"msg": "Upload Success", "flag": True})


@app.route("/api/get_reports", methods=["GET"])
def get_reports():
    user_id = request.args.get("user_id", None)
    admin = request.args.get("admin", None)
    admin = True if admin == "true" else False
    if user_id is None:
        return jsonify({"msg": "No User ID", "flag": False})
    if admin:
        report_list = OralReport.query.all()
    else:
        report_list = OralReport.query.filter_by(user_id=user_id).all()
    report_list = [
        {
            "report_id": report.report_id,
            "upload_time": report.upload_time,
            "checked": report.description is not None,
        }
        for report in report_list
    ]
    return jsonify(
        {"msg": "Get Reports Success", "report_list": report_list, "flag": True}
    )


@app.route("/api/get_basic_info", methods=["GET"])
def get_basic_info():
    user_id = request.args.get("user_id", None)
    if user_id is None:
        return jsonify({"msg": "No User ID", "flag": False})
    user_info = User.query.filter_by(id=user_id).first()
    return jsonify(
        {
            "msg": "Get Basic Info Success",
            "name": user_info.name,
            "telephone": user_info.telephone,
            "department": user_info.department,
            "introduction": user_info.introduction,
            "flag": True,
        }
    )


@app.route("/api/update_basic_info", methods=["POST"])
def update_basic_info():
    data = request.get_json()
    if data is None:
        return jsonify({"msg": "No Data", "flag": False})
    user_id = data["user_id"]
    name = data["name"]
    telephone = data["telephone"]
    department = data["department"]
    introduction = data["introduction"]
    user_info = User.query.filter_by(id=user_id).first()
    user_info.name = name
    user_info.telephone = telephone
    user_info.department = department
    user_info.introduction = introduction
    db.session.commit()
    return jsonify({"msg": "Update Basic Info Success", "flag": True})


@app.route("/api/check_report", methods=["POST"])
def check_report():
    data = request.get_json()
    if data is None:
        return jsonify({"msg": "No Data", "flag": False})
    admin = data["admin"]
    if not admin:
        return jsonify({"msg": "No Permission", "flag": False})
    report_id = data["report_id"]
    description = data["description"]
    report_info = OralReport.query.filter_by(report_id=report_id).first()
    report_info.description = description
    report_info.check_time = datetime.now()
    db.session.commit()
    return jsonify({"msg": "Check Report Success", "flag": True})


@app.route("/api/get_report", methods=["GET"])
def get_report():
    report_id = request.args.get("report_id", None)
    if report_id is None:
        return jsonify({"msg": "No Report ID", "flag": False})
    report_info = OralReport.query.filter_by(report_id=report_id).first()
    images = OralImage.query.filter_by(report_id=report_id).all()
    report_info = {
        "msg": "Get Report Success",
        "report_id": report_info.report_id,
        "upload_time": report_info.upload_time,
        "description": report_info.description,
        "check_time": report_info.check_time,
        "images": [image.image_id for image in images],
        "flag": True,
    }
    return jsonify(
        {"msg": "Get Report Success", "report_info": report_info, "flag": True}
    )


@app.route("/api/send_email", methods=["GET"])
def send_email():
    email_addr = request.args.get("email", None)
    if email_addr is None:
        return jsonify({"msg": "No Email", "flag": False})
    user_info = User.query.filter_by(email=email_addr).first()
    email_addr = user_info.email
    msg = email.message.EmailMessage()
    captcha = generate_random_int(6)
    msg.set_content(f"您的验证码为{captcha}，请在5分钟内输入。")
    msg["Subject"] = "慧牙E密码重置"
    msg["From"] = mail_sender
    msg["To"] = email_addr
    server = smtplib.SMTP_SSL("smtp.qq.com", 465)
    server.login(mail_sender, mail_password)
    server.send_message(msg)
    server.quit()
    return jsonify({"msg": "Send Email Success", "captcha": captcha, "flag": True})


@app.route("/api/reset_password", methods=["POST"])
def reset_password():
    data = request.get_json()
    if data is None:
        return jsonify({"msg": "No Data", "flag": False})
    email_addr = data["email"]
    new_password = data["new_password"]
    user_info = User.query.filter_by(email=email_addr).first()
    user_info.password_hash = set_password(new_password)
    db.session.commit()
    return jsonify({"msg": "Reset Password Success", "flag": True})


@app.route("/api/generate_report", methods=["GET"])
def generate_report():
    report_id = request.args.get("report_id", None)
    report_info = OralReport.query.filter_by(report_id=report_id).first()
    images = OralImage.query.filter_by(report_id=report_id).all()
    file_ids = [image.image_id for image in images]
    params = {
        "env": env_id,
        "file_list": [{"fileid": file_id, "max_age": 7200} for file_id in file_ids],
    }
    url = "http://api.weixin.qq.com/tcb/batchdownloadfile"
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=json.dumps(params), headers=headers).json()
    file_list = response["file_list"]
    for file in file_list:
        download_url = file["download_url"]
        app.logger.info("Downloading file: %s", download_url)
        response = requests.get(download_url)
        if response.status_code == 200:
            filename = file["fileid"]
            with open(filename, "wb") as f:
                f.write(response.content)
            app.logger.info("Downloaded file: %s", filename)


if __name__ == "__main__":
    app.run(host=sys.argv[1], port=sys.argv[2])
