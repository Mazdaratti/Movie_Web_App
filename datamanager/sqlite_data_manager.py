"""
This module provides the implementation of the DataManagerInterface using SQLite as the database.
It contains methods to manage users and their movie collections, including operations for adding,
deleting, and updating users and movies, as well as retrieving user movie data.

Classes:
    SQLiteDataManager (DataManagerInterface):
                      A class that handles user and movie data in an SQLite database.
"""
from sqlalchemy.exc import IntegrityError
from datamanager.data_manager import DataManagerInterface
from datamanager.models import db, User, Movie, UserMovies
from datamanager.movie_fetcher import MovieInfoDownloader, APIError
from decorators.db_decorators import transactional


class SQLiteDataManager(DataManagerInterface):
    """
    A class that implements the DataManagerInterface using SQLite as the database.
    This class provides methods for managing users and their movie collections.
    """

    def __init__(self, app):
        """
        Initializes the SQLiteDataManager with a Flask app instance and configures the database.

        Args:
            app: Flask app instance with SQLAlchemy configuration.
        """
        db.init_app(app)  # Initialize SQLAlchemy with Flask app
        self.db = db  # Store the db object for use in methods

    def get_all_users(self):
        """
        Retrieves all users from the database.

        Returns:
            list: A list of all users.
        """
        return User.query.all()

    def get_user_by_id(self, user_id):
        """
        Fetches a user by their ID from the database.

        Args:
            user_id (int): ID of the user to fetch.

        Returns:
            User or None: User object if found, else None.
        """
        return User.query.get(user_id)

    @transactional(db.session)
    def add_user(self, user_name):
        """
        Adds a new user to the database if the user does not already exist.

        Args:
            user_name (str): The name of the user to be added.

        Returns:
            dict: A dictionary containing a success or error message.
        """
        if User.query.filter_by(name=user_name).first():
            return {"error": f"User with the name '{user_name}' already exists."}

        new_user = User(name=user_name)
        self.db.session.add(new_user)

        return {"success": f"User '{user_name}' was successfully added."}

    @transactional(db.session)
    def delete_user(self, user_id):
        """
        Deletes a user and their associated movies from the database.
        If a movie is associated only with this user, it is also deleted from the database.
        Args:
            user_id (int): ID of the user to be deleted.

        Returns:
            dict: A dictionary with a success or error message.
        """

        if not (user := self.get_user_by_id(user_id)):
            return {"error": f"User with ID {user_id} not found"}

        # Delete the user (this will trigger cascading deletions for associated user_movies)
        self.db.session.delete(user)

        # Check and delete movies with no remaining associations
        movies_with_no_associations = (
            Movie.query
            .outerjoin(UserMovies, UserMovies.movie_id == Movie.id)
            .filter(UserMovies.id == None)
            .all()
        )

        for movie in movies_with_no_associations:
            self.db.session.delete(movie)

        return {"success": f"User with ID {user_id} "
                           f"and all associated data have been deleted successfully"}

    def get_user_movie(self, user_movie_id):
        """
        Fetches a UserMovies object by its unique ID.

        Args:
            user_movie_id (int): The ID of the UserMovies record to fetch.

        Returns:
            UserMovies or None: UserMovies object if found, else None.
        """
        try:
            return UserMovies.query.get(user_movie_id)
        except Exception as e:
            self.db.session.rollback()
            print(f"Error fetching movie by ID: {e}")
            return None

    def get_user_movies(self, user_id):
        """
        Retrieves all movies associated with a specific user,
        including user-specific overrides.

        Args:
            user_id (int): ID of the user whose movies are to be fetched.

        Returns:
            list: A list of dictionaries containing movie data
                  with user-specific values where applicable.
        """
        try:
            user_movies = (
                db.session.query(UserMovies)
                .join(Movie)
                .filter(UserMovies.user_id == user_id)
                .all()
            )

            return [
                {**user_movie.movie.to_dict(), **user_movie.to_dict()}
                for user_movie in user_movies
            ]
        except Exception as e:
            self.db.session.rollback()
            print(f"Error fetching user movies: {str(e)}")
            return []

    @staticmethod
    def is_movie_in_user_list(user_id, user_movie_id):
        """
        Checks if a specific movie is in the user's collection.

        Args:
            user_id (int): The ID of the user.
            user_movie_id (int): The ID of the UserMovies record.

        Returns:
            bool: True if the movie is in the user's collection, False otherwise.
        """
        return UserMovies.query.filter_by(user_id=user_id, id=user_movie_id).first()

    def get_movie_by_id(self, movie_id):
        """
        Fetches a movie by its ID from the database.

        Args:
            movie_id (int): ID of the movie to fetch.

        Returns:
            Movie or None: Movie object if found, else None.
        """
        try:
            return Movie.query.get(movie_id)
        except Exception as e:
            self.db.session.rollback()
            print(f"Error fetching movie by ID: {str(e)}")
            return None

    @staticmethod
    def get_recent_movies():
        """
        Retrieves the most recent movies from the database.

        Returns:
            list: A list of the most recent 8 movies.
        """
        return Movie.query.order_by(Movie.id.desc()).limit(8).all()

    @transactional(db.session)
    def add_movie(self, user_id, movie_name):
        """
        Adds a movie to a specific user's collection.
        If the movie doesn't exist, fetches it from OMDb.

        Args:
            user_id (int): The ID of the user adding the movie.
            movie_name (str): The name of the movie to be added.

        Returns:
            dict: A dictionary containing a success or error message.
        """
        # Check if the user exists
        if not self.get_user_by_id(user_id):
            return {"error": f"User with ID {user_id} not found."}

        # Check if the movie already exists (case-insensitive)
        movie = Movie.query.filter(Movie.name.ilike(movie_name)).first()

        # Check if the movie is already in the user's collection
        if movie and UserMovies.query.filter_by(user_id=user_id, movie_id=movie.id).first():
            return {"error": f"You already have the movie '{movie_name}' in your list!"}

        # Add new movie if not already in database
        if not movie:
            movie_data = MovieInfoDownloader().fetch_movie_data(movie_name)
            movie = Movie(**movie_data)
            self.db.session.add(movie)
            self.db.session.commit()

        # Associate movie with the user
        self.db.session.add(UserMovies(
            user_id=user_id,
            movie_id=movie.id,
            user_title=movie.name
            ))
        return {"success": f"Movie '{movie_name}' was successfully "
                           f"added to your list!"}

    @transactional(db.session)
    def update_movie(self, user_movie_id, updated_details):
        """
        Updates the user-specific details of a movie in the UserMovies table.

        Args:
            user_movie_id (int): The ID of the UserMovies record to update.
            updated_details (dict): A dictionary of updated user-specific details.

        Returns:
            dict: A dictionary with success or error message.
        """
        if not (user_movie := self.get_user_movie(user_movie_id)):
            return {"error": "This movie is not in your list."}

        for key, value in updated_details.items():
            if hasattr(user_movie, key):
                setattr(user_movie, key, value)
            else:
                return {"error": f"Invalid attribute '{key}' for movie details."}

        return {"success": f"Movie '{user_movie.movie.name}' has been successfully updated."}

    @transactional(db.session)
    def delete_movie(self, user_movie_id):
        """
        Deletes a user-specific movie record and its associated data from the database.

        Args:
            user_movie_id (int): The ID of the UserMovies record to delete.

        Returns:
            dict: A dictionary with success or error message.
        """
        if not (user_movie := self.get_user_movie(user_movie_id)):
            return {"error": "This movie is not in your list."}

        movie = user_movie.movie

        self.db.session.delete(user_movie)

        if not UserMovies.query.filter_by(movie_id=movie.id).first():
            self.db.session.delete(movie)

        return {
            "success": f"Movie '{movie.name}' has been successfully removed from your list."
        }
