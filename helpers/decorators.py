"""
This module defines decorators for API endpoint handling in the Flask app.

Decorators:
    handle_api_errors: Handles exceptions and standardizes API error responses.
    validate_json: Ensures that the request body contains valid JSON data.
"""

from functools import wraps
from flask import request
from werkzeug.exceptions import BadRequest
from helpers.api_helpers import create_error_response, create_success_response
from helpers.logger import logger


def handle_api_errors():
    """
    A decorator to handle exceptions and standardize API error responses.

    Returns:
        Function: The wrapped function with error handling.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}")
                return create_error_response(message="An unexpected error occurred."), 500
        return wrapper
    return decorator


def validate_json(required_keys=None):
    """
    A decorator to validate JSON request data for API routes.

    Args:
        required_keys (list, optional): A list of keys that must be present in the request JSON.
                                         If None, only validates that the body contains valid JSON.

    Returns:
        Function: The wrapped function with JSON validation.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                data = request.get_json()
                if not data:
                    return create_error_response(message="No data provided!"), 400
                if required_keys:
                    missing_keys = [key for key in required_keys if key not in data]
                    if missing_keys:
                        return create_error_response(
                            message=f"Missing required fields: {', '.join(missing_keys)}"
                        ), 400
                return func(*args, **kwargs)
            except BadRequest as e:
                logger.error(
                    f"BadRequest in {func.__name__}: Invalid JSON format: {str(e)}")
                return create_error_response(message=f"Invalid JSON format"), 400
            except Exception as e:
                logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
                return create_error_response(
                    message="An error occurred during JSON validation."), 500
        return wrapper
    return decorator
