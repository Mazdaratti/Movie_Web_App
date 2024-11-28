import os
from flask import Flask, render_template, redirect, flash, request, url_for
from datamanager.sqlite_data_manager import SQLiteDataManager
from storage import PATH
from datamanager.models import db

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Set up SQLite database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the SQLiteDataManager
data_manager = SQLiteDataManager(app)


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
    user = data_manager.get_user_by_id(user_id)  # Fetch the user by ID

    if not user:
        return render_template('error.html',
                               error_message=f"User with ID {user_id} not found.")

    movies = data_manager.get_user_movies(user_id)  # Fetch the user's movies
    return render_template('user_movies.html', user=user, movies=movies)


@app.route('/users/<int:user_id>/update_movie/<int:movie_id>')
def update_movie(user_id, movie_id):
    """
    Temporary route to avoid errors, redirecting or displaying a dummy message.
    """
    return f"Update movie {movie_id} for user {user_id} (this is a placeholder route)."


@app.route('/users/<int:user_id>/delete_movie/<int:movie_id>')
def delete_movie(user_id, movie_id):
    """
    Temporary route to avoid errors, redirecting or displaying a dummy message.
    """
    return f"Delete movie {movie_id} for user {user_id} (this is a placeholder route)."


@app.route('/users/<int:user_id>/add_movie')
def add_movie(user_id):
    """
    Temporary route to avoid errors, redirecting or displaying a dummy message.
    """
    return f"Add movie for user {user_id} (this is a placeholder route)."


if __name__ == "__main__":
    app.run(debug=True)
