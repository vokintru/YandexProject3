import os
from PIL import Image
from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from discord_webhook import DiscordWebhook, DiscordEmbed
import re
from data import db_session
from data.posts import Post
from data.users import User, Account
from data.comments import Comment
from forms.post import NewPostForm, RepostForm, CommentForm, EditPostForm
from forms.user import RegisterForm, LoginForm, EditForm
import random

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'boloto_p07G5n1W2E4f8Zq1Xc6T7yU'
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


def check_username(input_string):
    pattern = r'^[a-zA-Zа-яА-Я0-9_\.]+$'
    if re.match(pattern, input_string):
        return True
    else:
        return False


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


def get_user_id_by_name(name):
    db_sess = db_session.create_session()
    if name[0] == '@':
        account = db_sess.query(User).filter(User.username == name).first()
        db_sess.close()
    else:
        account = db_sess.query(Account).filter(Account.name == name).first()
        db_sess.close()
    if account:
        return account.id
    return None


def get_username_by_user_id(user_id):
    db_sess = db_session.create_session()
    account = db_sess.query(Account).filter(Account.id == user_id).first()
    user = db_sess.query(User).filter(User.id == user_id).first()
    db_sess.close()
    if account:
        return f"@{user.username}"
    return None


def get_user_id_by_username(username, sobaka):
    db_sess = db_session.create_session()
    if sobaka:
        username = username
    account = db_sess.query(Account).filter(Account.name == username).first()
    db_sess.close()
    if account:
        return account.id
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
            count_comments=0
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


@app.route('/editpost/<fromm>/<id>', methods=['GET', 'POST'])
def editpost(fromm, id):
    db_sess = db_session.create_session()
    post = db_sess.query(Post).filter(Post.id == id).first()
    if current_user.id != post.author:
        db_sess.close()
        return redirect('/')
    form = EditPostForm(text=post.text)
    if form.validate_on_submit():
        tegi = []
        for i in form.text.data.split(' '):
            if '#' in i:
                tegi.append(i)
        post.text = form.text.data
        db_sess.commit()
        db_sess.close()
        if fromm == 'profile':
            return redirect(f'/users/@{current_user.username}')
        return redirect('/')
    post.avatar = get_avatar_by_user_id(post.author)
    post.username = get_username_by_user_id(post.author)
    post.author = get_name_by_user_id(post.author)
    post.time = post.time.strftime("%d:%m:%Y %H:%M")
    orig_post_avatar = ""
    if post.orig_post != 0:
        with db_sess.no_autoflush:
            post.orig_post = db_sess.query(Post).filter(Post.id == post.orig_post).first()
            orig_post_avatar = db_sess.query(Account).filter(Account.id == post.orig_post.author).first().avatar
            post.orig_post.username = "@" + db_sess.query(User).filter(
                User.id == post.orig_post.author).first().username
            post.orig_post.name = db_sess.query(Account).filter(Account.id == post.orig_post.author).first().name
    db_sess.close()
    return render_template('edit_post.html', post=post, form=form, get_name_by_user_id=get_name_by_user_id,
                           orig_post_avatar=orig_post_avatar)


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
            count_comments=0,
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
    posts_all = process_posts(posts_all)
    posts = []
    for post in posts_all:
        if post.author.id in follow or post.author.id == current_user.id:
            posts.append(post)
    posts = list(reversed(posts))
    db_sess.close()
    return render_template('index.html', posts=posts, len=len, posts_all=posts_all, form=form)


@app.route("/follows", methods=['GET', 'POST'])
def follows():
    db_sess = db_session.create_session()
    if not current_user.is_authenticated:
        db_sess.close()
        return redirect('/login')

    account = db_sess.query(Account).filter(Account.id == current_user.id).first()
    follows_all = db_sess.query(Account).filter(Account.id.in_(account.follow)).all()
    follows_new = []
    for follow in follows_all:
        follow.avatar = get_avatar_by_user_id(follow.id)
        follow.username = get_username_by_user_id(follow.id)
        follows_new.append(follow)
    db_sess.close()
    return render_template('follow.html', follows=follows_new)


def process_posts(posts_all):
    db_sess = db_session.create_session()
    posts = []
    for post in posts_all:
        post.avatar = get_avatar_by_user_id(post.author)
        post.username = get_username_by_user_id(post.author)
        with db_sess.no_autoflush:
            post.badges = db_sess.query(Account).filter(Account.id == post.author).first().badges
        post.author = db_sess.query(Account).filter(Account.id == post.author).first()
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
    db_sess.close()
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
                count_reposts=0,
                count_comments=0,
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
                count_reposts=0,
                count_comments=0,
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
        if not check_username:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Юзернейм может содержать только буквы, нижние подчёркивание и точку")
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
                f"отличная жаба.",
            avatar=random.choice(default_avatars),
            followers=[],
            follow=[]
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.add(account)
        db_sess.commit()
        login_user(user, remember=True)
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
    params['badges'] = account.badges
    if current_user.is_authenticated:
        params['is_follow'] = int(current_user.id) in account.followers
    else:
        params['is_follow'] = False
    posts_all = db_sess.query(Post).all()
    posts_all = process_posts(posts_all)
    posts = []
    for post in posts_all:
        if post.author.id == user.id:
            posts.append(post)
    posts = list(reversed(posts))
    db_sess.close()
    return render_template('profile.html', posts=posts, posts_all=posts_all, get_id=get_user_id_by_name, **params)


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    db_sess = db_session.create_session()
    if not current_user.is_authenticated:
        db_sess.close()
        return redirect('/login')
    accaunt = db_sess.query(Account).filter(Account.id == current_user.id).first()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    form = EditForm(name=accaunt.name, bio=accaunt.bio, username=user.username)
    if form.validate_on_submit():
        if not check_username(form.username.data):
            return render_template('edit_profile.html',
                                   form=form,
                                   message="Юзернейм может содержать только буквы, нижние подчёркивание и точку")
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
            accaunt.avatar = filepath
        db_sess.commit()
        return redirect(f"/users/@{user.username}")
    db_sess.close()
    return render_template('edit_profile.html', title='Редактировать', form=form)


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
    return 'Done'


