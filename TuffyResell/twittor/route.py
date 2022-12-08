from flask import render_template, redirect, url_for, request, \
    abort, current_app, flash
from flask_login import login_user, current_user, logout_user, login_required

from twittor.forms import LoginForm, RegisterForm, EditProfileForm, TweetForm, \
    PasswdResetRequestForm, PasswdResetForm
from twittor.models.user import User
from twittor.models.tweet import Tweet
from twittor import db
from twittor.email import send_email

from flask_uploads import UploadSet, IMAGES, configure_uploads

from werkzeug.utils import secure_filename
from werkzeug.utils import secure_filename
import uuid as uuid
import os

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *


@login_required
def index():
    page_num = int(request.args.get('page') or 1)
    tweets = Tweet.query.order_by(Tweet.create_time.desc()).paginate(
        page=page_num, per_page=current_app.config['TWEET_PER_PAGE'], error_out=False)
    next_url = url_for('index', page=tweets.next_num) if tweets.has_next else None
    prev_url = url_for('index', page=tweets.prev_num) if tweets.has_prev else None
    return render_template(
        'index.html', tweets=tweets.items, next_url=next_url, prev_url=prev_url
    )


def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        u = User.query.filter_by(username=form.username.data).first()
        if u is None or not u.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(u, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('index'))
    return render_template('login.html', title="Sign In", form=form)


def logout():
    logout_user()
    return redirect(url_for('login'))


def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', title='Registration', form=form)


@login_required
def user(username):
    u = User.query.filter_by(username=username).first()
    if u is None:
        abort(404)
    page_num = int(request.args.get('page') or 1)
    tweets = u.tweets.order_by(Tweet.create_time.desc()).paginate(
        page=page_num,
        per_page=current_app.config['TWEET_PER_PAGE'],
        error_out=False)

    next_url = url_for(
        'profile',
        page=tweets.next_num,
        username=username) if tweets.has_next else None
    prev_url = url_for(
        'profile',
        page=tweets.prev_num,
        username=username) if tweets.has_prev else None
    if request.method == 'POST':
        if request.form['request_button'] == 'Follow':
            current_user.follow(u)
            db.session.commit()
        elif request.form['request_button'] == "Unfollow":
            current_user.unfollow(u)
            db.session.commit()
        else:
            if "@fullerton.com" in u.email or "@csu.fullerton.edu" in u.email:
                flash("Send an email to your email address, please check!!!!")
                send_email_for_user_activate(current_user)
            else:
                flash("Only CSUF student or staff email can active their account")

    return render_template(
        'user.html',
        title='Profile',
        tweets=tweets.items,
        user=u,
        next_url=next_url,
        prev_url=prev_url
    )


def send_email_for_user_activate(user):
    token = user.get_jwt()
    url_user_activate = url_for(
        'user_activate',
        token=token,
        _external=True
    )
    send_email(
        subject=current_app.config['MAIN_SUBJECT_USER_ACTIVATE'],
        recipients=[user.email],
        text_body=render_template(
            'email/user_activate.txt',
            username=user.username,
            url_user_activate=url_user_activate
        ),
        html_body=render_template(
            'email/user_activate.html',
            username=user.username,
            url_user_activate=url_user_activate
        )
    )


def user_activate(token):
    user = User.verify_jwt(token)
    if not user:
        msg = "Token has expired, please try to re-send email"
    else:
        user.is_activated = 1
        db.session.commit()
        msg = 'User has been activated!'
    return render_template(
        'user_activate.html', msg=msg
    )


def page_not_found(e):
    return render_template('404.html'), 404


@login_required
def edit_profile():
    form = EditProfileForm()
    if request.method == 'GET':
        form.about_me.data = current_user.about_me
        form.email.data = current_user.email

    if form.validate_on_submit():
        current_user.about_me = form.about_me.data
        current_user.email = form.email.data
        if form.profile_pic.data:
            if current_user.profile_pic:
                item_name = current_user.profile_pic
                delete_avatar(item_name)
            current_user.profile_pic = request.files['profile_pic']
            pic_filename = secure_filename(current_user.profile_pic.filename)
            pic_name = str(uuid.uuid1()) + "_" + pic_filename
            saver = request.files['profile_pic']
            current_user.profile_pic = pic_name
            saver.save(os.path.join(current_app.config['UPLOAD_FOLDER_AVATAR'], pic_name))

        db.session.commit()
        flash("Profile updated successfully!")
        return redirect(url_for('profile', username=current_user.username, email=current_user.email))
    return render_template('edit_profile.html', form=form)


def delete_avatar(item_name):
    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER_AVATAR'], item_name))
    return


def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = PasswdResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash(
                "You should soon receive an email allowing you to reset your \
                password. Please make sure to check your spam and trash \
                if you can't find the email."
            )
            token = user.get_jwt()
            url_password_reset = url_for(
                'password_reset',
                token=token,
                _external=True
            )
            url_password_reset_request = url_for(
                'reset_password_request',
                _external=True
            )
            send_email(
                subject=current_app.config['MAIL_SUBJECT_RESET_PASSWORD'],
                recipients=[user.email],
                text_body=render_template(
                    'email/passwd_reset.txt',
                    url_password_reset=url_password_reset,
                    url_password_reset_request=url_password_reset_request
                ),
                html_body=render_template(
                    'email/passwd_reset.html',
                    url_password_reset=url_password_reset,
                    url_password_reset_request=url_password_reset_request
                )
            )
        return redirect(url_for('login'))
    return render_template('password_reset_request.html', form=form)


