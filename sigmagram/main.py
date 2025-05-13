import os.path
from datetime import date
from datetime import datetime

from flask_socketio import SocketIO
from flask import Flask, render_template, redirect, url_for, request, make_response, jsonify
from werkzeug.utils import secure_filename
from hash import generate_hash, check_password
from functools import wraps

from flaskform_class import AddPostForm, LoginForm, RegisterForm, Edit_prof
from db_init import global_init, create_session
from db_class import User, Chat, Message, Posts, Comments

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['MAX_CONTENT_LENGTH'] = None
socketio = SocketIO(app)

db_name = "database.db"
session_factory = global_init(db_name)
session = create_session(session_factory)

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


@app.route('/post/delete/<post_id>', methods=['DELETE'])
@login_required
def delete_post(post_id):
    post = session.query(Posts).filter(Posts.id == post_id).first()
    comments = session.query(Comments).filter(Comments.post_id == post_id).all()

    if post.author != request.cookies.get('login'):
        return jsonify({"error": "You are not the author of this post"}), 403

    if post:
        # Удаляем каждый комментарий по отдельности
        for comment in comments:
            session.delete(comment)

        session.delete(post)
        session.commit()
        return jsonify({"message": "Post deleted successfully"}), 200
    else:
        return jsonify({"error": "Post not found"}), 404

