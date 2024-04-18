import os
import random

from PIL import Image
from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename

from data import db_session
from data.posts import Post
from data.users import User, Account
from forms.post import NewPostForm, RepostForm
from forms.user import RegisterForm, LoginForm, EditForm

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'boloto_p07G5n1W2E4f8Zq1Xc6T7yU_220'
app.config['UPLOAD_FOLDER'] = 'static/content'
ALLOWED_EXTENSIONS_AVATAR = {'png', 'jpg', 'jpeg'}


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    ret = db_sess.get(User, user_id)
    db_sess.close()
    return ret


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_AVATAR


def get_avatar_by_user_id(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(Account).filter(Account.id == user_id).first()
    db_sess.close()
    if user:
        return user.avatar
    return None


def get_name_by_user_id(user_id):
    db_sess = db_session.create_session()
    account = db_sess.query(Account).filter(Account.id == user_id).first()
    user = db_sess.query(User).filter(User.id == user_id).first()
    db_sess.close()
    if account:
        if account.name != user.username:
            return account.name
        else:
            return f"@{user.username}"
    return None


def get_username_by_user_id(user_id):
    db_sess = db_session.create_session()
    account = db_sess.query(Account).filter(Account.id == user_id).first()
    user = db_sess.query(User).filter(User.id == user_id).first()
    db_sess.close()
    if account:
        return f"@{user.username}"
    return None


@app.route("/")
def index():
    return redirect('/all_posts')


@app.route("/all_posts", methods=['GET', 'POST'])
def all_posts():
    db_sess = db_session.create_session()
    form = NewPostForm()

    if form.validate_on_submit():
        tegi = []
        for i in form.text.data.split(' '):
            if '#' in i:
                tegi.append(i)
        post = Post(
            author=current_user.id,
            text=form.text.data,
            file_path=None,
            tegs=tegi,
            liked=[],
            orig_post=0,
            count_reposts=0,
        )
        db_sess.add(post)
        db_sess.commit()

        if form.file.data:
            posts_all = db_sess.query(Post).all()
            filename = secure_filename(form.file.data.filename)
            file_id = f"file_{len(posts_all) + 1}.{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_id)
            form.file.data.save(file_path)
            post.file_path = file_path
            post.liked = []
            post.orig_post = 0
            post.count_reposts = 0
            db_sess.commit()
            db_sess.close()
        return redirect('/')
    posts_all = db_sess.query(Post).all()
    posts = process_posts(posts_all)
    posts = list(reversed(posts))
    db_sess.close()
    return render_template('index.html', posts=posts, len=len, posts_all=posts_all, form=form)


@app.route("/subscriptions", methods=['GET', 'POST'])
def subscriptions():
    db_sess = db_session.create_session()
    form = NewPostForm()

    if form.validate_on_submit():
        tegi = []
        for i in form.text.data.split(' '):
            if '#' in i:
                tegi.append(i)
        post = Post(
            author=current_user.id,
            text=form.text.data,
            file_path=None,
            tegs=tegi,
            liked=[],
            orig_post=0,
            count_reposts=0,
        )
        db_sess.add(post)
        db_sess.commit()

        if form.file.data:
            posts_all = db_sess.query(Post).all()
            filename = secure_filename(form.file.data.filename)
            file_id = f"file_{len(posts_all) + 1}.{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_id)
            form.file.data.save(file_path)
            post.file_path = file_path
            post.liked = []
            post.orig_post = 0
            post.count_reposts = 0
            db_sess.commit()
        db_sess.close()
        return redirect('/')
    if not current_user.is_authenticated:
        db_sess.close()
        return redirect('/login')  # Редирект на страницу входа, если пользователь не авторизован

    account = db_sess.query(Account).filter(Account.id == current_user.id).first()
    follow = account.follow
    posts_all = db_sess.query(Post).all()
    posts = []
    for post in posts_all:
        if post.author in follow or post.author == current_user.id:
            post.avatar = get_avatar_by_user_id(post.author)
            post.username = get_username_by_user_id(post.author)
            post.author = get_name_by_user_id(post.author)
            post.time = post.time.strftime("%d:%m:%Y %H:%M")
            if current_user.id in post.liked:
                post.self_like = True
            else:
                post.self_like = False
            post.liked = len(post.liked)
            if str(post.file_path).split(".")[-1].lower() in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp',
                                                              'ico', 'tif', 'tiff']:
                post.file_type = "img"
            elif str(post.file_path).split(".")[-1].lower() in ["webm", "mp4", "ogg", "ogv", "avi", "mov", "wmv"]:
                post.file_type = "video"
            else:
                post.file_type = "None"
            posts.append(post)
    posts = list(reversed(posts))
    db_sess.close()
    return render_template('index.html', posts=posts, len=len, posts_all=posts_all, form=form)


