import os

config_path = os.path.abspath(os.path.dirname(__file__))


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///" + os.path.join(config_path, 'TuffyResell.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'twittor/static/images'
    SECRET_KEY = 'abc123'
    TWEET_PER_PAGE = 8

    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@twittor.com')
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = os.environ.get('MAIL_PORT', 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 1)
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'qicesun0401@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'efafmlgfbplercbr')
    MAIL_SUBJECT_RESET_PASSWORD = '[TuffyResell] Please Reset Your Password'
    MAIN_SUBJECT_USER_ACTIVATE = '[TuffyResell] Please Activate Your Accout'

    # UPLOAD_FOLDER = 'static/images/'
