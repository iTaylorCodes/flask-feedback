from flask import Flask, render_template,  redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import RegisterUserForm, LoginForm, FeedbackForm
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
    if "username" not in session:
        return redirect('/register')
    else:
        return redirect(f'/users/{session["username"]}')

@app.route('/register', methods=["GET", "POST"])
def register_user():
    if "username" not in session:
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
                form.username.errors.append('Username or Email already taken. Please pick another.')
                return render_template('register_user_form.html', form=form)
            session['username'] = new_user.username
            return redirect(f'/users/{username}')
        else:
            return render_template('register_user_form.html', form=form)
    else:
        return redirect(f'/users/{session["username"]}')


@app.route('/login', methods=["GET", "POST"])
def login_user():
    if "username" not in session:
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
                return render_template('login_form.html', form=form)
        else:
            return render_template('login_form.html', form=form)
    else:
        return redirect(f'/users/{session["username"]}')


@app.route('/users/<username>')
def show_secret(username):
    if session["username"] == username:
        user = User.query.get_or_404(username)
        feedback = Feedback.query.all()
        if "username" not in session:
            flash("Please login first.", "danger")
            return redirect('/login')
        else:
            return render_template('user.html', user=user, feedback=feedback)
    else:
        return redirect(f'/users/{session["username"]}')

@app.route('/logout')
def logout_user():
    session.pop('username')
    flash('You have been logged out.', 'info')
    return redirect('/login')

@app.route('/users/<username>/delete', methods=["GET", "POST"])
def delete_user(username):
    if session["username"] == username:
        user = User.query.get_or_404(username)
        db.session.delete(user)
        db.session.commit()
        session.pop('username')
        flash("Your Account has been deleted.", "danger")
        return redirect('/')
    else:
        if "username" not in session:
            flash('Please login first', 'danger')
            return redirect('/login')
        else:
            return redirect(f'/users/{session["username"]}')

@app.route('/users/<username>/feedback/add', methods=["GET", "POST"])
def add_feedback(username):
    if session["username"] == username:
        user = User.query.get_or_404(username)
        form = FeedbackForm()
        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data
            username = username

            feedback = Feedback(title=title, content=content, username=username)
            db.session.add(feedback)
            db.session.commit()
            return redirect(f'/users/{username}')
        else:
            return render_template('feedback_form.html', form=form, user=user)
    else:
        return redirect(f'/users/{session["username"]}/feedback/add')

@app.route('/feedback/<int:feedback_id>/update', methods=["GET", "POST"])
def edit_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    if feedback.username == session["username"]:
        form = FeedbackForm()
        if form.validate_on_submit():
            feedback.title = form.title.data
            feedback.content = form.content.data

            db.session.commit()
            return redirect(f'/users/{feedback.username}')
        else:
            return render_template('edit_feedback_form.html', form=form, feedback=feedback)
    else:
        return redirect(f'/users/{session["username"]}')

@app.route('/feedback/<int:feedback_id>/delete', methods=["GET", "POST"])
def delete_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    if feedback.username == session["username"]:
        db.session.delete(feedback)
        db.session.commit()
        return redirect(f'/users/{feedback.username}')
    else:
        return redirect(f'/users/{session["username"]}')