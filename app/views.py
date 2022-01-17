import datetime
from app import app
from flask import render_template, flash, redirect, request, url_for
from .email import send_email
from .models import Comments, Tags, User, db, Posts
from flask_login import current_user, login_user, logout_user, login_required
from .forms import CommentsForm, LoginForm, RegisterForm, BlogPostsForm, EditBlogPostsForm, SearchForm
from flask_bcrypt import Bcrypt
from .token import confirm_token, generate_confirmation_token
from sqlalchemy import desc
bcrypt = Bcrypt(app)
import requests

@app.route('/')
def home():
    form = SearchForm()
    random_api = requests.get("https://api.quotable.io/random")
    quotes_api = requests.get("https://quotable.io/quotes?tags=technology")
    quotes = quotes_api.json()
    random = random_api.json()
    posts = Posts.query.order_by(desc(Posts.created_on)).all()
    return render_template('Index.html', posts = posts, quotes = quotes, random = random, form = form)

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

@app.route('/post/<int:id>', methods=['POST','GET'])
def post(id):
    form = SearchForm()
    post = Posts.query.filter_by(id = id).first()

    return render_template('Post.html', post = post, form = form)

@app.route('/post/<int:id>/edit', methods=['POST','GET'])
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
        flash ('✅ The Post Has Been Successfully Updated!', 'success')
        return redirect(url_for('edit_post', id = id))

    elif request.method == 'GET':
        form.title.data = post.title
        form.description.data = post.description
        form.category.data = post.category

    if current_user.id != post.user_id:
        flash('⚠️ You Are Not Authorized To Edit This Post! You Are Not The Author', 'danger')
        return redirect(url_for('home'))
    
    return render_template('Edit Post.html', post = post, form = form)

@app.route('/post/<int:id>/delete', methods=['GET', 'POST'])
@login_required
def delete_post(id):
    post = Posts.query.get_or_404(id)

    if current_user.id != post.user_id:
        flash('⚠️ You Are Not Authorized To Delete This Post! You Are Not The Author', 'danger')
        return redirect(url_for('home'))
    
    db.session.delete(post)
    db.session.commit()
    flash ('✅ The Post Has Been Successfully Delete!', 'success')
    return redirect(url_for('home', id = id))

@app.route('/posts')
@login_required
def my_posts():
    form = SearchForm()
    posts = Posts.query.filter_by(user_id = current_user._get_current_object().id)
    return render_template('My Posts.html', posts = posts, form = form)

@app.route('/profile')
def profile():
    form = SearchForm()
    user = current_user._get_current_object()
    return render_template('Profile.html', user = user, form = form)

@app.route('/<int:id>/comment', methods=['POST','GET'])
@login_required
def addComment(id):
    form = CommentsForm()
    searchform = SearchForm()
    post = Posts.query.get(id)
    comments = Comments.query.filter_by(post_id = id).all()
    comment = form.comment.data
    user_id = current_user._get_current_object().id

    if form.validate_on_submit():
        comment = Comments(comment = comment, post = post, user_id = user_id)
        db.session.add(comment)
        db.session.commit()
        flash ('✅ Your Comment Has Been Successfully Added!', 'success')
        return redirect(url_for('addComment', id = id))

    return render_template('Add Comment.html', form = form, post = post, comments = comments, searchform = searchform)

