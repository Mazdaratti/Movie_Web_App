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
        flash(f"User with ID {user_id} not found.", "error")
        return redirect(url_for('list_users'))

    movies = data_manager.get_user_movies(user_id)  # Fetch the user's movies
    return render_template('user_movies.html', user=user, movies=movies)


@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    """
    Route to delete a user.
    Deletes the user with the given ID and redirects to the users list page.
    """
    result = data_manager.delete_user(user_id)

    if 'error' in result:
        flash(result['error'], 'error')
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

        except Exception as e:
            flash(f"An error occurred while adding the movie: {str(e)}", "error")
            return redirect(url_for('add_movie', user_id=user_id))

    return render_template('add_movie.html', user_id=user_id)


@app.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    """
    Route to update a movie's details.

    - GET: Display a form pre-filled with the current movie details.
    - POST: Update the movie details based on submitted form data.

    :param user_id: ID of the user who owns the movie.
    :param movie_id: ID of the movie to be updated.
    :return: Rendered template for GET, or a redirect/flash message for POST.
    """
    movie = data_manager.get_movie_by_id(movie_id)

    if not movie:
        flash(f"Movie with ID {movie_id} not found.", "error")
        return redirect(url_for('user_movies', user_id=user_id))
    if request.method == 'POST':
        updated_details = request.form.to_dict()

        result = data_manager.update_movie(movie_id, updated_details)
        if "success" in result:
            flash(result['success'], "success")
            return redirect(url_for('user_movies', user_id=user_id))
        else:
            flash(result['error'], "error")

    return render_template('update_movie.html', user_id=user_id, movie=movie)


@app.route('/users/<int:user_id>/delete_movie/<int:movie_id>')
def delete_movie(user_id, movie_id):
    """
    Temporary route to avoid errors, redirecting or displaying a dummy message.
    """
    return f"Delete movie {movie_id} for user {user_id} (this is a placeholder route)."


if __name__ == "__main__":
    app.run(debug=True)
