"""
This module defines API routes for interacting with user and movie data.

The API routes are registered as a Flask Blueprint and support operations
like retrieving users, managing user-specific movie collections, and deleting users.

Functions:
    create_api(data_manager): Creates and returns a Flask Blueprint with API routes.
"""

from flask import Blueprint, request
from helpers.api_helpers import create_success_response, create_error_response
from decorators.api_decorators import handle_api_errors, validate_json


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
    @handle_api_errors()
    def get_users():
        """
        Retrieves all users from the database.

        Returns:
            Response: JSON response containing a list of all users or an error message.
        """
        users = data_manager.get_all_users()
        return create_success_response(
            data=[user.to_dict(include_relationships=False) for user in users]), 200

    @api.route('/users/<int:user_id>', methods=['GET'])
    @handle_api_errors()
    def get_user(user_id):
        """
        Retrieves a specific user by their ID.

        Args:
            user_id (int): ID of the user to retrieve.

        Returns:
            Response: JSON response containing the user data or an error message.
        """
        if not (user := data_manager.get_user_by_id(user_id)):
            return create_error_response(
                message=f'User with ID {user_id} not found'), 404
        return create_success_response(data=user.to_dict()), 200

    @api.route('/users', methods=['POST'])
    @validate_json(required_keys=["name"])
    @handle_api_errors()
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

        data = request.get_json()

        if 'error' in (result := data_manager.add_user(data["name"])):
            return create_error_response(message=result['error']), 400
        return create_success_response(message=result["success"]), 201

    @api.route('/users/<int:user_id>', methods=['DELETE'])
    @handle_api_errors()
    def delete_user(user_id):
        """
        Deletes a user and their associated movies.

        Args:
            user_id (int): ID of the user to delete.

        Returns:
            Response: JSON response with success or error message.
        """

        if 'error' in (result := data_manager.delete_user(user_id)):
            return create_error_response(message=result["error"]), 404
        return create_success_response(message=result["success"]), 200

    @api.route('/users/<int:user_id>/movies', methods=['GET'])
    @handle_api_errors()
    def get_user_movies(user_id):
        """
        Retrieves all movies associated with a specific user.

        Args:
            user_id (int): ID of the user whose movies are to be fetched.

        Returns:
            Response: JSON response containing a list of user movies or an error message.
        """

        if not (movies := data_manager.get_user_movies(user_id)):
            return create_error_response(
                message=f'No movies found for user with ID {user_id}'), 404
        return create_success_response(data=movies), 200

    @api.route('/users/<int:user_id>/movies', methods=['POST'])
    @validate_json(required_keys=["movie_name"])
    @handle_api_errors()
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

        data = request.get_json()

        if 'error' in (result := data_manager.add_movie(user_id, data["movie_name"])):
            return create_error_response(
                message=result['error']), 400
        return create_success_response(message=result['success']), 201

    @api.route('/users/movies/<int:user_movie_id>', methods=['PATCH'])
    @validate_json()
    @handle_api_errors()
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

        data = request.get_json()

        if 'error' in (result := data_manager.update_movie(user_movie_id, data)):
            return create_error_response(message=result['error']), 400
        return create_success_response(message=result['success']), 200

    @api.route('/users/movies/<int:user_movie_id>', methods=['DELETE'])
    @handle_api_errors()
    def delete_user_movie(user_movie_id):
        """
        Deletes a specific movie from a user's collection.

        Args:
            user_movie_id (int): ID of the UserMovies record to delete.

        Returns:
            Response: JSON response with success or error message.
        """

        if 'error' in (result := data_manager.delete_movie(user_movie_id)):
            return create_error_response(message=result['error']), 404
        return create_success_response(message=result['success']), 200

    return api
