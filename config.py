import os

class Config:
    SQLALCHEMY_DATABASE_URI = (
        "mysql+pymysql://root:666666@localhost:3307/lab_chemical_db?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_AS_ASCII = False
    SECRET_KEY = os.urandom(24)

    # Email configuration for password reset
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or '587')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None or True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'qjlgghenshuai@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'ysdg eapx evwc xmgj'
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'qjlgghenshuai@gmail.com'