@app.route('/post/<int:id>/comment/<int:comment_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_comment(id, comment_id):
    form = SearchForm()
    comment = Comments.query.filter_by(id = comment_id).first()
    post = Posts.query.filter_by(id = id).first()

    if not comment:
        flash('⚠️ Comment Does Not Exist!', 'danger')
        return redirect(url_for('addComment', form = form))

    elif current_user.id != comment.user_id and current_user.id != comment.post_id:
        flash('⚠️ You Are Not Authorized To Delete This Comment! You Are Not The Post Author or Comment Author.', 'danger')
        return redirect(url_for('addComment', id = post.id, form = form))
    
    else:
        db.session.delete(comment)
        db.session.commit()
        flash ('✅ The Comment Has Been Successfully Deleted!', 'success')
        
    return redirect(url_for('addComment', id = post.id, form = form))

@app.route('/author/<int:id>')
def author(id):
    form = SearchForm()
    user = User.query.get(id)
    return render_template('Profile.html', user = user, form = form)

@app.route('/results', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    random_api = requests.get("https://api.quotable.io/random")
    quotes_api = requests.get("https://quotable.io/quotes?tags=technology")
    quotes = quotes_api.json()
    random = random_api.json()

    if form.validate_on_submit():
        searched = form.search.data
        query = Posts.query.filter(Posts.title.like('%' + searched + '%'))
        posts = query.order_by(Posts.title).all()

        return render_template('Search Results.html', form = form, posts = posts, quotes = quotes, random = random)

@app.route('/posts/category/ai-machine-learning', methods=['GET', 'POST'])
def aimachinelearning():
    form = SearchForm()
    random_api = requests.get("https://api.quotable.io/random")
    quotes_api = requests.get("https://quotable.io/quotes?tags=technology")
    quotes = quotes_api.json()
    random = random_api.json()
    posts = Posts.query.filter_by(category = "AI & Machine Learning").order_by(desc(Posts.created_on)).all()
    return render_template('AI & Machine Learning.html', posts = posts, form = form, quotes = quotes, random = random)

@app.route('/posts/category/big-data', methods=['GET', 'POST'])
def bigdata():
    form = SearchForm()
    random_api = requests.get("https://api.quotable.io/random")
    quotes_api = requests.get("https://quotable.io/quotes?tags=technology")
    quotes = quotes_api.json()
    random = random_api.json()
    posts = Posts.query.filter_by(category = "Big Data").order_by(desc(Posts.created_on)).all()
    return render_template('Big Data.html', posts = posts, form = form, quotes = quotes, random = random)

@app.route('/posts/category/blockchain-cryptocurrency', methods=['GET', 'POST'])
def blockchaincryptocurrency():
    form = SearchForm()
    random_api = requests.get("https://api.quotable.io/random")
    quotes_api = requests.get("https://quotable.io/quotes?tags=technology")
    quotes = quotes_api.json()
    random = random_api.json()
    posts = Posts.query.filter_by(category = "Blockchain & Cryptocurrency").order_by(desc(Posts.created_on)).all()
    return render_template('Blockchain & Cryptocurrency.html', posts = posts, form = form, quotes = quotes, random = random)

@app.route('/posts/category/career-development', methods=['GET', 'POST'])
def careerdevelopment():
    form = SearchForm()
    random_api = requests.get("https://api.quotable.io/random")
    quotes_api = requests.get("https://quotable.io/quotes?tags=technology")
    quotes = quotes_api.json()
    random = random_api.json()
    posts = Posts.query.filter_by(category = "Career Development").order_by(desc(Posts.created_on)).all()
    return render_template('Career Development.html', posts = posts, form = form, quotes = quotes, random = random)

@app.route('/posts/category/cloud-computing', methods=['GET', 'POST'])
def cloudcomputing():
    form = SearchForm()
    random_api = requests.get("https://api.quotable.io/random")
    quotes_api = requests.get("https://quotable.io/quotes?tags=technology")
    quotes = quotes_api.json()
    random = random_api.json()
    posts = Posts.query.filter_by(category = "Cloud Computing").order_by(desc(Posts.created_on)).all()
    return render_template('Cloud Computing.html', posts = posts, form = form, quotes = quotes, random = random)

@app.route('/posts/category/cybersecurity', methods=['GET', 'POST'])
def cybersecurity():
    form = SearchForm()
    random_api = requests.get("https://api.quotable.io/random")
    quotes_api = requests.get("https://quotable.io/quotes?tags=technology")
    quotes = quotes_api.json()
    random = random_api.json()
    posts = Posts.query.filter_by(category = "Cybersecurity").order_by(desc(Posts.created_on)).all()
    return render_template('Cybersecurity.html', posts = posts, form = form, quotes = quotes, random = random)

@app.route('/posts/category/design-ux', methods=['GET', 'POST'])
def designux():
    form = SearchForm()
    random_api = requests.get("https://api.quotable.io/random")
    quotes_api = requests.get("https://quotable.io/quotes?tags=technology")
    quotes = quotes_api.json()
    random = random_api.json()
    posts = Posts.query.filter_by(category = "Design + UX").order_by(desc(Posts.created_on)).all()
    return render_template('Design & UX.html', posts = posts, form = form, quotes = quotes, random = random)

@app.route('/posts/category/devops', methods=['GET', 'POST'])
def devops():
    form = SearchForm()
    random_api = requests.get("https://api.quotable.io/random")
    quotes_api = requests.get("https://quotable.io/quotes?tags=technology")
    quotes = quotes_api.json()
    random = random_api.json()
    posts = Posts.query.filter_by(category = "DevOps").order_by(desc(Posts.created_on)).all()
    return render_template('DevOps.html', posts = posts, form = form, quotes = quotes, random = random)

@app.route('/posts/category/fintech', methods=['GET', 'POST'])
def fintech():
    form = SearchForm()
    random_api = requests.get("https://api.quotable.io/random")
    quotes_api = requests.get("https://quotable.io/quotes?tags=technology")
    quotes = quotes_api.json()
    random = random_api.json()
    posts = Posts.query.filter_by(category = "Fintech").order_by(desc(Posts.created_on)).all()
    return render_template('Fintech.html', posts = posts, form = form, quotes = quotes, random = random)

@app.route('/posts/category/iot', methods=['GET', 'POST'])
def iot():
    form = SearchForm()
    random_api = requests.get("https://api.quotable.io/random")
    quotes_api = requests.get("https://quotable.io/quotes?tags=technology")
    quotes = quotes_api.json()
    random = random_api.json()
    posts = Posts.query.filter_by(category = "IoT").order_by(desc(Posts.created_on)).all()
    return render_template('IoT.html', posts = posts, form = form, quotes = quotes, random = random)

@app.route('/posts/category/robotics', methods=['GET', 'POST'])
def robotics():
    form = SearchForm()
    random_api = requests.get("https://api.quotable.io/random")
    quotes_api = requests.get("https://quotable.io/quotes?tags=technology")
    quotes = quotes_api.json()
    random = random_api.json()
    posts = Posts.query.filter_by(category = "Robotics").order_by(desc(Posts.created_on)).all()
    return render_template('Robotics.html', posts = posts, form = form, quotes = quotes, random = random)

@app.route('/posts/category/saas', methods=['GET', 'POST'])
def saas():
    form = SearchForm()
    random_api = requests.get("https://api.quotable.io/random")
    quotes_api = requests.get("https://quotable.io/quotes?tags=technology")
    quotes = quotes_api.json()
    random = random_api.json()
    posts = Posts.query.filter_by(category = "SaaS").order_by(desc(Posts.created_on)).all()
    return render_template('SaaS.html', posts = posts, form = form, quotes = quotes, random = random)

@app.route('/posts/category/software-developmet', methods=['GET', 'POST'])
def softwaredevelopmet():
    form = SearchForm()
    random_api = requests.get("https://api.quotable.io/random")
    quotes_api = requests.get("https://quotable.io/quotes?tags=technology")
    quotes = quotes_api.json()
    random = random_api.json()
    posts = Posts.query.filter_by(category = "Software Development").order_by(desc(Posts.created_on)).all()
    return render_template('Software Development.html', posts = posts, form = form, quotes = quotes, random = random)