@app.route('/unfollow/<username>/<accid>')
@login_required
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
    return 'Done'


@app.route('/like/<post_id>')
@login_required
def like(post_id):
    db_sess = db_session.create_session()
    acc = db_sess.query(Account).filter(Account.id == current_user.id).first()
    post = db_sess.query(Post).filter(Post.id == post_id).first()
    liked = list(post.liked)
    liked.append(acc.id)
    post.liked = list(set(liked))
    db_sess.commit()
    db_sess.close()
    return 'Done'


@app.route('/unlike/<post_id>')
@login_required
def unlike(post_id):
    db_sess = db_session.create_session()
    acc = db_sess.query(Account).filter(Account.id == current_user.id).first()
    post = db_sess.query(Post).filter(Post.id == post_id).first()
    liked = list(post.liked)
    liked.remove(int(acc.id))
    post.liked = list(set(liked))
    db_sess.commit()
    db_sess.close()
    return 'Done'


@app.route('/report/<post_id>', methods=['GET'])
def report(post_id):
    db_sess = db_session.create_session()
    webhook = DiscordWebhook(url="https://discord.com/api/webhooks/1231209734783107164"
                                 "/t7a_idvkSuHt4Oq7jeQmyHwAiiQ7i9njx2B1_oWUgBolykZqI-hhN6ggBsDxnSkLAN4B")
    post = db_sess.query(Post).filter(Post.id == post_id).first()
    account = db_sess.query(Account).filter(Account.id == post.author).first()
    user = db_sess.query(User).filter(User.id == account.id).first()
    embed = DiscordEmbed(title="Type: POST", description=f"ID: {post_id}", color="79b253")

    embed.set_author(
        name=f"@{user.username}",
        url=f"https://zhabki.ru/users/@{user.username}",
    )

    embed.add_embed_field(name="Содержание", value=post.text, inline=False)
    embed.add_embed_field(name="Медиа", value=f"{post.file_path}", inline=False)
    if current_user.is_authenticated:
        embed.set_footer(text=f"From: @{db_sess.query(User).filter(User.id == current_user.id).first().username}")

    webhook.add_embed(embed)
    webhook.execute()
    db_sess.close()
    return 'Done'


@app.route('/report_comment/<comment_id>')
def report_comment(comment_id):
    db_sess = db_session.create_session()
    webhook = DiscordWebhook(url="https://discord.com/api/webhooks/1231209734783107164"
                                 "/t7a_idvkSuHt4Oq7jeQmyHwAiiQ7i9njx2B1_oWUgBolykZqI-hhN6ggBsDxnSkLAN4B")
    comment = db_sess.query(Comment).filter(Comment.id == comment_id).first()
    account = db_sess.query(Account).filter(Account.id == comment.author).first()
    user = db_sess.query(User).filter(User.id == account.id).first()
    embed = DiscordEmbed(title=f"Type: COMMENT", description=f"ID: {comment_id}", color="79b253")

    embed.set_author(
        name=f"@{user.username}",
        url=f"https://zhabki.ru/users/@{user.username}",
    )

    embed.add_embed_field(name="Содержание", value=comment.text, inline=False)
    if current_user.is_authenticated:
        embed.set_footer(text=f"From: @{db_sess.query(User).filter(User.id == current_user.id).first().username}")

    webhook.add_embed(embed)
    webhook.execute()
    db_sess.close()
    return 'Done'


