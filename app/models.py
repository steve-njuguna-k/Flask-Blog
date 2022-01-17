import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'))
)

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name= db.Column(db.String(15), unique=True)
    last_name = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(256), unique=True)
    blogs = db.relationship('Posts',backref = 'user',lazy = "dynamic")
    comments = db.relationship('Comments',backref = 'user',lazy = "dynamic")
    image_file = db.Column(db.String(500), nullable=False, default='https://upload.wikimedia.org/wikipedia/commons/7/7c/Profile_avatar_placeholder_large.png')
    registered_on = db.Column(db.DateTime, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)

    def __init__(self, first_name, last_name, email, password, confirmed, confirmed_on=None):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.registered_on = datetime.datetime.now()
        self.confirmed = confirmed
        self.confirmed_on = confirmed_on

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f'User {self.first_name} {self.last_name}'

class Posts(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(20000), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    comment = db.relationship('Comments', backref='post', lazy='dynamic')
    tags = db.relationship('Tags',secondary=post_tags, back_populates="posts")
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    created_on = db.Column(db.DateTime, default = datetime.datetime.utcnow())
    updated_on = db.Column(db.DateTime, nullable=True)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<Posts: {}>'.format(self.description)

class Comments(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer,primary_key=True)
    comment = db.Column(db.String(1000), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    date_published = db.Column(db.DateTime, default = datetime.datetime.utcnow)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'))

    def __repr__(self):
        return '<Comment: {}>'.format(self.comment)

class Tags(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    posts = db.relationship('Posts', secondary = post_tags, back_populates = "tags")
    created_on = db.Column(db.DateTime, default = datetime.datetime.utcnow)

    def __repr__(self):
        return "<{}:{}>".format(self.id, self.name)