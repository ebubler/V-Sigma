import os.path
from datetime import date
from datetime import datetime

from flask_socketio import SocketIO, emit, join_room
from flask import Flask, render_template, redirect, url_for, flash, request, make_response
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.fields.choices import SelectField
from wtforms.fields.datetime import DateField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, Optional
from sqlalchemy import Column, Integer, String, create_engine, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from hash import generate_hash, check_password, check_login
from functools import wraps


user_rooms = {}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        hpassword = request.cookies.get('hpassword')
        login = request.cookies.get('login')
        if login and hpassword:
            user = session.query(User).filter(User.login == login).first()
            if user:
                if user.hpassword == hpassword:
                    return f(*args, **kwargs)
        response = make_response("Cookie удалено")
        response.delete_cookie('login')
        response.delete_cookie('hpassword')
        return redirect(url_for('login'))
    return decorated_function


class AddPostForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
    file = FileField('Файл', validators=[Optional()])
    content = FileField('Контент', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'mp4', 'webm'],'Только изображения!')])
    submit = SubmitField('Добавить пост')


class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class RegisterForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    date_of_birth = DateField('Дата рождения', format='%Y-%m-%d', validators=[DataRequired()])
    sex = SelectField('Пол', choices=[('male', 'Мужской'), ('female', 'Женский')], validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')

class Edit_prof(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    date_of_birth = DateField('Дата рождения', format='%Y-%m-%d', validators=[DataRequired()])
    sex = SelectField('Пол', choices=[('male', 'Мужской'), ('female', 'Женский')], validators=[DataRequired()])
    photo_avatar = FileField(
        'Загрузить аватар',
        validators=[DataRequired(), FileAllowed(['jpg', 'jpeg', 'png'], 'Только изображения!')]
    )
    photo_banner = FileField(
        'Загрузить баннер',
        validators=[DataRequired(), FileAllowed(['jpg', 'jpeg', 'png'], 'Только изображения!')]
    )
    submit = SubmitField('Сохранить изменения')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app)

engine = create_engine("sqlite:///data/database.db")

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    login = Column(String(255), nullable=True)
    hlogin = Column(String(255), nullable=True)
    hpassword = Column(String(255), nullable=True)
    name = Column(String(50), nullable=True)
    surname = Column(String(50), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    sex = Column(String(50), nullable=True)
    photo_avatar = Column(String(255), nullable=True)
    photo_banner = Column(String(255), nullable=True)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

class Chat(Base):
    __tablename__ = 'chats'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=True)
    is_group = Column(String(255), nullable=True)
    about_us = Column(String(255), nullable=True)
    date_create = Column(Date, nullable=True)
    photo_avatar = Column(String(255), nullable=True)
    photo_banner = Column(String(255), nullable=True)

    users = Column(String(255), nullable=True)
    messages = Column(String(255), nullable=True)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


class Message(Base):
    __tablename__ = 'Messages'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=True)
    to_name = Column(String(255), nullable=True)
    date_create = Column(Date, nullable=True)
    message = Column(String(255), nullable=True)
    type_mess = Column(String(255), nullable=True)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


