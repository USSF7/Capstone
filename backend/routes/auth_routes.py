"""
Authentication routes module.

Provides endpoints for user registration, login, JWT token refresh,
current-user retrieval, and Google OAuth 2.0 sign-in flow.

Routes:
    POST /api/auth/register  -- Create a new local account.
    POST /api/auth/login     -- Authenticate with email and password.
    POST /api/auth/refresh   -- Refresh an expired access token.
    GET  /api/auth/me        -- Get the currently authenticated user.
    GET  /api/auth/google    -- Initiate Google OAuth sign-in.
    GET  /api/auth/google/callback -- Handle Google OAuth callback.
"""

from flask import Blueprint, request, jsonify, redirect, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from services import AuthService
from models import User
from urllib.parse import urlencode

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user with email and password.

    Expects JSON body with ``name``, ``email``, and ``password`` fields.

    Returns:
        201: JWT tokens and user profile on success.
        400: Validation error (missing fields, email taken, etc.).
    """
    try:
        data = request.get_json()
        user = AuthService.register(
            data.get('name'),
            data.get('email'),
            data.get('password'),
        )
        tokens = AuthService.generate_tokens(user)
        return jsonify(tokens), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate a user with email and password.

    Expects JSON body with ``email`` and ``password``.

    Returns:
        200: JWT tokens and user profile on success.
        401: Invalid credentials.
    """
    try:
        data = request.get_json()
        user = AuthService.login(data.get('email'), data.get('password'))
        tokens = AuthService.generate_tokens(user)
        return jsonify(tokens), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Issue new JWT tokens using a valid refresh token.

    Requires a valid refresh token in the Authorization header.

    Returns:
        200: New JWT access and refresh tokens.
        404: User not found.
    """
    try:
        identity = get_jwt_identity()
        user = User.query.get(int(identity))
        if not user:
            return jsonify({'error': 'User not found'}), 404
        tokens = AuthService.generate_tokens(user)
        return jsonify(tokens), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    """Return the profile of the currently authenticated user.

    Requires a valid access token.

    Returns:
        200: User profile dict.
        404: User not found (token references deleted user).
    """
    try:
        identity = get_jwt_identity()
        user = User.query.get(int(identity))
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/google', methods=['GET'])
def google_login():
    """Redirect the user to Google's OAuth consent screen.

    Returns:
        302: Redirect to Google OAuth URL.
        400: Google OAuth not configured.
    """
    try:
        redirect_uri = current_app.config['GOOGLE_REDIRECT_URI']
        url = AuthService.get_google_auth_url(redirect_uri)
        return redirect(url)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/google/callback', methods=['GET'])
def google_callback():
    """Handle the OAuth callback from Google after user consent.

    Exchanges the authorization code for tokens, upserts the user, and
    redirects to the frontend with JWT tokens as query parameters.

    Returns:
        302: Redirect to frontend ``/auth/callback`` with tokens.
        400: Missing authorization code or exchange failure.
    """
    try:
        code = request.args.get('code')
        if not code:
            return jsonify({'error': 'Missing authorization code'}), 400

        redirect_uri = current_app.config['GOOGLE_REDIRECT_URI']
        user = AuthService.handle_google_callback(code, redirect_uri)
        tokens = AuthService.generate_tokens(user)

        # Redirect to frontend with tokens as query params
        frontend_url = current_app.config['FRONTEND_URL'].rstrip('/') + '/auth/callback'
        params = urlencode({
            'access_token': tokens['access_token'],
            'refresh_token': tokens['refresh_token'],
        })
        return redirect(f'{frontend_url}?{params}')
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
