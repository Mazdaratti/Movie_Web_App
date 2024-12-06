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
from flask import Flask
from routes.html_routes import create_html_route
from routes.error_handlers import page_not_found, internal_server_error
from routes.api_routes import create_api
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

# Create and register the html_routes blueprint
html_routes = create_html_route(data_manager)
app.register_blueprint(html_routes, url_prefix='')

# Create and register the API Blueprint
api = create_api(data_manager)
app.register_blueprint(api, url_prefix='/api')

# Register error handlers
app.register_error_handler(404, page_not_found)
app.register_error_handler(500, internal_server_error)

if __name__ == "__main__":
    app.run(debug=True)
