import imp
from app import app
from flask import render_template
from .forms import RegisterForm, LoginForm, BlogPostsForm, CommentsForm

@app.route('/')
def home():
    return render_template('Index.html')

@app.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegisterForm()
    return render_template('Register.html', form = form)