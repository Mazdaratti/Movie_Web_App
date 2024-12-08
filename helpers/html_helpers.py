"""
This module defines helper functions for common operations in the Flask app.
These functions help with flashing messages and rendering error pages.
"""


from flask import render_template, flash


def flash_message(message, category="info"):
    """Flash a message with a given category."""
    flash(message, category)


def render_error_page(status_code, message):
    """Render a standardized error page."""
    return render_template(
        "error.html", error_message=message, status_code=status_code), status_code
