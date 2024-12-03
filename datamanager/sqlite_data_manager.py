"""
This module provides the implementation of the DataManagerInterface using SQLite as the database.
It contains methods to manage users and their movie collections, including operations for adding,
deleting, and updating users and movies, as well as retrieving user movie data.

Classes:
    SQLiteDataManager (DataManagerInterface): A class that handles user and movie data in an SQLite database.
"""
from datamanager.data_manager import DataManagerInterface
from datamanager.models import db, User, Movie, UserMovies
from datamanager.movie_fetcher import MovieInfoDownloader, APIError


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
        app.app_context().push()  # Ensure app context for SQLAlchemy
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

    def add_user(self, user_name):
        """
        Adds a new user to the database if the user does not already exist.

        Args:
            user_name (str): The name of the user to be added.

        Returns:
            dict: A dictionary containing a success or error message.
        """
        try:
            existing_user = User.query.filter_by(name=user_name).first()

            if existing_user:
                return {"error": f"User with the name '{user_name}' already exists."}

            new_user = User(name=user_name)
            self.db.session.add(new_user)
            self.db.session.commit()

            return {"success": f"User '{user_name}' was successfully added."}
        except Exception as e:
            self.db.session.rollback()
            return {"error": f"An error occurred: {str(e)}"}

    def delete_user(self, user_id):
        """
        Deletes a user and their associated movies from the database.

        Args:
            user_id (int): ID of the user to be deleted.

        Returns:
            dict: A dictionary with a success or error message.
        """
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return {"error": f"User with ID {user_id} not found"}

            UserMovies.query.filter_by(user_id=user_id).delete()

            self.db.session.delete(user)
            self.db.session.commit()

            return {"success": f"User with ID {user_id} and all associated data have been deleted successfully"}
        except Exception as e:
            self.db.session.rollback()
            return {"error": f"An error occurred while deleting the user: {str(e)}"}

    def get_user_movie(self, user_movie_id):
        """
        Fetches a UserMovies object by its unique ID.

        Args:
            user_movie_id (int): The ID of the UserMovies record to fetch.

        Returns:
            UserMovies or None: UserMovies object if found, else None.
        """
        try:
            user_movie = UserMovies.query.get(user_movie_id)
            return user_movie
        except Exception as e:
            self.db.session.rollback()
            print(f"Error fetching movie by ID: {e}")
            return None

    def get_user_movies(self, user_id):
        """
        Retrieves all movies associated with a specific user, including user-specific overrides.

        Args:
            user_id (int): ID of the user whose movies are to be fetched.

        Returns:
            list: A list of dictionaries containing movie data with user-specific values where applicable.
        """
        try:
            # Query to fetch user-movie relationships and associated movie details
            user_movies = (
                db.session.query(UserMovies, Movie)
                .join(Movie, UserMovies.movie_id == Movie.id)
                .filter(UserMovies.user_id == user_id)
                .all()
            )

            # Construct the result
            result = []
            for user_movie, movie in user_movies:
                result.append({
                    "id": movie.id,
                    "user_movie_id": user_movie.id,
                    "name": user_movie.user_title if user_movie.user_title else movie.name,
                    "year": movie.year,
                    "director": movie.director,
                    "poster": movie.poster,
                    "imdb_link": movie.imdb_link,
                    "rating": movie.rating,
                    "user_title": user_movie.user_title,
                    "user_rating": user_movie.user_rating,
                    "user_notes": user_movie.user_notes,
                    "added_at": user_movie.added_at
                })

            return result

        except Exception as e:
            self.db.session.rollback()
            print(f"Error fetching user movies: {str(e)}")
            return []

    def get_movie_by_id(self, movie_id):
        """
        Fetches a movie by its ID from the database.

        Args:
            movie_id (int): ID of the movie to fetch.

        Returns:
            Movie or None: Movie object if found, else None.
        """
        try:
            movie = Movie.query.get(movie_id)
            return movie
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

    def add_movie(self, user_id, movie_name):
        """
        Adds a movie to a specific user's collection. If the movie doesn't exist, fetches it from OMDb.

        If the movie already exists in the database, it associates the movie with the user.
        The user can add their own title, rating, and notes, while default values are
        fetched from OMDb.

        Args:
            user_id (int): The ID of the user adding the movie.
            movie_name (str): The name of the movie to be added.

        Returns:
            dict: A dictionary containing a success or error message.
        """
        try:
            existing_movie = Movie.query.filter_by(name=movie_name).first()
            user = self.get_user_by_id(user_id)

            if existing_movie:
                existing_user_movie = UserMovies.query.filter_by(user_id=user_id, movie_id=existing_movie.id).first()
                if existing_user_movie:
                    return {"error": f"User '{user.name}' already has the movie '{movie_name}' in their collection."}
                else:
                    association = UserMovies(
                        user_id=user_id,
                        movie_id=existing_movie.id,
                        user_title=movie_name
                    )
                    self.db.session.add(association)
                    self.db.session.commit()
                    return {"success": f"Movie '{movie_name}' was successfully added to user '{user.name}'."}

            else:
                movie_data = MovieInfoDownloader().fetch_movie_data(movie_name)

                new_movie = Movie(
                    name=movie_data.get('name', movie_name),
                    director=movie_data.get('director', None),
                    year=movie_data.get('year', None),
                    rating=movie_data.get('rating', None),
                    poster=movie_data.get('poster', None),
                    imdb_link=movie_data.get('imdb_link', None)
                )
                self.db.session.add(new_movie)
                self.db.session.commit()

                association = UserMovies(
                    user_id=user_id,
                    movie_id=new_movie.id,
                    user_title=movie_name
                )
                self.db.session.add(association)
                self.db.session.commit()

                return {"success": f"Movie '{movie_data['name']}' was successfully added to user '{user.name}'."}

        except APIError as e:
            return {"error": f"Failed to fetch movie data: {str(e)}"}
        except Exception as e:
            self.db.session.rollback()
            return {"error": f"An error occurred: {str(e)}"}

    def update_movie(self, user_movie_id, updated_details):
        """
        Updates the user-specific details of a movie in the UserMovies table.

        Args:
            user_movie_id (int): The ID of the UserMovies record to update.
            updated_details (dict): A dictionary of updated user-specific details (e.g., {'user_title': 'New Title'}).

        Returns:
            dict: A dictionary with success or error message.
        """
        try:
            user_movie = self.get_user_movie(user_movie_id)

            for key, value in updated_details.items():
                if hasattr(user_movie, key):
                    setattr(user_movie, key, value)
                else:
                    return {"error": f"Invalid attribute '{key}' for movie details."}

            self.db.session.commit()

            return {"success": f"Movie '{user_movie.movie.name}' has been successfully updated."}

        except Exception as e:
            self.db.session.rollback()
            return {"error": f"An error occurred while updating the movie: {str(e)}"}

    def delete_movie(self, user_movie_id):
        """
        Deletes a user-specific movie record and its associated data from the database.

        Args:
            user_movie_id (int): The ID of the UserMovies record to delete.

        Returns:
            dict: A dictionary with success or error message.
        """
        try:
            user_movie = self.get_user_movie(user_movie_id)

            if not user_movie:
                return {"error": "This movie is not in your list."}

            movie = user_movie.movie
            user_id = user_movie.user_id

            self.db.session.delete(user_movie)
            self.db.session.commit()

            if not UserMovies.query.filter_by(movie_id=movie.id).first():
                self.db.session.delete(movie)
                self.db.session.commit()

            return {
                "success": f"Movie '{movie.name}' has been successfully removed from your list.",
                "user_id": user_id
            }

        except Exception as e:
            self.db.session.rollback()
            return {"error": f"An error occurred: {str(e)}"}

