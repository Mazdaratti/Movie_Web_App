"""
This module defines the database models for the MovieWeb App, including:
- User: Represents a user of the application.
- Movie: Represents movies stored in the database.
- UserMovies: Represents the association between users and movies,
  allowing per-user customizations like user-defined title, rating, and notes.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """
    Represents a user of the MovieWeb App.

    Attributes:
        id (int): The unique identifier for a user.
        name (str): The name of the user.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)


class Movie(db.Model):
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


class UserMovies(db.Model):
    """
    Represents the association between a user and a movie.

    Allows users to customize certain movie attributes while keeping defaults
    fetched from OMDb.

    Attributes:
        id (int): The unique identifier for the user-movie association.
        user_id (int): The foreign key referencing the user.
        movie_id (int): The foreign key referencing the movie.
        user_title (str): The custom title of the movie defined by the user. Defaults to the movie's original name.
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
