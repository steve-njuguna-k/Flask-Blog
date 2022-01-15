from itsdangerous import URLSafeTimedSerializer
from app import app

def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt = app.config['SQLALCHEMY_DATABASE_URI'])


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt = app.config['SQLALCHEMY_DATABASE_URI'],
            max_age = expiration
        )
    except:
        return False
    return email