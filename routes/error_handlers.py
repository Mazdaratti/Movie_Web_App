"""
This module defines custom error handlers for the Flask application.

The error handlers provide custom error pages for specific HTTP errors like 404 and 500.

Error Handlers:
    - 404: Page Not Found error.
    - 500: Internal Server Error.
"""

from flask import render_template
from flask import current_app


def page_not_found(e):
    """
    Handles 404 Not Found errors.
    Renders a custom 404 error page.

    Args:
        e: The error object, passed automatically by Flask.

    Returns:
        Response: The rendered HTML template for the 404 error page.
    """
    current_app.logger.error(f"Page not found: {e}")
    return render_template('404.html', error_message="Page not found."), 404


def internal_server_error(e):
    """
    Handles 500 Internal Server Error.
    Renders a custom 500 error page and logs the error.

    Args:
        e: The error object, passed automatically by Flask.

    Returns:
        Response: The rendered HTML template for the 500 error page.
    """
    current_app.logger.error(f"Server Error: {e}")
    return render_template('500.html', error_message="Something went wrong on our end."), 500