def process_posts(posts_all):
    posts = []
    for post in posts_all:
        post.avatar = get_avatar_by_user_id(post.author)
        post.username = get_username_by_user_id(post.author)
        post.author = get_name_by_user_id(post.author)
        post.time = post.time.strftime("%d:%m:%Y %H:%M")
        if current_user.is_authenticated:
            if current_user.id in post.liked:
                post.self_like = True
            else:
                post.self_like = False
        else:
            post.self_like = False
        post.liked = len(post.liked)
        if str(post.file_path).split(".")[-1].lower() in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp',
                                                          'ico', 'tif', 'tiff']:
            post.file_type = "img"
        elif str(post.file_path).split(".")[-1].lower() in ["webm", "mp4", "ogg", "ogv", "avi", "mov", "wmv"]:
            post.file_type = "video"
        else:
            post.file_type = "None"
        posts.append(post)
    return posts


@app.route('/tegs_post/<teg>')
def tegs_post(teg):
    db_sess = db_session.create_session()
    posts_all = db_sess.query(Post).all()
    posts = []
    for post in posts_all:
        post.avatar = "/" + get_avatar_by_user_id(post.author)
        post.username = get_username_by_user_id(post.author)
        post.author = get_name_by_user_id(post.author)
        post.time = post.time.strftime("%d:%m:%Y %H:%M")
        if current_user.is_authenticated:
            if current_user.id in post.liked:
                post.self_like = True
            else:
                post.self_like = False
        else:
            post.self_like = False
        post.liked = len(post.liked)
        if str(post.file_path).split(".")[-1].lower() in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp',
                                                          'ico', 'tif', 'tiff']:
            post.file_type = "img"
        elif str(post.file_path).split(".")[-1].lower() in ["webm", "mp4", "ogg", "ogv", "avi", "mov", "wmv"]:
            post.file_type = "video"
        else:
            post.file_type = "None"
        if post.tegs is not None and '#' + teg in post.tegs:
            posts.append(post)
    posts = list(reversed(posts))
    # posts = db_sess.query(Post).filter(func.json_contains(Post.tegs, X) == 1).all()
    # posts = list(reversed(posts))
    db_sess.close()
    return render_template('tegs_posts.html', posts=posts)


# @app.route("/newpost", methods=['GET', 'POST'])
# def newpost():
#     form = NewPostForm()
#     if form.validate_on_submit():
#         db_sess = db_session.create_session()
#         tegi = []
#         for i in form.text.data.split(' '):
#             if '#' in i:
#                 tegi.append(i)
#         post = Post(
#             author=current_user.id,
#             text=form.text.data,
#             tegs=tegi,
#             liked=[],
#             orig_post=0,
#             count_reposts=0,
#         )
#         db_sess.add(post)
#         db_sess.commit()
#         db_sess.close()
#         return redirect('/')
#     return render_template('newpost.html', form=form)


def find_orig_post(db_sess, orig_post):
    orig_db = db_sess.query(Post).filter(Post.id == orig_post.id).first()
    while True:
        if orig_db.orig_post == 0:
            return orig_db
        else:
            orig_db = db_sess.query(Post).filter(Post.id == orig_db.orig_post).first()


