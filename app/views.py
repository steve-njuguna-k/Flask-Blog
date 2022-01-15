import datetime
from app import app
from flask import render_template, flash, redirect, request, url_for
from .email import send_email
from .models import Comments, User, db, Posts
from flask_login import current_user, login_user, logout_user, login_required
from .forms import CommentsForm, LoginForm, RegisterForm, BlogPostsForm
from flask_bcrypt import Bcrypt
from .token import confirm_token, generate_confirmation_token
bcrypt = Bcrypt(app)

@app.route('/')
def home():
    return render_template('Index.html')

@app.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data, password=password, confirmed=False)
        
        email = User.query.filter_by(email=form.email.data).first()
        if email:
            flash ("⚠️ The Email Address Already Exists! Choose Another One", "danger")
            return redirect(url_for("register"))
        
        else:
            db.session.add(user)
            db.session.commit()

            token = generate_confirmation_token(user.email)
            confirm_url = url_for('confirm_email', token=token, _external=True)
            html = render_template('Activation.html', confirm_url=confirm_url)
            subject = "[PITCH DECK] Confrim Your Email Address"
            send_email(user.email, subject, html)

            return redirect(url_for("email_verification_sent"))

    return render_template('Register.html', form=form)

@login_required
@app.route('/confirm/<token>')
def confirm_email(token):
    if User.confirmed==1:
        flash('✅ Account Already Confirmed! You Can Log In.', 'success')
        return redirect(url_for('login'))

    email = confirm_token(token)
    user = User.query.filter_by(email=email).first_or_404()

    if user.email == email:
        user.confirmed = True
        user.confirmed_on = datetime.datetime.now()
        db.session.add(user)
        db.session.commit()
        flash('✅ You Have Successfully Confirmed Your Email Address. You Can Now Log In. Thanks!', 'success')
    else:
        flash('⚠️ The Confirmation Link Is Invalid Or Has Expired.', 'danger')

    return redirect(url_for('login'))

@login_required
@app.route('/sent')
def email_verification_sent():
    if User.confirmed==1:
        flash('✅ You Can Now Log In!', 'success')
        return redirect(url_for('login'))
    else:
        flash('✅ Registration Successful! A Confirmation Link Has Been Sent To The Registered Email Address.', 'success')
        return redirect(url_for('register'))

@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    return render_template('Login.html', form = form)