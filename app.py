import os
from datetime import datetime
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
    recent_movies = data_manager.get_recent_movies()
    year = datetime.now().year
    return render_template('home.html', featured_movies=recent_movies, current_year=year)


@app.route('/users')
def list_users():
    """
    Fetches all users and renders the users list page.
    """
    users = data_manager.get_all_users()
    return render_template('users.html', users=users)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
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
    If the user is not found, an error page is shown.

    :param user_id: ID of the user whose movies are to be displayed.
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
    Route to delete a user.
    Deletes the user with the given ID and redirects to the users list page.
    """
    result = data_manager.delete_user(user_id)

    if 'error' in result:
        return render_template("error.html", error_message=result["error"]), 404
    else:
        flash(result['success'], 'success')

    return redirect(url_for('list_users'))


@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
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
    Route to update user-specific details for a movie.

    - GET: Display a form pre-filled with the current user-movie details.
    - POST: Update the user-specific movie details.

    :param user_id: ID of the user
    :param user_movie_id: ID of the UserMovies record to update.
    :return: Rendered template for GET, or a redirect/flash message for POST.
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
    Route to delete a user-specific movie entry.

    - Deletes the association of the movie with the specific user from the `UserMovies` table.
    - If no other users are associated with the movie, it deletes the movie itself from the `Movies` table.

    :param user_id:
    :param user_movie_id: ID of the `UserMovies` record to delete.
    :return: Redirects to the user's movie list page on success, or renders an error template on failure.
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
