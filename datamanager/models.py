from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    # Relationship to UserMovies
    movies = db.relationship('UserMovies', back_populates='user', cascade="all, delete")


class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    director = db.Column(db.String(100))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)

    # Relationship to UserMovies
    users = db.relationship('UserMovies', back_populates='movie', cascade="all, delete")


class UserMovies(db.Model):
    __tablename__ = 'user_movies'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), primary_key=True)

    # Relationships
    user = db.relationship('User', back_populates='movies')
    movie = db.relationship('Movie', back_populates='users')
