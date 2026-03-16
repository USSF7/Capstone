from flask import Blueprint, request, jsonify, redirect
from flask_jwt_extended import jwt_required, get_jwt_identity
from services import AuthService
from models import User
from urllib.parse import urlencode

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
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
    try:
        redirect_uri = request.host_url.rstrip('/') + '/api/auth/google/callback'
        url = AuthService.get_google_auth_url(redirect_uri)
        return redirect(url)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/google/callback', methods=['GET'])
def google_callback():
    try:
        code = request.args.get('code')
        if not code:
            return jsonify({'error': 'Missing authorization code'}), 400

        redirect_uri = request.host_url.rstrip('/') + '/api/auth/google/callback'
        user = AuthService.handle_google_callback(code, redirect_uri)
        tokens = AuthService.generate_tokens(user)

        # Redirect to frontend with tokens as query params
        frontend_url = 'http://localhost:8080/auth/callback'
        params = urlencode({
            'access_token': tokens['access_token'],
            'refresh_token': tokens['refresh_token'],
        })
        return redirect(f'{frontend_url}?{params}')
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
