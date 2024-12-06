"""
This module defines API routes for interacting with user and movie data.

The API routes are registered as a Flask Blueprint and support operations
like retrieving users, managing user-specific movie collections, and deleting users.

Functions:
    create_api(data_manager): Creates and returns a Flask Blueprint with API routes.
"""

from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest
from helpers.api_helpers import create_response
from helpers.logger import logger

def create_api(data_manager):
    """
    Creates a Flask Blueprint for API routes to manage users and movies.

    Args:
        data_manager: An instance of the data manager that provides database interaction methods.

    Returns:
        Blueprint: A Flask Blueprint with the registered API routes.
    """
    api = Blueprint('api', __name__)

    @api.route('/users', methods=['GET'])
    def get_users():
        """
        Retrieves all users from the database.

        Returns:
            Response: JSON response containing a list of all users or an error message.
        """
        try:
            users = data_manager.get_all_users()
            return create_response("success", data=[user.to_dict() for user in users])
        except Exception as e:
            logger.error(f"Error in get_users: {str(e)}")
            return create_response("error", message=str(e)), 500

    @api.route('/users/<int:user_id>', methods=['GET'])
    def get_user(user_id):
        """
        Retrieves a specific user by their ID.

        Args:
            user_id (int): ID of the user to retrieve.

        Returns:
            Response: JSON response containing the user data or an error message.
        """
        try:
            user = data_manager.get_user_by_id(user_id)
            if not user:
                return create_response(
                    "error", message=f'User with ID {user_id} not found'), 404
            return jsonify(user.to_dict()), 200
        except Exception as e:
            logger.error(f"Error in get_user with ID {user_id}: {str(e)}")
            return create_response("error", message=str(e)), 500

    @api.route('/users', methods=['POST'])
    def add_user():
        """
        Adds a new user to the database.

        Request Body (JSON):
            {
                "name": "User Name"
            }

        Returns:
            Response: JSON response with success or error message.
        """
        try:
            data = request.get_json()
            user_name = data.get('name')
            if not user_name:
                return create_response(
                    "error", message="User name is required"), 400
            result = data_manager.add_user(user_name)
            if 'error' in result:
                return create_response("error", message=result['error']), 400
            return create_response("success", message=result['success']), 201
        except BadRequest as e:
            logger.error(f"BadRequest in add_user: {str(e)}")
            return create_response("error", message="Invalid JSON format"), 400
        except Exception as e:
            logger.error(f"Error in add_user: {str(e)}")
            return create_response("error", message=str(e)), 500

    @api.route('/users/<int:user_id>', methods=['DELETE'])
    def delete_user(user_id):
        """
        Deletes a user and their associated movies.

        Args:
            user_id (int): ID of the user to delete.

        Returns:
            Response: JSON response with success or error message.
        """
        try:
            result = data_manager.delete_user(user_id)
            if 'error' in result:
                return create_response("error", message=result["error"]), 404
            return create_response("success", message=result["success"])
        except Exception as e:
            logger.error(f"Error in delete_user with ID {user_id}: {str(e)}")
            return create_response("error", message=str(e)), 500

    @api.route('/users/<int:user_id>/movies', methods=['GET'])
    def get_user_movies(user_id):
        """
        Retrieves all movies associated with a specific user.

        Args:
            user_id (int): ID of the user whose movies are to be fetched.

        Returns:
            Response: JSON response containing a list of user movies or an error message.
        """
        try:
            movies = data_manager.get_user_movies(user_id)
            if not movies:
                return create_response(
                    "error", message=f'No movies found for user with ID {user_id}'), 404
            return create_response("success", data=movies)
        except Exception as e:
            logger.error(
                f"Error in get_user_movies for user with ID {user_id}: {str(e)}")
            return create_response("error", message=str(e)), 500

    @api.route('/users/<int:user_id>/movies', methods=['POST'])
    def add_movie_to_user(user_id):
        """
        Adds a movie to a specific user's collection.

        Request Body (JSON):
            {
                "movie_name": "Movie Name"
            }

        Args:
            user_id (int): ID of the user adding the movie.

        Returns:
            Response: JSON response with success or error message.
        """
        try:
            data = request.get_json()
            movie_name = data.get('movie_name')
            if not movie_name:
                return create_response(
                    "error", message="Movie name is required"), 400
            result = data_manager.add_movie(user_id, movie_name)
            if 'error' in result:
                return create_response(
                    "error", message=result['error']), 400
            return create_response("success", message=result['success']), 201
        except BadRequest:
            logger.error(
                "BadRequest in add_movie_to_user: Invalid JSON format")
            return create_response("error", message="Invalid JSON format"), 400
        except Exception as e:
            logger.error(
                f"Error in add_movie_to_user for user with ID {user_id}: {str(e)}")
            return create_response("error", message=str(e)), 500

    @api.route('/users/movies/<int:user_movie_id>', methods=['PATCH'])
    def update_user_movie(user_movie_id):
        """
        Updates user-specific details for a movie in the UserMovies collection.

        Request Body (JSON):
            {
                "user_title": "New Title",
                "user_rating": 9,
                "user_notes": "Some notes"
            }

        Args:
            user_movie_id (int): ID of the UserMovies record to update.

        Returns:
            Response: JSON response with success or error message.
        """
        try:
            data = request.get_json()
            result = data_manager.update_movie(user_movie_id, data)
            if 'error' in result:
                return create_response("error", message=result['error']), 400
            return create_response("success", message=result['success'])
        except BadRequest:
            logger.error(
                f"BadRequest in update_user_movie with ID {user_movie_id}: Invalid JSON format")
            return create_response("error", message="Invalid JSON format"), 400
        except Exception as e:
            logger.error(
                f"Error in update_user_movie with ID {user_movie_id}: {str(e)}")
            return create_response("error", message=str(e)), 500

    @api.route('/users/movies/<int:user_movie_id>', methods=['DELETE'])
    def delete_user_movie(user_movie_id):
        """
        Deletes a specific movie from a user's collection.

        Args:
            user_movie_id (int): ID of the UserMovies record to delete.

        Returns:
            Response: JSON response with success or error message.
        """
        try:
            result = data_manager.delete_movie(user_movie_id)
            if 'error' in result:
                return create_response("error", message=result['error']), 404
            return create_response("success", message=result['success'])
        except Exception as e:
            logger.error(
                f"Error in delete_user_movie with ID {user_movie_id}: {str(e)}")
            return create_response("error", message=str(e)), 500

    return api