@app.route('/posts/range/user/<user_login>', methods=['GET'])
@login_required
def get_posts_range_user(user_login):
    try:
        start = request.args.get('start', default=0, type=int)
        end = request.args.get('end', default=10, type=int)

        if start < 0 or end < 0 or start > end:
            return jsonify({"error": "Invalid range parameters"}), 400
        posts = session.query(Posts).filter(Posts.author == user_login).order_by(Posts.id.desc()).offset(start).limit(end - start + 1).all()
        if not posts:
            return jsonify({"error": "Posts not found"}), 404

        result = []
        for post in posts:
            user = session.query(User).filter(User.login == post.author).first()
            result.append({
                "id": post.id,
                "title": post.title,
                "description": post.description,
                "content": post.content,
                "author": post.author,
                "file": post.file,
                "date_create": post.date_create,
                "author_name": user.name if user else "Unknown",
                "author_surname": user.surname if user else "User",
                "len_comments": len(session.query(Comments).filter_by(post_id=post.id).all()),
                "likes": len(post.likes.split(',')) - 1,
                "liked": request.cookies.get('login') in post.likes.split(','),
                'photo_avatar': session.query(User).filter(User.login == post.author).first().photo_avatar
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        session.close()

@app.route('/posts/range', methods=['GET'])
@login_required
def get_posts_range():
    try:
        start = request.args.get('start', default=0, type=int)
        end = request.args.get('end', default=10, type=int)

        if start < 0 or end < 0 or start > end:
            return jsonify({"error": "Invalid range parameters"}), 400
        posts = session.query(Posts).order_by(Posts.id.desc()).offset(start).limit(end - start + 1).all()
        if not posts:
            return jsonify({"error": "Posts not found"}), 404

        result = []
        for post in posts:
            user = session.query(User).filter(User.login == post.author).first()
            result.append({
                "id": post.id,
                "title": post.title,
                "description": post.description,
                "content": post.content,
                "author": post.author,
                "file": post.file,
                "date_create": post.date_create,
                "author_name": user.name if user else "Unknown",
                "author_surname": user.surname if user else "User",
                "len_comments": len(session.query(Comments).filter_by(post_id=post.id).all()),
                "likes": len(post.likes.split(',')) - 1,
                "liked": request.cookies.get('login') in post.likes.split(','),
                'photo_avatar': session.query(User).filter(User.login == post.author).first().photo_avatar
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        session.close()

@app.route('/posts/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    post = session.query(Posts).filter_by(id=post_id).first()
    if not (request.cookies.get('login') in post.likes.split(',')):
        post.likes += f'{request.cookies.get("login")},'
    else:
        post.likes = post.likes.replace(f'{request.cookies.get("login")},', '')
    session.commit()
    return jsonify({'likes': len(post.likes.split(',')) - 1,
                    'liked': request.cookies.get('login') in post.likes.split(',')
                    })

@app.route('/posts/<int:post_id>/comments', methods=['GET', 'POST'])
@login_required
def post_comments(post_id):
    current_user = request.cookies.get('login')
    if request.method == 'GET':
        comments = session.query(Comments).filter_by(post_id=post_id).all()
        return jsonify([{
            'author': c.author,
            'author_name': session.query(User).filter(User.login == c.author).first().name,
            'author_surname': session.query(User).filter(User.login == c.author).first().surname,
            'message': c.message,
            'date': c.date_create,
            'post_id': c.post_id,
            'photo_avatar': session.query(User).filter(User.login == c.author).first().photo_avatar
        } for c in comments])

    elif request.method == 'POST':
        data = request.get_json()
        comment = Comments(
            message=data['text'].strip(),
            post_id=post_id,
            author=current_user,
            date_create=datetime.now()
        )
        session.add(comment)
        session.commit()
        return jsonify({'success': True})

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    posts = session.query(Posts).all()
    for post in posts:
        post.author_name = session.query(User).filter(User.login == post.author).first().name
        post.author_surname = session.query(User).filter(User.login == post.author).first().surname
    add_post_form = AddPostForm()
    if add_post_form.validate_on_submit():
        try:
            title_data = add_post_form.title.data
            description_data = add_post_form.description.data
            author = request.cookies.get('login')
            date_create = datetime.now()

            media_files = []
            i = 0
            while True:
                file_key = f'media-{i}'
                if file_key not in request.files:
                    break
                file = request.files[file_key]
                if file.filename == '':
                    i += 1
                    continue

                filename = secure_filename(
                    f"{author}_{int(datetime.now().timestamp())}_{i}.{file.filename.split('.')[-1]}")
                filepath = os.path.join('static/uploads/media', filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                file.save(filepath)
                media_files.append(filename)
                i += 1

            regular_files = []
            for file in request.files.getlist('file-upload'):
                if file.filename == '':
                    continue

                filename = secure_filename(f"{author}_{int(datetime.now().timestamp())}_{file.filename}")
                filepath = os.path.join('static/uploads/files', filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                file.save(filepath)
                regular_files.append(filename)

            new_post = Posts(
                author=author,
                date_create=date_create,
                title=title_data,
                description=description_data,
                file=','.join(regular_files) if regular_files else None,
                content=','.join(media_files) if media_files else None,
                likes='',
                comments='',
                views=''
            )

            session.add(new_post)
            session.commit()

            return redirect(url_for('index'))

        except Exception as e:
            print(f"Ошибка при создании поста: {str(e)}")
            session.rollback()
    login = request.cookies.get('login')
    user = session.query(User).filter(User.login == login).first()
    return render_template('posts.html', user=user, add_post_form=add_post_form, posts=posts)

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

@app.route('/subscribe/<user>', methods=['GET'])
@login_required
def subscribe(user):
    login = request.cookies.get('login')
    data_user = session.query(User).filter(User.login == login).first()
    if login == user:
        return 'пользователь не может подписаться на самого себя'
    if user in str(data_user.subscriptions).split(','):
        data_user.subscriptions = data_user.subscriptions.replace(f'{user},', '')
    else:
        if data_user.subscriptions:
            data_user.subscriptions += f'{user},'
        else:
            data_user.subscriptions = f'{user},'
    data_user.update()
    session.commit()
    return 'ok'

@app.route('/friends', methods=['GET'])
@login_required
def friends():
    login = request.cookies.get('login')
    user = session.query(User).filter(User.login == login).first()
    friends = session.query(User).filter(
        User.subscriptions.contains(user.login + ','),
        User.login.in_(user.subscriptions.split(','))
    ).all()
    subscriptions_you = session.query(User).filter(User.subscriptions.contains(user.login + ','))
    subscriptions = session.query(User).filter(User.login.in_(user.subscriptions.split(',')))
    return render_template('friends.html', user=user, friends=friends, subscriptions_you=subscriptions_you)

@app.route('/prof', methods=['GET', 'POST'])
def redirect_to_profile():
    login = request.cookies.get('login')
    return redirect(url_for('prof', user_login=login))

@app.route('/prof/<user_login>', methods=['GET', 'POST'])
@login_required
def prof(user_login):
    login = request.cookies.get('login')
    user = session.query(User).filter(User.login == login).first()
    user_data = session.query(User).filter(User.login == user_login).first()

    add_post_form = AddPostForm()
    if add_post_form.validate_on_submit():
        try:
            title_data = add_post_form.title.data
            description_data = add_post_form.description.data
            author = request.cookies.get('login')
            date_create = datetime.now()

            media_files = []
            i = 0
            while True:
                file_key = f'media-{i}'
                if file_key not in request.files:
                    break
                file = request.files[file_key]
                if file.filename == '':
                    i += 1
                    continue

                filename = secure_filename(
                    f"{author}_{int(datetime.now().timestamp())}_{i}.{file.filename.split('.')[-1]}")
                filepath = os.path.join('static/uploads/media', filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                file.save(filepath)
                media_files.append(filename)
                i += 1

            regular_files = []
            for file in request.files.getlist('file-upload'):
                if file.filename == '':
                    continue

                filename = secure_filename(f"{author}_{int(datetime.now().timestamp())}_{file.filename}")
                filepath = os.path.join('static/uploads/files', filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                file.save(filepath)
                regular_files.append(filename)

            new_post = Posts(
                author=author,
                date_create=date_create,
                title=title_data,
                description=description_data,
                file=','.join(regular_files) if regular_files else None,
                content=','.join(media_files) if media_files else None,
                likes='',
                comments='',
                views=''
            )

            session.add(new_post)
            session.commit()

            return redirect(url_for('index'))

        except Exception as e:
            print(f"Ошибка при создании поста: {str(e)}")
            session.rollback()

    return render_template('prof.html', user=user, user_data=user_data, add_post_form=add_post_form)

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

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True, port=80, host='0.0.0.0')