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


@app.route('/')
def home():
    """
    Displays the home page with recent movies.

    Fetches a list of recently added movies from the database and displays it on the home page.

    Returns:
        dict: A dictionary containing the rendered home page template with recent movies and the current year.
    """
    recent_movies = data_manager.get_recent_movies()
    return render_template('home.html', featured_movies=recent_movies)


@app.route('/users')
def list_users():
    """
    Fetches all users and renders the users list page.

    Retrieves all user data from the database and renders it on the 'users' page.

    Returns:
        dict: A dictionary containing the rendered users list page with all users.
    """
    users = data_manager.get_all_users()
    return render_template('users.html', users=users)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """
    Allows the addition of a new user.

    - GET: Displays the form to add a new user.
    - POST: Submits the form and adds the user to the database.

    Returns:
        dict: A dictionary containing the redirected response to the add user page with a success or error message.
    """
    if request.method == 'POST':
        user_name = request.form['name']
        result = data_manager.add_user(user_name)

        if 'error' in result:
            flash(result['error'], 'error')  # Flash error message
        else:
            flash(result['success'], 'success')  # Flash success message

        return redirect(url_for('add_user'))  # Redirect to the same page to display the message

    return render_template('add_user.html')


@app.route('/users/<int:user_id>')
def user_movies(user_id):
    """
    Displays the list of movies for a specific user.

    Fetches and displays the movie collection for the specified user. If the user is not found, shows an error.

    Args:
        user_id (int): The ID of the user whose movies are to be displayed.

    Returns:
        dict: A dictionary containing the rendered template with the user's movie collection or an error message.
    """
    user = data_manager.get_user_by_id(user_id)

    if not user:
        return render_template('error.html',
                               error_message=f"User with ID {user_id} not found."), 404

    try:
        movies = data_manager.get_user_movies(user_id)
        return render_template('user_movies.html', user=user, movies=movies)

    except Exception as e:
        return render_template('error.html', error_message=f"An error occurred: {str(e)}"), 500


@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    """
    Deletes a user from the database.

    Deletes the user identified by user_id from the database and redirects to the user list page.

    Args:
        user_id (int): The ID of the user to be deleted.

    Returns:
        dict: A dictionary containing the success or error message and the redirection to the user list page.
    """
    result = data_manager.delete_user(user_id)

    if 'error' in result:
        return render_template("error.html", error_message=result["error"]), 404
    else:
        flash(result['success'], 'success')

    return redirect(url_for('list_users'))


@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    """
    Adds a movie to a user's collection.

    - GET: Displays the form to add a movie to the specified user's collection.
    - POST: Adds the movie to the user's collection and flashes a success or error message.

    Args:
        user_id (int): The ID of the user to whom the movie will be added.

    Returns:
        dict: A dictionary containing the redirected response to the add movie page with success or error message.
    """
    if request.method == 'POST':
        movie_name = request.form.get('movie_name')

        if not movie_name:
            flash("Movie name is required!", "error")
            return redirect(url_for('add_movie', user_id=user_id))

        try:
            result = data_manager.add_movie(user_id, movie_name)

            if 'error' in result:
                flash(result['error'], 'error')
            else:
                flash(result['success'], 'success')
        except KeyError as e:
            flash(f"Missing data: {str(e)}", "error")
            return render_template('error.html', error_message="Invalid data submitted.")
        except Exception as e:
            app.logger.error(f"Error in add_movie route: {e}")
            return render_template('500.html'), 500

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
        dict: A dictionary containing the redirected response to the user's movie list with success or error message.
    """
    try:
        user_movie = data_manager.get_user_movie(user_movie_id)

        if not user_movie:
            return render_template('error.html', error_message="User-movie record not found."), 404

        if request.method == 'POST':
            updated_details = request.form.to_dict()

            # Check if `user_rating` is empty or not provided, set it to None
            user_rating = updated_details.get('user_rating')
            updated_details['user_rating'] = user_rating if user_rating else None

            result = data_manager.update_movie(user_movie_id, updated_details)

            if "success" in result:
                flash(result["success"], "success")
                return redirect(url_for('user_movies', user_id=user_id))
            else:
                flash(result["error"], "error")

        return render_template('update_movie.html', user_movie=user_movie)

    except KeyError as e:
        flash(f"Invalid form data: {str(e)}", "error")
        return render_template('error.html', error_message="Invalid data submitted.")
    except Exception as e:
        app.logger.error(f"Error in update_movie route: {e}")
        return render_template('505.html'), 505


@app.route('/users/<int:user_id>/delete_movie/<int:user_movie_id>', methods=['POST'])
def delete_movie(user_id, user_movie_id):
    """
    Deletes a specific movie from a user's collection.

    If no other users are associated with the movie, it is deleted from the `Movies` table as well.

    Args:
        user_id (int): The ID of the user whose movie is being deleted.
        user_movie_id (int): The ID of the movie to delete from the user's collection.

    Returns:
        dict: A dictionary containing a success or error message and redirection to the user's movie list page.
    """
    try:
        result = data_manager.delete_movie(user_movie_id)

        if "success" in result:
            flash(result['success'], "success")
            return redirect(url_for('user_movies', user_id=user_id))
        else:
            flash(result['error'], "error")
            return render_template('error.html', error_message=result['error'])

    except Exception as e:
        app.logger.error(f"Error in delete_movie route: {e}")
        return render_template('500.html'), 500


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