@app.route('/comments/<post_id>', methods=['GET', 'POST'])
def comments(post_id):
    db_sess = db_session.create_session()
    # acc = db_sess.query(Account).filter(Account.id == current_user.id).first()
    form = CommentForm()
    post = db_sess.query(Post).filter(Post.id == post_id).first()
    posts_all = db_sess.query(Post).all
    if form.validate_on_submit():
        comment = Comment(
            author=current_user.id,
            text=form.text.data,
            post_id=post_id
        )
        db_sess.add(comment)
        post.count_comments += 1
        db_sess.commit()
        db_sess.close()
        return redirect(f'/comments/{post_id}')

    comments = list(reversed(db_sess.query(Comment).filter(Comment.post_id == post.id).all()))
    for comment in comments:
        comment.avatar = get_avatar_by_user_id(comment.author)
        comment.username = get_username_by_user_id(comment.author)
    post.avatar = get_avatar_by_user_id(post.author)
    post.username = get_username_by_user_id(post.author)
    post.author = get_name_by_user_id(post.author)
    post.time = post.time.strftime("%d:%m:%Y %H:%M")
    orig_post_avatar = ""
    if post.orig_post != 0:
        with db_sess.no_autoflush:
            post.orig_post = db_sess.query(Post).filter(Post.id == post.orig_post).first()
            orig_post_avatar = db_sess.query(Account).filter(Account.id == post.orig_post.author).first().avatar
            post.orig_post.username = "@" + db_sess.query(User).filter(
                User.id == post.orig_post.author).first().username
            post.orig_post.name = db_sess.query(Account).filter(Account.id == post.orig_post.author).first().name
    db_sess.close()
    return render_template('comments.html', title='Комментарии', form=form, post=post, posts_all=posts_all,
                           comments=comments, get_name_by_user_id=get_name_by_user_id,
                           orig_post_avatar=orig_post_avatar)


@app.route("/post/<postid>", methods=['GET', 'POST'])
def post(postid):
    db_sess = db_session.create_session()
    form = CommentForm()
    post = db_sess.query(Post).filter(Post.id == int(postid)).first()
    if form.validate_on_submit():
        comment = Comment(
            author=current_user.id,
            text=form.text.data,
            post_id=postid
        )
        db_sess.add(comment)
        post.count_comments += 1
        db_sess.commit()
        db_sess.close()
        return redirect(f'/comments/{postid}')

    post.avatar = get_avatar_by_user_id(post.author)
    post.username = get_username_by_user_id(post.author)
    post.badges = db_sess.query(Account).filter(Account.id == post.author).first().badges
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
    if post.orig_post != 0:
        with db_sess.no_autoflush:
            post.orig_post = db_sess.query(Post).filter(Post.id == post.orig_post).first()
            post.orig_post.avatar = get_avatar_by_user_id(post.orig_post.author)
            post.orig_post.username = get_username_by_user_id(post.orig_post.author)
            post.orig_post.badges = db_sess.query(Account).filter(Account.id == post.orig_post.author).first().badges
            post.orig_post.author = get_name_by_user_id(post.orig_post.author)
            post.orig_post.time = post.orig_post.time.strftime("%d:%m:%Y %H:%M")
    with db_sess.no_autoflush:
        comments = list(reversed(db_sess.query(Comment).filter(Comment.post_id == post.id).all()))
        for comment in comments:
            comment.avatar = get_avatar_by_user_id(comment.author)
            comment.username = get_username_by_user_id(comment.author)
            comment.name = get_name_by_user_id(comment.author)
    db_sess.close()
    return render_template('onepost.html', post=post, comments=comments, form=form)


@app.route('/delpost/<fromm>/<id>')
def delitepost(fromm, id):
    db_sess = db_session.create_session()
    post = db_sess.query(Post).filter(Post.id == int(id)).first()
    if post.author == current_user.id:
        if post:
            db_sess.delete(post)
            db_sess.commit()
    db_sess.close()
    if fromm == 'profile':
        return redirect(f'/users/@{current_user.username}')
    return redirect('/')


# ------------------------------------------------------(API)-----------------------------------------------------------

@app.route('/api/v1/status', methods=['GET'])
def api_v1_status():
    return "200"


@app.route('/adminlogin', methods=['GET'])
def adminlogin():
    key = request.args.get('key')
    username = request.args.get('username')
    if key == app.config['SECRET_KEY']:
        try:
            logout_user()
        except:
            pass
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.username == username).first()
        login_user(user, remember=True)
        db_sess.close()
        return redirect('/')
    return "NEPRAVILI KUCH"


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


@app.route('/api/v1/delpost', methods=['GET'])
def api_v1_delpost():
    key = request.args.get('key')
    postid = request.args.get('postid')
    if key == app.config['SECRET_KEY']:
        db_sess = db_session.create_session()
        post = db_sess.query(Post).filter(Post.id == int(postid)).first()
        if post:
            db_sess.delete(post)
            db_sess.commit()
            db_sess.close()
            return "Done"
        else:
            db_sess.close()
            return "Post wasn't found"
    return "401"


@app.route('/api/v1/delcomment', methods=['GET'])
def api_v1_delcomment():
    key = request.args.get('key')
    commentid = request.args.get('commentid')
    if key == app.config['SECRET_KEY']:
        db_sess = db_session.create_session()
        comment = db_sess.query(Comment).filter(Comment.id == int(commentid)).first()
        if comment:
            db_sess.delete(comment)
            post = db_sess.query(Post).filter(Post.id == comment.post_id).first()
            post.liked.remove(comment.author)
            db_sess.commit()
            db_sess.close()
            return "Done"
        else:
            db_sess.close()
            return "Comment wasn't found"
    return "401"


def main():
    db_session.global_init("db/users.db")
    app.run(host='0.0.0.0')


if __name__ == '__main__':
    main()
