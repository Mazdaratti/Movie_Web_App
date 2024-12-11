"""
This module defines the database models for the MovieWeb App, including:
- User: Represents a user of the application.
- Movie: Represents movies stored in the database.
- UserMovies: Represents the association between users and movies,
  allowing per-user customizations like user-defined title, rating, and notes.
"""
from datetime import datetime
import validators
from sqlalchemy.orm import validates
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class BaseModel(db.Model):
    """
    A base model that provides a `to_dict` method for all child classes.
    """
    __abstract__ = True  # Mark this class as abstract; it won't be created as a table.

    def to_dict(self, include_relationships=False, _seen=None):
        """
        Converts all column attributes of the model into a dictionary.
        Optionally includes related objects.
        """
        if _seen is None:
            _seen = set()

            # Prevent circular references
        obj_id = id(self)
        if obj_id in _seen:
            return {'id': self.id}  # Fallback to a basic representation
        _seen.add(obj_id)
        result = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        # Serialize relationships
        if include_relationships:
            for relationship in self.__mapper__.relationships:
                related_value = getattr(self, relationship.key)
                if isinstance(related_value, list):  # For one-to-many relationships
                    result[relationship.key] = [
                        item.to_dict(include_relationships, _seen) for item in related_value]
                elif related_value:  # For one-to-one or many-to-one relationships
                    result[relationship.key] = related_value.to_dict(include_relationships, _seen)
        return result


class User(BaseModel):
    """
    Represents a user of the MovieWeb App.

    Attributes:
        id (int): The unique identifier for a user.
        name (str): The name of the user.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)


class Movie(BaseModel):
    """
    Represents a movie in the MovieWeb App.

    Attributes:
        id (int): The unique identifier for a movie.
        name (str): The default name of the movie, fetched from OMDb.
        director (str): The director of the movie, fetched from OMDb.
        year (int): The year the movie was released, fetched from OMDb.
        rating (float): The default rating of the movie, fetched from OMDb.
        poster (str): The URL of the movie poster, fetched from OMDb.
        imdb_link (str): The IMDb link for the movie.
    """
    __tablename__ = 'movies'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    director = db.Column(db.String(100))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    poster = db.Column(db.String(255))
    imdb_link = db.Column(db.String(255))

    @validates('poster', 'imdb_link')
    def validate_url(self, key, value):
        """
        Validates that the given URL fields (poster, imdb_link) contain valid URLs.

        Args:
            key (str): The name of the field being validated.
            value (str): The value being assigned to the field.

        Returns:
            str: The validated URL if it is valid.

        Raises:
            ValueError: If the URL is not valid.
        """
        if value and not validators.url(value):
            raise ValueError(f"{key} must be a valid URL.")
        return value

    @validates('year')
    def validate_year(self, key, value):
        """
        Validates the year field to ensure it is logical.

        Args:
            key (str): The name of the field being validated.
            value (int): The value being assigned to the field.

        Returns:
            int: The validated year.

        Raises:
            ValueError: If the year is not between 1888 and the current year.
        """
        current_year = datetime.now().year
        if value < 1888 or value > current_year:
            raise ValueError(f"{key} must be between 1888 and {current_year}.")
        return value


class UserMovies(BaseModel):
    """
    Represents the association between a user and a movie.

    Allows users to customize certain movie attributes while keeping defaults
    fetched from OMDb.

    Attributes:
        id (int): The unique identifier for the user-movie association.
        user_id (int): The foreign key referencing the user.
        movie_id (int): The foreign key referencing the movie.
        user_title (str): The custom title of the movie defined by the user.
                          Defaults to the movie's original name.
        user_rating (float): The rating given by the user. Defaults to the movie's rating.
        user_notes (str): Notes about the movie added by the user.
        added_at (datetime): The timestamp when the user added the movie to their list.
    """
    __tablename__ = 'user_movies'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    user_title = db.Column(db.String(100))
    user_rating = db.Column(db.Float)
    user_notes = db.Column(db.Text)
    added_at = db.Column(db.DateTime, default=db.func.now())

    # Define relationships for easier querying
    user = db.relationship('User', backref=db.backref('user_movies', lazy=True))
    movie = db.relationship('Movie', backref=db.backref('user_movies', lazy=True))
