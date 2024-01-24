from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)


def set_password(password):
    return generate_password_hash(password)


def check_password(password, hash):
    return check_password_hash(hash, password)


@app.route("/api/login", methods=["POST"])
def login():
    username = request.form["name"]
    password = request.form["password"]


@app.route("/api/register", methods=["POST"])
def register():
    username = request.form["name"]
    password = request.form["password"]
    password_hash = set_password(password)
