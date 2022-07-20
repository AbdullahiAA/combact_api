import json
from flask import Flask, request,  jsonify
from flask_cors import CORS
from flaskr.auth import Error, encode_auth_token, get_token_auth_header, requires_auth

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
            return Error({
                'message': 'All fields are required.'
            }, 400)
        elif password != confirm_password:
            return Error({
                'message': 'The password does not match.'
            }, 400)
        elif len(password) < 4:
            return Error({
                'message': 'Password must be at least 4 characters long.'
            }, 400)

        # Confirm if the email does not exist
        similar_student_with_email = Student.query.filter_by(
            email=email).one_or_none()
        if similar_student_with_email != None:
            return Error({
                'message': 'This email has already been used.'
            }, 400)

        # Confirm if the username does not exist
        similar_student_with_username = Student.query.filter_by(
            username=username).one_or_none()
        if similar_student_with_username != None:
            return Error({
                'message': 'This username has already been used.'
            }, 400)

        # Encrypt the password
        password_hash = bcrypt.generate_password_hash(
            password).decode('UTF-8')

        # Register Student
        new_student = Student(
            name=str.title(name),
            username=username.lower(),
            password=password_hash,
            email=email.lower(),
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
            'message': 'Welcome to COMBACT, ' + new_student.get_firstname(),
            'student': formatted_student_data,
            'token': token,
            'status': True
        }), 201

    @app.route('/login', methods=['POST'])
    def login():
        body = request.get_json()

        username = body.get('username', None).strip()
        password = body.get('password', None).strip()

        if not username or not password:
            return Error({
                'message': 'All fields are required.'
            }, 400)

        found_user = Student.query.filter_by(
            username=username.lower()).one_or_none()

        if not found_user:
            return Error({
                'message': 'Username does not exist. Please register for an account.'
            }, 401)

        student = found_user.short()

        # Compare the passwords
        authenticated_user = bcrypt.check_password_hash(
            student['password'], password)

        if not authenticated_user:
            return Error({
                'message': 'Incorrect login credentials.'
            }, 401)

        # If success
        formatted_student_data = found_user.format()
        token = encode_auth_token(formatted_student_data['id'])

        return jsonify({
            'message': 'Welcome back to COMBACT, ' + found_user.get_firstname(),
            'student': formatted_student_data,
            'token': token,
            'status': True
        }), 200

    @app.route('/student')
    @requires_auth
    def get_student_data(payload):
        user_id = payload

        student = Student.query.get(user_id)

        return jsonify({
            'message': 'Success.',
            'student': student.format(),
            'token': get_token_auth_header(),
            'status': True
        }), 200

    @app.route('/lessons/<int:lesson_id>/mark')
    @requires_auth
    def mark_question_as_completed(payload, lesson_id):
        user_id = payload

        student = Student.query.get(user_id)
        formatted_data = student.format()

        # return jsonify(formatted_data)

        completed_lessons = formatted_data['completed_lessons']
        print(completed_lessons)

        print("TYPE")

        if lesson_id not in completed_lessons:
            completed_lessons.append(lesson_id)

            student['completed_lessons'] = json.dumps(completed_lessons)
            # student['completed_lessons'].append(lesson_id)
            print(type(formatted_data))
            print(formatted_data)

            student.update()

            return jsonify({
                'status': True,
                'message': 'Lesson marked completed',
                'student': student
            }), 200
        else:
            return Error({
                'message': 'Can not perform the action at the moment'
            }, 400)

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

    # @app.errorhandler(Error)
    # def handle_auth_error(ex):
    #     response = jsonify(ex.error)
    #     # response.status_code = ex.status_code
    #     return response

    return app