def password_reset(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_jwt(token)
    if not user:
        return redirect(url_for('login'))
    form = PasswdResetForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template(
        'password_reset.html', title='Password Reset', form=form
    )


@login_required
def following():
    # get all user and sort by followers
    page_num = int(request.args.get('page') or 1)
    tweets = current_user.followed_tweets().paginate(
        page=page_num, per_page=current_app.config['TWEET_PER_PAGE'], error_out=False)
    next_url = url_for('index', page=tweets.next_num) if tweets.has_next else None
    prev_url = url_for('index', page=tweets.prev_num) if tweets.has_prev else None
    return render_template(
        'following.html', tweets=tweets.items, next_url=next_url, prev_url=prev_url
    )


@login_required
def post(id):
    tweet = Tweet.query.get_or_404(id)
    return render_template('post.html', tweet=tweet)


@login_required
def post_item():
    form = TweetForm()
    if form.validate_on_submit():

        pic_filename = form.item_pic.data

        if pic_filename:
            form.item_pic = request.files['item_pic']
            pic_filename = secure_filename(form.item_pic.filename)
            pic_name = str(uuid.uuid1()) + "_" + pic_filename
            saver = request.files['item_pic']
            form.item_pic = pic_name
            saver.save(os.path.join(current_app.config['UPLOAD_FOLDER_ITEM_PIC'], pic_name))
            t = Tweet(body=form.tweet.data, item_name=form.item_name.data, price=form.price.data, author=current_user,
                      item_pic=pic_name)
        else:
            t = Tweet(body=form.tweet.data, item_name=form.item_name.data, price=form.price.data, author=current_user)
        db.session.add(t)
        db.session.commit()
        flash("Item has been posted!")
        return redirect(url_for('index'))
    return render_template('post_item.html', form=form)


@login_required
def post_edit(username, id):
    t = Tweet.query.get_or_404(id)
    form = TweetForm()
    if form.validate_on_submit():
        t.item_name = form.item_name.data
        t.body = form.tweet.data
        t.price = form.price.data

        pic_filename = form.item_pic.data
        if pic_filename:
            if t.item_pic:
                delete_item_pic(t.item_pic)
            t.item_pic = request.files['item_pic']
            pic_filename = secure_filename(t.item_pic.filename)
            pic_name = str(uuid.uuid1()) + "_" + pic_filename
            saver = request.files['item_pic']
            t.item_pic = pic_name
            saver.save(os.path.join(current_app.config['UPLOAD_FOLDER_ITEM_PIC'], pic_name))

        db.session.add(t)
        db.session.commit()
        flash("Post has been updated")
        return redirect(url_for('post', id=id))
    form.item_name.data = t.item_name
    form.tweet.data = t.body
    form.price.data = t.price
    form.item_pic.data = t.item_pic

    return render_template("edit_post.html", form=form, t=t)


def delete_item_pic(item_name):
    os.remove(os.path.join(current_app.config['UPLOAD_FOLDER_ITEM_PIC'], item_name))
    return


@login_required
def post_delete(username, id):
    t = Tweet.query.get_or_404(id)
    try:
        if t.item_pic:
            delete_item_pic(t.item_pic)
        db.session.delete(t)
        db.session.commit()
        flash("Item post was deleted.")
        return redirect(request.referrer)
    except:
        flash("Oops! There is a prolem deleting the item post.")
        return redirect(request.referrer)


@login_required
def post_mark_sold(username, id):
    t = Tweet.query.get_or_404(id)
    try:
        t.sell_status = 1
        db.session.commit()
        flash("Item post was marked as sold.")
        return redirect(request.referrer)
    except:
        flash("Oops! There is a prolem marking the item post.")
        return redirect(request.referrer)


@login_required
def search():
    keyword = request.args.get('keyword')
    page_num = int(request.args.get('page') or 1)
    # tweets = Tweet.query.filter(or_(Tweet.item_name.contains(keyword),
    #                                 Tweet.body.contains(keyword))).order_by(Tweet.create_time.desc())
    # tweets = tweets.all()

    tweets = Tweet.query.filter(or_(Tweet.price.contains(keyword),Tweet.item_name.contains(keyword),
                                    Tweet.body.contains(keyword))).order_by(Tweet.create_time.desc()).all()
    # tweets = tweets.order_by(Tweet.create_time.desc()).paginate(
    #     page=page_num, per_page=current_app.config['TWEET_PER_PAGE'], error_out=False)
    # next_url = url_for('index', page=tweets.next_num) if tweets.has_next else None
    # prev_url = url_for('index', page=tweets.prev_num) if tweets.has_prev else None

    if tweets:
        # return render_template('index.html', tweets=tweets.items, next_url=next_url, prev_url=prev_url)
        tweets_len = len(tweets)
        flash('Found ' + str(tweets_len) + ' result(s)')
        return render_template('index.html', tweets=tweets)

    else:
        flash('No post found')
        return redirect(url_for('index'))