@app.route("/repost/<orig_post>", methods=['GET', 'POST'])
def repost(orig_post):
    form = RepostForm()
    db_sess = db_session.create_session()
    orig_db = db_sess.query(Post).filter(Post.id == orig_post).first()
    post = orig_db
    post.avatar = get_avatar_by_user_id(post.author)
    post.username = get_username_by_user_id(post.author)
    post.author = get_name_by_user_id(post.author)
    post.time = post.time.strftime("%d:%m:%Y %H:%M")
    if str(post.file_path).split(".")[-1].lower() in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp',
                                                      'ico', 'tif', 'tiff']:
        post.file_type = "img"
    elif str(post.file_path).split(".")[-1].lower() in ["webm", "mp4", "ogg", "ogv", "avi", "mov", "wmv"]:
        post.file_type = "video"
    else:
        post.file_type = "None"
    if form.validate_on_submit():
        if orig_db.orig_post == 0:
            db_sess = db_session.create_session()
            tegi = []
            for i in form.text.data.split(' '):
                if '#' in i:
                    tegi.append(i)
            post = Post(
                author=current_user.id,
                text=form.text.data,
                tegs=tegi,
                liked=[],
                orig_post=orig_post,
                count_reposts=0
            )
            orig_db = db_sess.query(Post).filter(Post.id == orig_post).first()
            orig_db.count_reposts += 1
            db_sess.add(post)
            db_sess.commit()
            db_sess.close()
            return redirect('/')
        else:
            db_sess = db_session.create_session()
            orig_db = find_orig_post(db_sess, orig_db)
            tegi = []
            for i in form.text.data.split(' '):
                if '#' in i:
                    tegi.append(i)
            post = Post(
                author=current_user.id,
                text=form.text.data,
                tegs=tegi,
                liked=[],
                orig_post=orig_post,
                count_reposts=0
            )
            orig_db.count_reposts += 1
            db_sess.add(post)
            db_sess.commit()
            db_sess.close()
            return redirect('/')
    db_sess.close()
    return render_template('repost.html', form=form, post=orig_db)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.username == form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            db_sess.close()
            return redirect("/")
        db_sess.close()
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.username == form.username.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            username=form.username.data,
            hashed_password=form.password.data
        )

        default_avatars = [
            "static/img/default_avatars/avatar0.png",
            "static/img/default_avatars/avatar1.png",
            "static/img/default_avatars/avatar2.png",
            "static/img/default_avatars/avatar3.png",
            "static/img/default_avatars/avatar4.png",
            "static/img/default_avatars/avatar5.png",
            "static/img/default_avatars/avatar6.png",
            "static/img/default_avatars/avatar7.png",
            "static/img/default_avatars/avatar8.png",
            "static/img/default_avatars/avatar9.png",
        ]
        account = Account(
            name=form.username.data,
            bio=f"Мы почти ничего не знаем о {form.username.data}, но мы уверены, что {form.username.data} — "
                f"отличный человек.",
            avatar=random.choice(default_avatars),
            followers=[],
            follow=[]
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.add(account)
        db_sess.commit()
        db_sess.close()
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/users/@<username>')
def profile(username):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.username == username).first()
    account = db_sess.query(Account).filter(Account.id == user.id).first()
    params = {}
    params['accid'] = account.id
    params['username'] = username
    params['name'] = account.name
    params['avatar'] = account.avatar
    params['bio'] = account.bio
    params['folowers'] = len(account.followers)
    params['folow'] = len(account.follow)
    params['is_follow'] = int(current_user.id) in account.followers
    posts_all = db_sess.query(Post).all()
    posts = []
    for post in posts_all:
        if post.author == user.id:
            post.avatar = get_avatar_by_user_id(post.author)
            post.username = get_username_by_user_id(post.author)
            post.author = get_name_by_user_id(post.author)
            post.time = post.time.strftime("%d:%m:%Y %H:%M")
            if current_user.is_authenticated:
                if current_user.id in post.liked:
                    post.self_like = True
                else:
                    post.self_like = False
            else:
                post.self_like = False
            post.liked = len(post.liked)
            if str(post.file_path).split(".")[-1].lower() in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp',
                                                              'ico', 'tif', 'tiff']:
                post.file_type = "img"
            elif str(post.file_path).split(".")[-1].lower() in ["webm", "mp4", "ogg", "ogv", "avi", "mov", "wmv"]:
                post.file_type = "video"
            else:
                post.file_type = "None"
            posts.append(post)
    posts = list(reversed(posts))
    db_sess.close()
    return render_template('profile.html', posts=posts, **params)


