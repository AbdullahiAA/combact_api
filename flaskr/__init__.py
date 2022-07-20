import os
from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from flaskr.auth import Error, encode_auth_token

from models import setup_db, Student
from flask_bcrypt import Bcrypt


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    bcrypt = Bcrypt(app)
    setup_db(app)

    cors = CORS(app, resources={r"*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type, Authorization"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )

        return response

    @app.route('/')
    def index():
        return jsonify({
            "success": True,
            "message": "Welcome to COMBACT API",
        }), 200

    @app.route('/register', methods=['POST'])
    def register():
        try:
            body = request.get_json()

            name = body.get('name', None).strip()
            username = body.get('username', None).strip()
            password = body.get('password', None).strip()
            confirm_password = body.get('confirm_password', None).strip()
            email = body.get('email', None).strip()
            gender = body.get('gender', None).strip()
            school_name = body.get('school_name', None).strip()
            level = body.get('level', None).strip()

            if not name or not username or not password or not confirm_password or not email or not gender or not school_name or not level:
                raise Error({
                    'message': 'All fields are required.'
                }, 400)
            elif password != confirm_password:
                raise Error({
                    'message': 'The password does not match.'
                }, 400)
            elif len(password) <= 4:
                raise Error({
                    'message': 'Password must be at least 4 characters long.'
                }, 400)

            # Confirm if the email does not exist
            similar_student_with_email = Student.query.filter_by(
                email=email).one_or_none()
            if similar_student_with_email != None:
                raise Error({
                    'message': 'This email has already been used.'
                }, 400)

            # Confirm if the username does not exist
            similar_student_with_username = Student.query.filter_by(
                username=username).one_or_none()
            if similar_student_with_username != None:
                raise Error({
                    'message': 'This username has already been used.'
                }, 400)

            # Encrypt the password
            password_hash = bcrypt.generate_password_hash(
                password).decode('UTF-8')

            # Register Student
            new_student = Student(
                name=name,
                username=username.lower(),
                password=password_hash,
                email=email,
                gender=gender,
                school_name=school_name,
                level=level,
                rank=0,
                completed_lessons=[],
                attempted_quizzes=[],
            )

            new_student.insert()

            formatted_student_data = new_student.format()
            token = encode_auth_token(formatted_student_data['id'])

            return jsonify({
                'message': 'Student Registered.',
                'student': formatted_student_data,
                'token': token,
                'status': True
            }), 201
        except:
            abort(400)

    @app.route('/login', methods=['POST'])
    def login():
        body = request.get_json()

        username = body.get('username', None).strip()
        password = body.get('password', None).strip()

        if not username or not password:
            raise Error({
                'message': 'All fields are required.'
            }, 400)

        found_user = Student.query.filter_by(
            username=username.lower()).one_or_none()

        if not found_user:
            raise Error({
                'message': 'User does not exist. Please register for an account.'
            }, 401)

        student = found_user.short()

        # Compare the passwords
        authenticated_user = bcrypt.check_password_hash(
            student['password'], password)

        if not authenticated_user:
            raise Error({
                'message': 'Incorrect login credentials.'
            }, 401)

        # If success
        formatted_student_data = found_user.format()
        token = encode_auth_token(formatted_student_data['id'])

        return jsonify({
            'message': 'Successful login.',
            'student': formatted_student_data,
            'token': token,
            'status': True
        }), 200

    # Errors

    @app.errorhandler(400)
    def bad_request(_error):
        return jsonify({
            'status': False,
            'status_code': 400,
            'message': 'Bad request'
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'status': False,
            'status_code': 404,
            'message': 'Not found',
        }), 404

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            'status': False,
            'status_code': 405,
            'message': 'Method not allowed'
        }), 405

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            'status': False,
            'status_code': 422,
            'message': 'Unprocessable entity'
        }), 422

    @app.errorhandler(500)
    def server_error(_error):
        return jsonify({
            'status': False,
            'status_code': 500,
            'message': 'Server error'
        }), 500

    @app.errorhandler(Error)
    def handle_auth_error(ex):
        response = jsonify(ex.error)
        response.status_code = ex.status_code
        return response

    return app
