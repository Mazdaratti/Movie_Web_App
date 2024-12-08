"""
Main module for initializing and running the Flask application.

This module sets up the Flask app, including configuration, routes,
blueprints, and error handlers. It uses an SQLite database for storage
and follows a modular structure with separate concerns for routes,
data management, and storage.
"""
import os
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
