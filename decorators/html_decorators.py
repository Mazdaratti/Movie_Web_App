from functools import wraps
from flask import render_template
from helpers.logger import logger


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
