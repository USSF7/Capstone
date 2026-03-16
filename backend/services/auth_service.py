from models import User
from database import db
from flask_jwt_extended import create_access_token, create_refresh_token
from flask import current_app
import requests as http_requests


class AuthService:
    """Service layer for authentication"""

    @staticmethod
    def register(name, email, password):
        if not name or not email or not password:
            raise ValueError("Name, email, and password are required")

        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")

        if User.query.filter_by(email=email).first():
            raise ValueError("Email already exists")

        user = User(name=name, email=email, auth_provider='local')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def login(email, password):
        if not email or not password:
            raise ValueError("Email and password are required")

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            raise ValueError("Invalid email or password")

        return user

    @staticmethod
    def get_google_auth_url(redirect_uri):
        client_id = current_app.config['GOOGLE_CLIENT_ID']
        if not client_id:
            raise ValueError("Google OAuth is not configured")

        params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': 'openid email profile',
            'access_type': 'offline',
            'prompt': 'consent',
        }
        query = '&'.join(f'{k}={v}' for k, v in params.items())
        return f'https://accounts.google.com/o/oauth2/v2/auth?{query}'

    @staticmethod
    def handle_google_callback(code, redirect_uri):
        client_id = current_app.config['GOOGLE_CLIENT_ID']
        client_secret = current_app.config['GOOGLE_CLIENT_SECRET']

        # Exchange code for tokens
        token_resp = http_requests.post('https://oauth2.googleapis.com/token', data={
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
        })
        if token_resp.status_code != 200:
            raise ValueError("Failed to exchange Google auth code")

        token_data = token_resp.json()
        access_token = token_data.get('access_token')

        # Fetch user info
        userinfo_resp = http_requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        if userinfo_resp.status_code != 200:
            raise ValueError("Failed to fetch Google user info")

        info = userinfo_resp.json()
        google_id = info['id']
        email = info['email']
        name = info.get('name', email)

        # Upsert user
        user = User.query.filter_by(google_id=google_id).first()
        if not user:
            user = User.query.filter_by(email=email).first()
            if user:
                # Link existing account to Google
                user.google_id = google_id
                user.auth_provider = 'google'
            else:
                user = User(
                    name=name,
                    email=email,
                    google_id=google_id,
                    auth_provider='google',
                )
                db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def generate_tokens(user):
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict(),
        }
