from pickle import loads, dumps
from flask import Flask, render_template, redirect
from data import db_session
from data.users import User, Account
from data.posts import Post
from forms.user import RegisterForm, LoginForm, EditForm
from forms.post import NewPostForm, RepostForm
import random
import datetime
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy import func

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'boloto_p07G5n1W2E4f8Zq1Xc6T7yU_220'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        account = db_sess.query(Account).filter(Account.id == current_user.id).first()
        follow = account.follow
        posts_all = db_sess.query(Post).all()
        posts = []
        for post in posts_all:
            if post.author in follow or post.author == current_user.id:
                posts.append(post)
        posts = list(reversed(posts))
    else:
        posts = db_sess.query(Post).all()

    return render_template('index.html', posts=posts, len=len)


@app.route('/tegs_post/<teg>')
def tegs_post(teg):
    db_sess = db_session.create_session()
    posts_all = db_sess.query(Post).all()
    posts = []
    for post in posts_all:
        if '#' + teg in post.tegs:
            posts.append(post)
    posts = list(reversed(posts))
    # posts = db_sess.query(Post).filter(func.json_contains(Post.tegs, X) == 1).all()
    print(posts)
    # posts = list(reversed(posts))
    return render_template('index.html', posts=posts)


@app.route("/newpost", methods=['GET', 'POST'])
def newpost():
    form = NewPostForm()
    if form.validate_on_submit():
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
            orig_post=0,
            count_reposts=0,
        )
        db_sess.add(post)
        db_sess.commit()
        return redirect('/')
    return render_template('newpost.html', form=form)


@app.route("/repost/<orig_post>", methods=['GET', 'POST'])
def repost(orig_post):
    form = RepostForm()
    db_sess = db_session.create_session()
    orig_db = db_sess.query(Post).filter(Post.id == orig_post).first()
    print(orig_db.author)
    if form.validate_on_submit():
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
        orig_db.count_reposts = 1
        db_sess.add(post)
        db_sess.commit()
        return redirect('/')
    return render_template('repost.html', form=form, post=orig_db)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.username == form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
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
    return render_template('profile.html', **params)


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
        db_sess.commit()
        return redirect(f"/users/@{user.username}")
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
    return redirect("/")


@app.route('/unlike/<post_id>')
def unlike(post_id):
    db_sess = db_session.create_session()
    acc = db_sess.query(Account).filter(Account.id == current_user.id).first()
    post = db_sess.query(Post).filter(Post.id == post_id).first()
    liked = list(post.liked)
    liked.remove(int(acc.id))
    post.liked = list(set(liked))
    db_sess.commit()
    return redirect("/")


def main():
    db_session.global_init("db/users.db")
    app.run()


if __name__ == '__main__':
    main()
