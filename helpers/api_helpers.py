"""
This module defines helper functions for generating consistent JSON responses
in a Flask application. These functions are used to standardize the structure
of success and error responses.
"""

from flask import jsonify


def create_success_response(message=None, data=None):
    """
    Create a standardized JSON success response.

    Args:
        message (str, optional): A message describing the success. Defaults to None.
        data (any, optional): Additional data to include in the response. Defaults to None.

    Returns:
        Response: A Flask JSON response object with a success status.
    """
    return create_response('success', message, data)


def create_error_response(message=None, data=None):
    """
    Create a standardized JSON error response.

    Args:
        message (str, optional): A message describing the error. Defaults to None.
        data (any, optional): Additional data to include in the response. Defaults to None.

    Returns:
        Response: A Flask JSON response object with an error status.
    """
    return create_response('error', message, data)


def create_response(status, message=None, data=None):
    """
    Create a standardized JSON response with a given status.

    Args:
        status (str): The status of the response, e.g., 'success' or 'error'.
        message (str, optional): A message describing the response. Defaults to None.
        data (any, optional): Additional data to include in the response. Defaults to None.

    Returns:
        Response: A Flask JSON response object with the given status, message, and data.
    """
    response = {"status": status}
    if message:
        response["message"] = message
    if data:
        response["data"] = data
    return jsonify(response)
