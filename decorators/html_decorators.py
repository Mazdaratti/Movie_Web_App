"""
This module provides reusable decorators for HTML routes in Flask applications.

Decorators included:
- `handle_errors`: Handles exceptions and renders error pages for HTML routes.
- `validate_form`: Ensures required form fields are present in POST requests.
- `validate_user`: Verifies the existence of a user by their user ID.
"""
from functools import wraps
from flask import render_template, redirect, request
from helpers.logger import logger
from helpers.html_helpers import flash_message, render_error_page


def handle_errors():
    """
    A decorator to handle exceptions for HTML routes and render appropriate error pages.

    Usage:
        @handle_errors()
        def your_route():
            ...

    Returns:
        Function: The wrapped function with error handling.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}")
                # Render a generic error page for unhandled exceptions
                return render_template(
                    "error.html", error_message="An unexpected error occurred."), 500

        return wrapper

    return decorator


def validate_form(required_fields=None):
    """
    A decorator to validate if required form fields are present in POST requests.

    Args:
        required_fields (list, optional): List of required fields for the form.

    Usage:
        @validate_form(required_fields=["username", "password"])
        def your_route():
            ...

    Returns:
        Function: The wrapped function with form validation.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if request.method == 'POST':
                # Check if required_fields is provided and has values
                if required_fields:
                    missing_fields = [
                        field for field in required_fields if not request.form.get(field)]

                    if missing_fields:
                        message = f"Missing required fields: {', '.join(missing_fields)}"
                        flash_message(message, "error")
                        return redirect(request.referrer)  # Redirect back to the form

            return func(*args, **kwargs)

        return wrapper

    return decorator


def validate_user(data_manager):
    """
    A decorator to validate if a user exists based on the provided user_id.

    If the user does not exist, renders a 404 error page.

    Args:
        data_manager (object): An object with a `get_user_by_id` method to retrieve users.

    Usage:
        @validate_user(data_manager)
        def your_route(user_id):
            ...

    Returns:
        Function: The wrapped function with user validation.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(user_id, *args, **kwargs):
            user = data_manager.get_user_by_id(user_id)
            if not user:
                return render_error_page(404, f"User with ID {user_id} not found.")
            return func(user_id, *args, **kwargs)
        return wrapper
    return decorator
