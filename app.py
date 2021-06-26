from flask import Flask, render_template,  redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import RegisterUserForm, LoginForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///flask_feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "secret"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

@app.route('/')
def redirect_to_register():
    return redirect('/register')

@app.route('/register', methods=["GET", "POST"])
def register_user():
    form = RegisterUserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(username=username, password=password, email=email, first_name=first_name, last_name=last_name)

        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username already taken. Please pick another.')
            return render_template('register_user_form.html', form=form)
        session['username'] = new_user.username
        return redirect(f'/users/{username}')
    else:
         return render_template('register_user_form.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login_user():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            session['username'] = user.username
            return redirect(f'/users/{username}')
        else:
            form.username.errors = ['Invalid username/password']
    else:
        return render_template('login_form.html', form=form)

@app.route('/users/<username>')
def show_secret(username):
    user = User.query.get_or_404(username)
    if "username" not in session:
        flash("Please login first.", "danger")
        return redirect('/login')
    else:
        return render_template('user.html', user=user)

@app.route('/logout')
def logout_user():
    session.pop('username')
    flash('You have been logged out.', 'info')
    return redirect('/')