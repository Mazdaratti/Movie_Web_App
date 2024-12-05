"""
This module sets up the Flask web application for managing users and their movie collections.
It provides routes for displaying users, adding and deleting users, adding and updating movies
to user collections, and handling errors. The application uses SQLite as the database,
with all necessary operations being handled by the SQLiteDataManager.

Routes:
    - /: Home page that displays recent movies.
    - /users: Displays a list of all users.
    - /add_user: Page for adding a new user.
    - /users/<int:user_id>: Displays a user's movie collection.
    - /delete_user/<int:user_id>: Deletes a user.
    - /users/<int:user_id>/add_movie: Adds a movie to a user's collection.
    - /users/<int:user_id>/update_movie/<int:user_movie_id>: Updates user-specific movie details.
    - /users/<int:user_id>/delete_movie/<int:user_movie_id>: Deletes a movie from a user's collection.
    - Error Handlers: Custom 404 and 500 error pages.

Configuration:
    - SQLite database URI defined in the app's config.
    - Log errors to a rotating log file ('app.log').

Logging:
    - Error logs are saved to a rotating file 'app.log' with a max size of 10KB and 1 backup.
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, redirect, flash, request, url_for
from datamanager.sqlite_data_manager import SQLiteDataManager
from storage import PATH

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Set up SQLite database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the SQLiteDataManager
data_manager = SQLiteDataManager(app)

# Configure logging
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.ERROR)
app.logger.addHandler(handler)


def flash_message(message, category="info"):
    """Flash a message with a given category."""
    flash(message, category)


def render_error_page(status_code, message):
    """Render a standardized error page."""
    return render_template(
        "error.html", error_message=message, status_code=status_code), status_code


@app.route('/')
def home():
    """
    Render the home page with a list of featured movies.

    This route retrieves a list of recently added movies from the database
    and displays them as featured content on the home page. In case of an error
    during data retrieval, an error page is rendered.

    Returns:
        Response: The rendered HTML template for the home page, including the
        list of featured movies, or an error page if a server issue occurs.
    """
    try:
        recent_movies = data_manager.get_recent_movies()
        return render_template('home.html', featured_movies=recent_movies)
    except Exception as e:
        app.logger.error(f"Error in home route: {e}")
        return render_error_page(500, "Failed to load recent movies.")


@app.route('/users')
def list_users():
    """
    Render the users list page with all registered users.

    This route retrieves a list of all users from the database and displays them
    on the users list page. If an error occurs during data retrieval, an error
    page is rendered instead.

    Returns:
        Response: The rendered HTML template for the users list page, including
        all user data, or an error page if a server issue occurs.
    """
    try:
        users = data_manager.get_all_users()
        return render_template('users.html', users=users)
    except Exception as e:
        app.logger.error(f"Error in list_users route: {e}")
        return render_error_page(500, "Failed to load users.")


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """
    Handles the creation of a new user.

    - GET: Displays the form to add a new user.
    - POST: Processes the submitted form data and adds the user to the database.
            If successful, redirects with a success message.
            If unsuccessful, displays an error message.

    Args:
        None

    Returns:
        On success (POST): Redirects to the list user page with a success message.
        On failure (POST): Redirects to the same page with an error message.
        On GET: Renders the add user form template.
    """
    try:
        if request.method == 'POST':
            user_name = request.form['name']

            if not user_name:
                flash_message("User name is required.", 'error')
                return redirect(url_for('add_user'))  # Redirect to the same page with the error

            result = data_manager.add_user(user_name)

            if 'error' in result:
                flash_message(result['error'], 'error')
            else:
                flash_message(result['success'], 'success')

            return redirect(url_for('list_users'))

        return render_template('add_user.html')

    except Exception as e:
        app.logger.error(f"Unexpected error in add_user: {str(e)}")
        return render_error_page(500, "Failed to add user due to an unexpected error.")


@app.route('/users/<int:user_id>')
def user_movies(user_id):
    """
    Displays the movie collection for a specific user.

    Retrieves and displays the list of movies associated with the specified user.
    If the user does not exist, an error page is shown. If there is an issue fetching
    the user's movie collection, an internal server error page is displayed.

    Args:
        user_id (int): The unique identifier of the user whose movie collection is to be displayed.

    Returns:
        On success: The rendered template (`user_movies.html`) with the user's details and movie collection.
        On failure: An error page with an appropriate status code (404 if the user is not found, 500 for internal errors).
    """
    try:
        user = data_manager.get_user_by_id(user_id)
        if not user:
            return render_error_page(404, f"User with ID {user_id} not found.")

        movies = data_manager.get_user_movies(user_id)
        return render_template('user_movies.html', user=user, movies=movies)
    except Exception as e:
        app.logger.error(f"Error in user_movies route: {e}")
        return render_error_page(500, "Failed to load user movies.")


@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    """
    Deletes a user from the database.

    Deletes the user identified by user_id from the database and redirects to the user list page.

    Args:
        user_id (int): The ID of the user to be deleted.

    Returns:
        On success: Redirects to the users list page with a success message.
        On failure: Renders an error page with the appropriate message.
    """
    try:
        result = data_manager.delete_user(user_id)

        if "error" in result:
            app.logger.error(f"Error in delete_user: {result['error']}")
            return render_error_page(404, result["error"])

        flash_message(result["success"], "success")
        return redirect(url_for('list_users'))

    except Exception as e:
        app.logger.error(f"Unexpected error in delete_user route: {e}")
        return render_error_page(500, "An unexpected error occurred while deleting the user.")


@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    """
    Adds a movie to a user's collection.

    - GET: Displays the form to add a movie to the specified user's collection.
    - POST: Validates input and attempts to add the movie to the user's collection.
            Provides appropriate feedback (success or error messages).

    Args:
        user_id (int): The ID of the user to whom the movie will be added.

    Returns:
        On success (POST): Redirects to the user's movie collection with a success message.
        On error (POST): Redirects back to the add movie form with an error message.
        On GET: Renders the add movie form.
    """
    user = data_manager.get_user_by_id(user_id)
    if not user:
        return render_error_page(404, "User not found.")

    if request.method == 'POST':
        movie_name = request.form.get('movie_name')

        if not movie_name:
            flash_message("Movie name is required.", "error")
            return redirect(url_for('add_movie', user_id=user_id))

        try:
            result = data_manager.add_movie(user_id, movie_name)

            if 'error' in result:
                flash_message(result['error'], 'error')
            else:
                flash_message(result['success'], 'success')
        except KeyError as e:
            flash_message(f"Missing data: {str(e)}", "error")
            app.logger.error(f"KeyError in add_movie route: {e}")
            return redirect(url_for('add_movie', user_id=user_id))
        except Exception as e:
            app.logger.error(f"Error in add_movie route: {e}")
            return render_error_page(500, "Failed to add movie.")

    return render_template('add_movie.html', user_id=user_id)


@app.route('/users/<int:user_id>/update_movie/<int:user_movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, user_movie_id):
    """
    Updates details for a specific movie in a user's collection.

    - GET: Displays a form pre-filled with current movie details.
    - POST: Submits the form to update the movie's details.

    Args:
        user_id (int): The ID of the user whose movie is being updated.
        user_movie_id (int): The ID of the movie to update.

    Returns:
        On success: Redirect to the user's movie list with a success message.
        On error: Render the error page or redirect with an error message.
    """
    try:
        user_movie = data_manager.get_user_movie(user_movie_id)
        if not user_movie:
            return render_error_page(404, "Movie not found.")

        user = data_manager.get_user_by_id(user_id)
        if not user:
            return render_error_page(404, "User not found.")

        if request.method == 'POST':
            updated_details = request.form.to_dict()

            # Check if `user_rating` is empty or not provided, set it to None
            user_rating = updated_details.get('user_rating')
            updated_details['user_rating'] = user_rating if user_rating else None

            result = data_manager.update_movie(user_movie_id, updated_details)

            if "success" in result:
                flash_message(result["success"], "success")
                return redirect(url_for('user_movies', user_id=user_id))
            else:
                flash_message(result["error"], "error")

        return render_template('update_movie.html', user_movie=user_movie)

    except KeyError as e:
        flash(f"Invalid form data: {str(e)}", "error")
        return render_template('update_movie.html', user_movie=user_movie)
    except Exception as e:
        app.logger.error(f"Error in update_movie route: {e}")
        return render_error_page(500, "Failed to update movie.")


@app.route('/users/<int:user_id>/delete_movie/<int:user_movie_id>', methods=['POST'])
def delete_movie(user_id, user_movie_id):
    """
    Deletes a specific movie from a user's collection.

    If no other users are associated with the movie, it is deleted from the `Movies` table as well.

    Args:
        user_id (int): The ID of the user whose movie is being deleted.
        user_movie_id (int): The ID of the movie to delete from the user's collection.

    Returns:
        On success: Redirect to the user's movie list with a success message.
        On error: Render the error page with an error message.
    """
    try:
        result = data_manager.delete_movie(user_movie_id)

        if "success" in result:
            flash_message(result['success'], "success")
            return redirect(url_for('user_movies', user_id=user_id))
        else:
            flash_message(result['error'], "error")
            return render_error_page(500, result["error"])

    except Exception as e:
        app.logger.error(f"Error in delete_movie route: {e}")
        return render_error_page(500, "Failed to delete movie.")


@app.errorhandler(404)
def page_not_found(e):
    """
    Handles 404 Not Found errors.
    Renders a custom 404 error page.
    """
    return render_template('404.html', error_message="Page not found."), 404


@app.errorhandler(500)
def internal_server_error(e):
    """
    Handles 500 Internal Server Error.
    Renders a custom 500 error page.
    """
    app.logger.error(f"Server Error: {e}")
    return render_template('500.html', error_message="Something went wrong on our end."), 500


if __name__ == "__main__":
    app.run(debug=True)
