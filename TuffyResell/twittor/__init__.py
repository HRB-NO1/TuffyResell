from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail

from twittor.config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'login'
mail = Mail()

from twittor.route import index, login, logout, register, user, page_not_found, \
    edit_profile, reset_password_request, password_reset, following, user_activate, post, post_item, post_edit, \
    post_delete, post_mark_sold, search

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    app.add_url_rule('/index', 'index', methods=['GET', 'POST'])
    app.add_url_rule('/', 'index', index, methods=['GET', 'POST'])
    app.add_url_rule('/login', 'login', login, methods=['GET', 'POST'])
    app.add_url_rule('/logout', 'logout', logout)
    app.add_url_rule('/register', 'register', register, methods=['GET', 'POST'])
    app.add_url_rule('/<username>', 'profile', user, methods=['GET', 'POST'])
    app.add_url_rule('/edit_profile', 'edit_profile', edit_profile, methods=['GET', 'POST'])
    app.add_url_rule(
        '/reset_password_request',
        'reset_password_request',
        reset_password_request,
        methods=['GET', 'POST']
    )
    app.add_url_rule(
        '/password_reset/<token>',
        'password_reset',
        password_reset,
        methods=['GET', 'POST']
    )
    app.register_error_handler(404, page_not_found)
    app.add_url_rule('/following', 'following', following)
    app.add_url_rule('/activate/<token>', 'user_activate', user_activate)
    app.add_url_rule('/post/<int:id>', 'post', post)
    app.add_url_rule('/post_item', 'post_item', post_item, methods=['GET', 'POST'])
    app.add_url_rule('/<username>/edit/<int:id>', 'post_edit', post_edit, methods=['GET', 'POST'])
    app.add_url_rule('/<username>/delete/<int:id>', 'post_delete', post_delete, methods=['GET', 'POST'])
    app.add_url_rule('/<username>/post_mark_sold/<int:id>', 'post_mark_sold', post_mark_sold, methods=['GET', 'POST'])

    app.add_url_rule('/search', 'search', search)
    return app
