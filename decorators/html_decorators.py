from functools import wraps
from flask import flash, render_template, redirect, request
from helpers.logger import logger
from helpers.html_helpers import flash_message, render_error_page


def handle_errors():
    """
    A decorator to handle exceptions for HTML routes and render appropriate error pages.

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
        required_fields (list): List of required fields for the form.

    Returns:
        Function: The wrapped function with form validation.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if request.method == 'POST':
                # Check if required_fields is provided and has values
                if required_fields:
                    missing_fields = [field for field in required_fields if not request.form.get(field)]

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

    If the user does not exist, returns a 404 error page.
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