class Posts(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    author = Column(String(255), nullable=True)
    date_create = Column(Date, nullable=True)
    file = Column(String(255), nullable=True)
    content = Column(String(255), nullable=True)
    likes = Column(String(255), nullable=True)
    comments = Column(String(255), nullable=True)
    views = Column(String(255), nullable=True)


    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login_data = form.login.data
        password_data = form.password.data
        check_log = session.query(User).filter(User.login == login_data).first()
        if check_log:
            if check_password(password_data, check_log.hpassword):
                response = make_response(redirect(url_for('index')))
                response.delete_cookie('login')
                response.delete_cookie('hpassword')

                response.set_cookie('login', check_log.login, max_age=60 * 60 * 720)
                response.set_cookie('hpassword', check_log.hpassword, max_age=60 * 60 * 720)

                return response

    return render_template('login.html', form=form)

@app.route('/reg', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        login = form.login.data.lower()
        password = form.password.data
        name = form.name.data
        surname = form.surname.data
        date_of_birth = form.date_of_birth.data
        sex = form.sex.data
        check_login = session.query(User).filter(User.login == login).all()

        if check_login:
            return render_template('register.html', form=form, nick_error=True)

        h = generate_hash(login, password)
        hlogin = h[0]
        hpassword = h[1]

        new_user = User(login=login, hlogin=hlogin, hpassword=hpassword, name=name, surname=surname, date_of_birth=date_of_birth, sex=sex)

        response = make_response(redirect(url_for('index')))

        response.delete_cookie('login')
        response.delete_cookie('hpassword')

        response.set_cookie('login', login, max_age=60 * 60 * 720)
        response.set_cookie('hpassword', hpassword, max_age=60 * 60 * 720)

        session.add(new_user)

        session.commit()

        return response

    today = date.today()
    fourteen_years_ago = date(today.year - 14, today.month, today.day).strftime('%Y-%m-%d')
    return render_template('register.html', form=form, nick_error=False, true_date=fourteen_years_ago)

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    add_post_form = AddPostForm()
    if add_post_form.validate_on_submit():
        print(add_post_form.data)
    login = request.cookies.get('login')
    user = session.query(User).filter(User.login == login).first()
    return render_template('posts.html', user=user, add_post_form=add_post_form)

@app.route('/chat')
@login_required
def chat():
    login = request.cookies.get('login')
    user = session.query(User).filter(User.login == login).first()
    return render_template('chat.html', user=user)

@app.route('/chat/<chat_id>')
@login_required
def chat_to_id(chat_id):
    chat_id = int(chat_id)
    login = request.cookies.get('login')
    user = session.query(User).filter(User.login == login).first()
    chat = session.query(Chat).filter(Chat.id == chat_id).first()
    print(chat.id)
    if not (login in chat.users.strip(', ')):
        return redirect(url_for('index'))
    mess = []
    if chat.messages:
        for i in chat.messages.split(', '):
            mess.append(session.query(Message).where(Message.id == int(i)).first())

    return render_template('chat.html', user=user, chat_id=chat_id, messages=mess)

@app.route('/prof_settings', methods=['GET', 'POST'])
@login_required
def prof_settings():
    login = request.cookies.get('login')
    user = session.query(User).filter(User.login == login).first()
    form = Edit_prof(obj=user)
    today = date.today()
    fourteen_years_ago = date(today.year - 14, today.month, today.day).strftime('%Y-%m-%d')

    if request.method == 'POST':
        login = form.login.data.lower()
        name = form.name.data
        surname = form.surname.data
        date_of_birth = form.date_of_birth.data
        sex = form.sex.data
        img_avatar = request.files['img_avatar']
        img_banner = request.files['img_banner']

        updates = {
            "name": name,
            "surname": surname,
            "date_of_birth": date_of_birth,
            "sex": sex,
        }

        if img_banner.filename:
            filepath = os.path.join('static/user_img/', f'banner_{login}.png')
            img_banner.save(filepath)
            updates["photo_banner"] = f'banner_{login}.png'

        if img_avatar.filename:
            filepath = os.path.join('static/user_img/', f'avatar_{login}.png')
            img_avatar.save(filepath)
            updates["photo_avatar"] = f'avatar_{login}.png'

        user.update(**updates)

        session.commit()
        return render_template('edit_prof.html', user=user, form=form, true_date=fourteen_years_ago)
    return render_template('edit_prof.html', user=user, form=form, true_date=fourteen_years_ago)

@app.route('/log_out')
def log_out():
    response = make_response(redirect(url_for('index')))
    response.delete_cookie('login')
    response.delete_cookie('hpassword')
    return response


@socketio.on('join_chat')
@login_required
def handle_join_chat(data):
    """Подписка пользователя на комнату чата"""
    chat_id = data['chat_id']
    request.sid = chat_id  # Сохраняем chat_id в сессии
    print(f"User joined chat {chat_id}")


@socketio.on('send_message')
@login_required
def handle_send_message(data):
    """Обработка нового сообщения"""
    login = request.cookies.get('login')
    chat_id = data['chat_id']
    print(data)
    print(login)
    # Здесь можно сохранить сообщение в БД

    # Отправляем сообщение всем подписанным на этот чат
    emit('new_message', data, room=chat_id)
    print(f"New message in chat {chat_id}: {data['message']}")

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True, port=80)