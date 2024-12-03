"""
This module defines an abstract interface for managing data operations
in the MovieWeb App. The interface provides methods for handling users,
movies, and user-specific movie details. Implementations of this interface
must define all abstract methods to interact with the underlying data store.
"""

from abc import ABC, abstractmethod


class DataManagerInterface(ABC):
    """
    Abstract base class for data management in the MovieWeb App.

    Defines the required methods for managing users, movies, and their associations.
    """

    @abstractmethod
    def get_all_users(self):
        """
        Retrieve all users from the data store.

        :return: A list of user records.
        """
        pass

    @abstractmethod
    def get_user_by_id(self, user_id):
        """
        Retrieve a specific user by their ID.

        :param user_id: The ID of the user to retrieve.
        :return: A user record or None if not found.
        """
        pass

    @abstractmethod
    def get_user_movie(self, user_movie_id):
        """
        Retrieve a user-specific movie record by its ID.

        :param user_movie_id: The ID of the user-movie record to retrieve.
        :return: A user-movie record or None if not found.
        """
        pass

    @abstractmethod
    def get_user_movies(self, user_id):
        """
        Retrieve all movies associated with a specific user.

        :param user_id: The ID of the user.
        :return: A list of user-movie records.
        """
        pass

    @abstractmethod
    def add_user(self, user):
        """
        Add a new user to the data store.

        :param user: A dictionary or object containing user details.
        :return: The added user record or a success indicator.
        """
        pass

    @abstractmethod
    def delete_user(self, user_id):
        """
        Delete a user from the data store by their ID.

        :param user_id: The ID of the user to delete.
        :return: A success or error indicator.
        """
        pass

    def get_movie_by_id(self, movie_id):
        """
        Retrieve a movie by its ID.

        :param movie_id: The ID of the movie to retrieve.
        :return: A movie record or None if not found.
        """
        pass

    @abstractmethod
    def add_movie(self, user_id, movie_details):
        """
        Add a new movie associated with a specific user.

        :param user_id: The ID of the user adding the movie.
        :param movie_details: A dictionary or object containing movie details.
        :return: The added movie record or a success indicator.
        """
        pass

    @abstractmethod
    def delete_movie(self, user_movie_id):
        """
        Delete a user-specific movie record and its associated movie
        if no other users are linked to it.

        :param user_movie_id: The ID of the user-movie record to delete.
        :return: A success or error indicator.
        """
        pass

    @abstractmethod
    def update_movie(self, user_movie_id, updated_details):
        """
        Update user-specific details for a movie.

        :param user_movie_id: The ID of the user-movie record to update.
        :param updated_details: A dictionary containing the updated details.
        :return: A success or error indicator.
        """
        pass
