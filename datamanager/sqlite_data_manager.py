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

        :param app: Flask app instance with SQLAlchemy configuration.
        """
        app.app_context().push()  # Ensure app context for SQLAlchemy
        db.init_app(app)  # Initialize SQLAlchemy with Flask app
        self.db = db  # Store the db object for use in methods

    def get_all_users(self):
        """
        Retrieves all users from the database.

        :return: A list of all users.
        """
        return User.query.all()

    def get_user_by_id(self, user_id):
        """
        Fetches a user by their ID from the database.

        :param user_id: ID of the user to fetch.
        :return: User object if found, else None.
        """
        return User.query.get(user_id)

    def add_user(self, user_name):
        """
        Adds a new user to the database if the user does not already exist.

        :param user_name: The name of the user to be added.
        :return: A dictionary containing a success or error message.
        """
        try:
            # Check if the user already exists
            existing_user = User.query.filter_by(name=user_name).first()
            if existing_user:
                return {"error": f"User with the name '{user_name}' already exists."}

            # Create a new user and commit to the database
            new_user = User(name=user_name)
            self.db.session.add(new_user)
            self.db.session.commit()

            return {"success": f"User '{user_name}' was successfully added."}
        except Exception as e:
            # Handle any errors
            return {"error": f"An error occurred: {str(e)}"}

    def delete_user(self, user_id):
        """
        Deletes a user and their associated movies from the database.

        :param user_id: ID of the user to be deleted.
        :return: A dictionary with a success or error message.
        """
        try:
            # Fetch the user by ID
            user = self.get_user_by_id(user_id)
            if not user:
                return {"error": f"User with ID {user_id} not found"}

            # Remove associations in the UserMovies table
            UserMovies.query.filter_by(user_id=user_id).delete()

            # Delete the user
            self.db.session.delete(user)
            self.db.session.commit()

            return {"success": f"User with ID {user_id} and all associated data have been deleted successfully"}
        except Exception as e:
            self.db.session.rollback()  # Rollback any pending changes in case of error
            return {"error": f"An error occurred while deleting the user: {str(e)}"}

    def get_user_movies(self, user_id):
        """
        Retrieves all movies associated with a specific user.

        :param user_id: ID of the user whose movies are to be fetched.
        :return: A list of movies associated with the user.
        """
        user_movies = self.db.session.query(Movie).join(UserMovies).filter(UserMovies.user_id == user_id).all()
        return user_movies

    def add_movie(self, user_id, movie_name):
        """
        Adds a movie to a specific user's collection. If the movie doesn't exist, fetches it from OMDb.

        :param user_id: The ID of the user.
        :param movie_name: A dictionary containing movie information (name, director, year, rating).
        :return: A dictionary containing a success or error message.
        """
        try:
            # Check if the movie already exists in the database based on both title and year
            existing_movie = Movie.query.filter_by(
                name=movie_name).first()
            user = self.get_user_by_id(user_id)
            if existing_movie:
                # Check if the movie is already associated with the user
                existing_user_movie = UserMovies.query.filter_by(user_id=user_id, movie_id=existing_movie.id).first()
                if existing_user_movie:
                    return {
                        "error": f"User '{user.name}' already has the movie '{movie_name}'."}
                else:
                    # Associate the movie with the user
                    association = UserMovies(user_id=user_id, movie_id=existing_movie.id)
                    self.db.session.add(association)
                    self.db.session.commit()
                    return {
                        "success": f"Movie '{movie_name}' was successfully added to user '{user.name}'."}
            else:
                # If movie doesn't exist in the database, fetch data from OMDb
                movie_data = MovieInfoDownloader().fetch_movie_data(movie_name)
                # Create and add the new movie to the database
                new_movie = Movie(**movie_data)
                self.db.session.add(new_movie)
                self.db.session.commit()

                # Now associate the new movie with the user
                association = UserMovies(user_id=user_id, movie_id=new_movie.id)
                self.db.session.add(association)
                self.db.session.commit()

                return {
                    "success": f"Movie '{movie_data['name']}' "
                               f"was successfully added to user '{user.name}'."}

        except APIError as e:
            # Handle errors during the movie data fetch
            return {"error": f"Failed to fetch movie data: {str(e)}"}
        except Exception as e:
            # Handle other errors
            return {"error": f"An error occurred: {str(e)}"}

    def update_movie(self, movie_id, updated_details):
        """
        Updates the details of an existing movie.

        :param movie_id: ID of the movie to be updated.
        :param updated_details: Dictionary of updated details (e.g., {'name': 'New Name', 'year': 2024}).
        :return: A dictionary with a success message or error message.
        """
        try:
            # Fetch the movie by its ID
            movie = Movie.query.get(movie_id)
            if not movie:
                return {"error": f"Movie with ID {movie_id} not found."}

            # Validate and update movie details
            for key, value in updated_details.items():
                if hasattr(movie, key):
                    setattr(movie, key, value)
                else:
                    return {"error": f"Invalid attribute '{key}' for movie."}

            # Commit changes to the database
            self.db.session.commit()

            return {"success": f"Movie '{movie.name}' has been successfully updated."}

        except Exception as e:
            return {"error": f"An error occurred while updating the movie: {str(e)}"}

    def delete_movie(self, movie_id, user_id):
        """
        Deletes the association of a movie with a user. If the movie is no longer associated with any users,
        the movie will be deleted.

        :param movie_id: The ID of the movie to be deleted.
        :param user_id: The ID of the user making the deletion request.
        :return: A dictionary containing success or error message.
        """
        try:
            # Check if the movie exists in the database
            movie = Movie.query.get(movie_id)
            if not movie:
                return {"error": f"Movie with ID {movie_id} does not exist."}

            # Delete the association between the current user and the movie
            association_to_delete = UserMovies.query.filter_by(movie_id=movie_id, user_id=user_id).first()

            if association_to_delete:
                self.db.session.delete(association_to_delete)
                self.db.session.commit()

                # If no other users are associated with the movie, delete the movie itself
                if not UserMovies.query.filter_by(movie_id=movie_id).count():
                    self.db.session.delete(movie)
                    self.db.session.commit()

                return {"success": f"Movie '{movie.name}' has been successfully removed from your list."}

            else:
                return {"error": "No association found between the user and the movie."}

        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}
