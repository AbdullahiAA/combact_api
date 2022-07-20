import os
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')


class Error(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.error['status_code'] = status_code
        self.error['status'] = False
        self.status_code = status_code


def encode_auth_token(user_id):
    """
    Generates the Auth Token
    :return: string
    """
    try:
        payload = {
            'exp': datetime.utcnow() + timedelta(days=0, seconds=5),
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
        payload = jwt.decode(auth_token, SECRET_KEY)
        return payload['sub']
    except jwt.ExpiredSignatureError:
        raise Error({
            'message': 'Signature expired. Please log in again.'
        }, 401)
    except jwt.InvalidTokenError:
        raise Error({
            'message': 'Invalid token. Please log in again.'
        }, 401)
    except:
        raise Error({
            'message': 'Some error occurred during the process. Please log in again.'
        }, 401)
