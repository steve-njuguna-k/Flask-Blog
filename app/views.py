import datetime
from app import app
from flask import render_template, flash, redirect, request, url_for
from .email import send_email
from .models import Comments, Tags, User, db, Posts
from flask_login import current_user, login_user, logout_user, login_required
from .forms import CommentsForm, LoginForm, RegisterForm, BlogPostsForm, EditBlogPostsForm
from flask_bcrypt import Bcrypt
from .token import confirm_token, generate_confirmation_token
bcrypt = Bcrypt(app)

@app.route('/')
def home():
    posts = Posts.query.all()
    return render_template('Index.html', posts = posts)

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
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.confirmed ==0:
            flash('⚠️ Your Acount Is Not Activated! Please Check Your Email Inbox And Click The Activation Link We Sent To Activate It', 'danger')
            return render_template('Login.html', form=form)

        if user and bcrypt.check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('home'))
        
        if user and not bcrypt.check_password_hash(user.password, request.form['password']):
            flash('⚠️ Invalid Password!', 'danger')
            return render_template('Login.html', form=form)

        if not user:
            flash('⚠️ Account Does Not Exist!', 'danger')
            return render_template('Login.html', form=form)

    return render_template('Login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    user = current_user
    user.authenticated = False
    logout_user()
    # redirecting to home page
    return redirect(url_for('home'))

@app.route('/post/add', methods = ['GET', 'POST'])
@login_required
def add_post():
    form = BlogPostsForm()

    if form.validate_on_submit():
        post = Posts()
        post.title = form.title.data
        post.description = form.description.data
        post.category = form.category.data
        tag_string = form.tags.data
        tags = tag_string.split(",")
        for tag in tags:
            post_tag = add_tags(tag)
            print (post_tag)
            post.tags.append(post_tag)
            
        post.user_id = current_user._get_current_object().id
       
        db.session.add(post)
        db.session.commit()
        flash ('✅ New Post Successfully Created!', 'success')
        return redirect(url_for('add_post'))

    return render_template('Add Post.html', form = form)

def add_tags(tag):
    existing_tag = Tags.query.filter(Tags.name == tag.lower()).one_or_none()
    """if it does return existing tag objec to list"""
    if existing_tag is not None:
        return existing_tag
    else:
       new_tag = Tags()
       new_tag.name = tag.lower()
       return new_tag

@app.route('/post/<id>', methods=['POST','GET'])
@login_required
def post(id):
    post = Posts.query.filter_by(id = id).first()

    return render_template('Post.html', post = post)

@app.route('/post/<id>/edit', methods=['POST','GET'])
@login_required
def edit_post(id):
    form = EditBlogPostsForm(request.form)
    post = Posts.query.get_or_404(id)

    if form.validate_on_submit():
        post.title = form.title.data
        post.description = form.description.data
        post.category = form.category.data
            
        post.user_id = current_user._get_current_object().id
       
        db.session.add(post)
        db.session.commit()
        flash ('✅ New Post Successfully Updated!', 'success')
        return redirect(url_for('edit_post', id = id))

    elif request.method == 'GET':
        form.title.data = post.title
        form.description.data = post.description
        form.category.data = post.category

    if current_user.id == post.id:
        return render_template('Edit Post.html', post = post, form = form)
    else:
        flash('⚠️ You Are Not Authorized To Edit This Post! You Are Not The Author', 'danger')
        return redirect(url_for('home'))