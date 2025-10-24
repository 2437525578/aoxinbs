from flask import Blueprint, request, jsonify, current_app
from database import db
from models import User
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from datetime import datetime, timedelta

user_bp = Blueprint("user", __name__)

@user_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get("username")).first()
    if user and check_password_hash(user.password_hash, data.get("password")):
        # For now, just return success. In a real app, you'd return a token.
        return jsonify({"code": 200, "message": "登录成功", "role": user.role, "token": "dummy_token"}), 200
    current_app.logger.warning(f"Login failed for username: {data.get('username')}. Invalid credentials.")
    return jsonify({"code": 401, "message": "用户名或密码错误"}), 401

@user_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not all([username, email, password]):
        current_app.logger.warning("Registration attempt with missing fields.")
        return jsonify({"code": 400, "message": "缺少必要的字段"}), 400

    if User.query.filter_by(username=username).first():
        current_app.logger.warning(f"Registration attempt with existing username: {username}")
        return jsonify({"code": 409, "message": "用户名已存在"}), 409

    if User.query.filter_by(email=email).first():
        current_app.logger.warning(f"Registration attempt with existing email: {email}")
        return jsonify({"code": 409, "message": "邮箱已被注册"}), 409

    # Password complexity check (simple example)
    if len(password) < 6 or not any(char.isdigit() for char in password) or not any(char.isalpha() for char in password):
        current_app.logger.warning("Registration attempt with weak password.")
        return jsonify({"code": 400, "message": "密码必须至少包含6个字符，且包含字母和数字"}), 400

    try:
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=hashed_password, role="user") # Default role

        db.session.add(new_user)
        db.session.commit()
        current_app.logger.info(f"User registered successfully: {username}")

        return jsonify({"code": 201, "message": "用户注册成功"}), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error during user registration for {username}: {e}")
        return jsonify({"code": 500, "message": "用户注册失败"}), 500

@user_bp.route("/change_password", methods=["POST"])
def change_password():
    data = request.json
    username = data.get("username")
    old_password = data.get("oldPassword")
    new_password = data.get("newPassword")

    current_app.logger.info(f"Received change password request for username: {username}")

    if not all([username, old_password, new_password]):
        current_app.logger.warning(f"Missing required fields for change password for user: {username}")
        return jsonify({"code": 400, "message": "缺少必要的字段"}), 400

    user = User.query.filter_by(username=username).first()

    if not user:
        current_app.logger.warning(f"User {username} not found during change password attempt.")
        return jsonify({"code": 401, "message": "旧密码不正确或用户不存在"}), 401

    if not check_password_hash(user.password_hash, old_password):
        current_app.logger.warning(f"Old password does not match for user: {username}")
        return jsonify({"code": 401, "message": "旧密码不正确或用户不存在"}), 401

    # Password complexity validation for new password
    if len(new_password) < 6 or not any(char.isdigit() for char in new_password) or not any(char.isalpha() for char in new_password):
        current_app.logger.warning("Change password attempt with weak new password.")
        return jsonify({"code": 400, "message": "新密码必须至少包含6个字符，且包含字母和数字"}), 400

    try:
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        current_app.logger.info(f"Password for {username} successfully changed.")
        return jsonify({"code": 200, "message": "密码修改成功"}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error during password change for {username}: {e}")
        return jsonify({"code": 500, "message": "密码修改失败"}), 500

def send_reset_email(user):
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    token = s.dumps(user.email, salt="password-reset-salt")
    
    # In a real application, you would construct a full URL to your frontend reset page
    # For now, we'll just send the token.
    reset_link = f"http://localhost:8080/reset-password?token={token}" # Assuming frontend runs on 8080
    
    msg = Message("密码重置请求",
                  sender=current_app.config["MAIL_DEFAULT_SENDER"],
                  recipients=[user.email])
    try:
        mail = current_app.extensions['mail']
        msg.body = f"""您好，{user.username}！

您请求重置密码。请点击以下链接重置您的密码：
{reset_link}

此链接将在 15 分钟后失效。

如果您没有请求重置密码，请忽略此邮件。

此致，
您的管理团队
"""
        try:
            mail.send(msg)
            current_app.logger.info(f"Password reset email sent to {user.email}")
            return True
        except Exception as e:
            current_app.logger.error(f"Failed to send password reset email: {e}")
            print(f"DEBUG: Failed to send password reset email: {e}") # Add this line for debugging
            return False
    except Exception as e:
        current_app.logger.error(f"Failed to send password reset email to {user.email}: {e}")
        return False

@user_bp.route("/reset-password/request", methods=["POST"])
def request_password_reset():
    data = request.get_json()
    email = data.get("email")

    if not email:
        current_app.logger.warning("Password reset request received without email.")
        return jsonify({"code": 400, "message": "缺少邮箱地址"}), 400

    user = User.query.filter_by(email=email).first()
    if user:
        if send_reset_email(user):
            current_app.logger.info(f"Password reset requested for existing user: {email}")
            return jsonify({"code": 200, "message": "密码重置链接已发送至您的邮箱"}), 200
        else:
            return jsonify({"code": 500, "message": "发送密码重置邮件失败"}), 500
    else:
        current_app.logger.info(f"Password reset requested for non-existent email: {email}")
        # For security reasons, we don't reveal if the email exists or not
        return jsonify({"code": 200, "message": "密码重置链接已发送至您的邮箱"}), 200

@user_bp.route("/reset-password/confirm/<token>", methods=["POST"])
def reset_password_with_token(token):
    data = request.get_json()
    new_password = data.get("new_password")

    if not new_password:
        current_app.logger.warning("Password reset confirmation received without new password.")
        return jsonify({"code": 400, "message": "缺少新密码"}), 400

    # Password complexity validation (example: at least 8 characters, one uppercase, one lowercase, one digit)
    if len(new_password) < 8 or not any(char.isupper() for char in new_password) or \
       not any(char.islower() for char in new_password) or not any(char.isdigit() for char in new_password):
        current_app.logger.warning("Password complexity validation failed during reset.")
        return jsonify({"code": 400, "message": "密码必须至少8个字符，包含大小写字母和数字"}), 400

    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        email = s.loads(token, salt="password-reset-salt", max_age=900)  # 900 seconds = 15 minutes
    except Exception:
        current_app.logger.warning(f"Invalid or expired password reset token received: {token}")
        return jsonify({"code": 400, "message": "重置链接无效或已过期"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        current_app.logger.error(f"User not found for valid reset token: {email}")
        return jsonify({"code": 404, "message": "用户未找到"}), 404

    try:
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        current_app.logger.info(f"Password successfully reset for user: {email}")
        return jsonify({"code": 200, "message": "密码重置成功"}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error during password reset for {email}: {e}")
        return jsonify({"code": 500, "message": "密码重置失败"}), 500
