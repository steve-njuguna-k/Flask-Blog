from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from flask_ckeditor import CKEditorField

class LoginForm(FlaskForm):
    email = StringField(label='Email Address', validators=[DataRequired(), Email(message='⚠️ Enter A Valid Email Address!')], render_kw={"placeholder": "Email Address"})
    password = PasswordField(label='Password', validators=[DataRequired(), Length(min=6, max=255,  message='⚠️ Password strength must be between %(min)d and %(max)d characters!')], render_kw={"placeholder": "Password"})
    show_password = BooleanField('Show password', id='check')
    submit = SubmitField(label=('Log In'))

class RegisterForm(FlaskForm):
    first_name = StringField(label='First Name', validators=[DataRequired(), Length(min=3, max=255,  message='⚠️ Name length must be between %(min)d and %(max)d characters!')], render_kw={"placeholder": "First Name"})
    last_name = StringField(label='Last Name', validators=[DataRequired(), Length(min=3, max=255,  message='⚠️ Name length must be between %(min)d and %(max)d characters!')], render_kw={"placeholder": "Last Name"})
    email = StringField(label='Email Address', validators=[DataRequired(), Email(message='⚠️ Enter A Valid Email Address!')], render_kw={"placeholder": "Email Address"})
    password = PasswordField(label='Password', validators=[DataRequired(), Length(min=6, max=255,  message='⚠️ Password strength must be between %(min)d and %(max)d characters!')], render_kw={"placeholder": "Password"})
    confirm_password = PasswordField(label='Confirm Password', validators=[DataRequired(), EqualTo('password', message='⚠️ The Passwords Entered Do Not Match!')], render_kw={"placeholder": "Confirm Password"})
    submit = SubmitField(label=('Sign Up'))

class BlogPostsForm(FlaskForm):
    title = StringField(label='Post Title', validators=[DataRequired(), Length(min=3, max=100,  message='⚠️ Title length must be between %(min)d and %(max)d characters!')], render_kw={"placeholder": "New Post Title Here..."})
    description = CKEditorField(label='Description',validators=[DataRequired(), Length(min=6, max=10000,  message='⚠️ Content length must be between %(min)d and %(max)d characters!')], render_kw={"placeholder": "Write Your Post Content Here...", 'rows': 20})
    category = SelectField(label='Select Category',choices=[
        ('AI & Machine Learning', 'AI & Machine Learning'),
        ('Big Data', 'Big Data'),
        ('Blockchain & Cryptocurrency', 'Blockchain & Cryptocurrency'),
        ('Career Development', 'Career Development'),
        ('Cloud Computing', 'Cloud Computing'),
        ('Cybersecurity', 'Cybersecurity'),
        ('Design + UX', 'Design + UX'),
        ('DevOps', 'DevOps'),
        ('Fintech', 'Fintech'),
        ('IoT: The Internet of Things', 'IoT: The Internet of Things'),
        ('Robotics', 'Robotics'),
        ('SaaS', 'SaaS'),
        ('Software Development', 'Software Development')
    ], render_kw={"placeholder": "Choose Category"})
    tags = StringField(label='Tags', validators=[DataRequired(), Length(min=3, max=50,  message='⚠️ Tag length must be between %(min)d and %(max)d characters!')], render_kw={"placeholder": "Tags (Add up to 5 short tags)"})
    submit = SubmitField('Submit')

class EditBlogPostsForm(FlaskForm):
    title = StringField(label='Post Title', validators=[DataRequired(), Length(min=3, max=100,  message='⚠️ Title length must be between %(min)d and %(max)d characters!')], render_kw={"placeholder": "New Post Title Here..."})
    description = CKEditorField(label='Description',validators=[DataRequired(), Length(min=6, max=10000,  message='⚠️ Content length must be between %(min)d and %(max)d characters!')], render_kw={"placeholder": "Write Your Post Content Here...", 'rows': 20})
    category = SelectField(label='Select Category',choices=[
        ('AI & Machine Learning', 'AI & Machine Learning'),
        ('Big Data', 'Big Data'),
        ('Blockchain & Cryptocurrency', 'Blockchain & Cryptocurrency'),
        ('Career Development', 'Career Development'),
        ('Cloud Computing', 'Cloud Computing'),
        ('Cybersecurity', 'Cybersecurity'),
        ('Design + UX', 'Design + UX'),
        ('DevOps', 'DevOps'),
        ('Fintech', 'Fintech'),
        ('IoT: The Internet of Things', 'IoT: The Internet of Things'),
        ('Robotics', 'Robotics'),
        ('SaaS', 'SaaS'),
        ('Software Development', 'Software Development')
    ], render_kw={"placeholder": "Choose Category"})
    submit = SubmitField('Submit')

class CommentsForm(FlaskForm):
    comment = TextAreaField(label = 'Comment',validators=[DataRequired(), Length(min=6, max=255,  message='⚠️ Comment length must be between %(min)d and %(max)d characters!')], render_kw={"placeholder": "Your Comment", 'rows': 5})
    submit= SubmitField('Submit')

class SearchForm(FlaskForm):
    search = StringField(label='Search Blog Articles', validators=[DataRequired(), Length(min=3, max=100,  message='⚠️ Search length must be between %(min)d and %(max)d characters!')], render_kw={"placeholder": "Search Blog Articles"})
    submit= SubmitField('Submit')