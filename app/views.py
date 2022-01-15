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
    form = RegisterForm()
    return render_template('Register.html', form = form)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    return render_template('Login.html', form=form)