from flask import jsonify
from app.exceptions import ValidationError
from . import api

@api.errorhandler(400)
def bad_request(e):
    response = jsonify({'error': str(e) })
    response.status_code = 400
    return response

@api.errorhandler(401)
def unauthorized(e):
    response = jsonify({'error': str(e)})
    response.status_code = 401
    return response


def forbidden(message):
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response


@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])