# функция для кнопки подписаться
@app.route('/follow/<username>/<accid>')
@login_required
def follow(username, accid):
    db_sess = db_session.create_session()
    acc1 = db_sess.query(Account).filter(Account.id == current_user.id).first()
    acc2 = db_sess.query(Account).filter(Account.id == accid).first()
    f1 = list(acc1.follow)
    f1.append(int(accid))
    acc1.follow = list(set(f1))
    f2 = list(acc2.followers)
    f2.append(int(current_user.id))
    acc2.followers = list(set(f2))
    db_sess.commit()
    db_sess.close()
    return redirect(f'/users/@{username}')


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    db_sess = db_session.create_session()
    accaunt = db_sess.query(Account).filter(Account.id == current_user.id).first()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    form = EditForm(name=accaunt.name, bio=accaunt.bio, username=user.username)
    if form.validate_on_submit():
        accaunt.bio = form.bio.data
        accaunt.name = form.name.data
        user.username = form.username.data
        # Загрузка и сохранение аватарки
        file = form.avatar.data
        if file and allowed_file(file.filename):
            filename = str(user.id) + '.jpg'  # Имя файла устанавливаем на основе id пользователя
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            img = Image.open(file)
            # Обрезаем изображение до соотношения сторон 1:1
            width, height = img.size
            new_size = min(width, height)
            left = (width - new_size) / 2
            top = (height - new_size) / 2
            right = (width + new_size) / 2
            bottom = (height + new_size) / 2
            img_cropped = img.crop((left, top, right, bottom))
            # Сохраняем обрезанное изображение
            img_cropped.save(filepath, 'PNG')

        accaunt.avatar = "/" + filepath
        db_sess.commit()
        return redirect(f"/users/@{user.username}")
    db_sess.close()
    return render_template('edit_profile.html', title='Редактировать', form=form)


@app.route('/unfollow/<username>/<accid>')
def unfollow(username, accid):
    db_sess = db_session.create_session()
    acc1 = db_sess.query(Account).filter(Account.id == current_user.id).first()
    acc2 = db_sess.query(Account).filter(Account.id == accid).first()
    f1 = list(acc1.follow)
    f1.remove(int(accid))
    acc1.follow = list(set(f1))
    f2 = list(acc2.followers)
    f2.remove(int(current_user.id))
    acc2.followers = list(set(f2))
    db_sess.commit()
    db_sess.close()
    return redirect(f'/users/@{username}')


@app.route('/like/<post_id>')
def like(post_id):
    db_sess = db_session.create_session()
    acc = db_sess.query(Account).filter(Account.id == current_user.id).first()
    post = db_sess.query(Post).filter(Post.id == post_id).first()
    liked = list(post.liked)
    liked.append(acc.id)
    post.liked = list(set(liked))
    db_sess.commit()
    db_sess.close()
    return '200'


@app.route('/unlike/<post_id>')
def unlike(post_id):
    db_sess = db_session.create_session()
    acc = db_sess.query(Account).filter(Account.id == current_user.id).first()
    post = db_sess.query(Post).filter(Post.id == post_id).first()
    liked = list(post.liked)
    liked.remove(int(acc.id))
    post.liked = list(set(liked))
    db_sess.commit()
    db_sess.close()
    return '200'


# ------------------------------------------------------(API)-----------------------------------------------------------

@app.route('/api/v1/status', methods=['GET'])
def api_v1_status():
    return "200"


@app.route('/api/v1/getuser', methods=['GET'])
def api_v1_getuser():
    db_sess = db_session.create_session()
    username = request.args.get('username')
    user = db_sess.query(User).filter(User.username == username).first()
    account = db_sess.query(Account).filter(Account.id == user.id).first()
    response = {
        "user": {
            "id": user.id,
            "username": username,
        },
        "account": {
            "id": account.id,
            "username": username,
            "name": account.name,
            "bio": account.bio,
            "followers": account.followers,
        }
    }
    db_sess.close()
    return response


def main():
    db_session.global_init("db/users.db")
    app.run()


if __name__ == '__main__':
    main()
