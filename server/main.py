from flask import Flask, render_template, redirect
from data import db_session
from data.users import User, Account
from forms.user import RegisterForm, LoginForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'boloto_p07G5n1W2E4f8Zq1Xc6T7yU0'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    return render_template("index.html")


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
            return render_template('register1.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.username == form.username.data).first():
            return render_template('register1.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            username=form.username.data,
            hashed_password=form.password.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template('register1.html', title='Регистрация', form=form)


@app.route('/register_complement', methods=['GET', 'POST'])
@login_required
def register_complement():
    form = RegisterForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = User(
            username=form.username.data,
            hashed_password=form.password.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template('register2.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/users/@<username>')
@login_required
def profile(username):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.username == username).first()
    account = db_sess.query(Account).filter(Account.id == user.id).first()
    params = {}
    params['name'] = account.name
    params['avatar'] = account.avatar
    params['bio'] = account.bio
    params['folowers'] = account.followers
    params['folow'] = account.follow
    return render_template('profile.html', **params)


def main():
    db_session.global_init("db/users.db")
    app.run()


if __name__ == '__main__':
    main()
