from functools import wraps
import os
from flask import jsonify, make_response, request
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')


def Error(error, status_code):
    # error = error
    error['status_code'] = status_code
    error['status'] = False
    # status_code = status_code

    return jsonify(error)


def encode_auth_token(user_id):
    """
    Generates the Auth Token
    :return: string
    """
    try:
        payload = {
            'exp': datetime.utcnow() + timedelta(days=0, seconds=7200),
            'iat': datetime.utcnow(),
            'sub': user_id
        }

        return jwt.encode(
            payload,
            SECRET_KEY,
            algorithm='HS256'
        )
    except Exception as e:
        return e


def decode_auth_token(auth_token):
    """
    Decodes the auth token
    :param auth_token:
    :return: integer|string
    """
    try:
        payload = jwt.decode(auth_token, SECRET_KEY, algorithms='HS256')
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return Error({
            'message': 'Token has expired. Please log in again.'
        }, 401)
    except jwt.InvalidTokenError:
        return Error({
            'message': 'Invalid token. Please log in again.'
        }, 401)
    except:
        return Error({
            'message': 'Some error occurred during the process. Please log in again.'
        }, 401)


def get_token_auth_header():
    auth = request.headers.get('Authorization', None)
    if not auth:
        return Error({
            'message': 'Authorization header is missing.'
        }, 401)

    parts = auth.split(' ')
    if parts[0] != 'Bearer':
        return Error({
            'message': 'Authorization header must start with "Bearer".'
        }, 401)

    elif len(parts) == 1:
        return Error({
            'message': 'Token not found.'
        }, 401)

    elif len(parts) > 2:
        return Error({
            'message': 'Authorization header must be \'Bearer <token>\'.'
        }, 401)

    token = parts[1]
    return token


def requires_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = get_token_auth_header()
        payload = decode_auth_token(token)

        return f(payload, *args, **kwargs)

    return wrapper
