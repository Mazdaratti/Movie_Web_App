"""
This module defines helper functions for common operations in the Flask app.
These functions help with generating consistent JSON responses.
"""
from flask import jsonify


def create_success_response(message=None, data=None):
    return create_response('sucess', message, data)


def create_error_response(message=None, data=None):
    return create_response('error', message, data)


def create_response(status, message=None, data=None):
    response = {"status": status}
    if message:
        response["message"] = message
    if data:
        response["data"] = data
    return jsonify(response)
