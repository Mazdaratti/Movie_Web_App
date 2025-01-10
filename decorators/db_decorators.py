"""
This module provides utility decorators for managing database operations.

Decorators:
    transactional: Ensures a function runs within a database transaction,
    committing changes on success or rolling back on failure.

Usage:
    Use the @transactional decorator to wrap functions that perform database
    operations to handle transactions automatically.

Dependencies:
    - SQLAlchemy session object
    - SQLAlchemyError from sqlalchemy.exc
"""
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError
from datamanager.models import User, Movie, UserMovies
from datamanager.movie_fetcher import APIError
from helpers.logger import logger


def transactional(session):
    """
    Decorator to manage database transactions.

    This decorator ensures that database operations are committed if the
    wrapped function completes successfully. If an exception occurs, it
    rolls back the transaction and re-raises the exception.

    Args:
        session: The SQLAlchemy session object.

    Returns:
        A wrapped function with transaction handling.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                session.commit()
                return result
            except SQLAlchemyError as e:
                session.rollback()
                logger.error(f"Database error in {func.__name__}: {str(e)}")
                raise e
            except APIError as e:
                session.rollback()
                logger.error(f"API error in {func.__name__}: {str(e)}")
                raise e
            except Exception as e:
                session.rollback()
                logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
                raise e

        return wrapper

    return decorator


def validate_user(session):
    """
    Decorator to validate if a user exists in the database.

    Args:
        session (SQLAlchemy session): The database session to use for querying.

    Returns:
        function: The wrapped function, which will raise an error
                  if the user does not exist.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(user_id, *args, **kwargs):
            if not session.query(User).get(user_id):
                return {"error": f"User with ID {user_id} does not exist."}
            return func(user_id, *args, **kwargs)

        return wrapper

    return decorator


def validate_movie(session):
    """
    Decorator to validate if a movie exists in the database.

    Args:
        session (SQLAlchemy session): The database session to use for querying.

    Returns:
        function: The wrapped function, which will raise an error
                  if the movie does not exist.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(movie_id, *args, **kwargs):
            if not session.query(Movie).get(movie_id):
                return {"error": f"Movie with ID {movie_id} does not exist."}
            return func(movie_id, *args, **kwargs)

        return wrapper

    return decorator


def validate_user_movie(session):
    """
    Decorator to validate if a specific movie is in the user's list.

    Args:
        session (SQLAlchemy session): The database session to use for querying.

    Returns:
        function: The wrapped function, which will raise an error
                  if the movie is not in the user's list.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(user_id, movie_id, *args, **kwargs):
            if not session.query(UserMovies).filter_by(user_id=user_id, movie_id=movie_id).first():
                return {"error": f"Movie with ID {movie_id} is not in the user's list."}
            return func(user_id, movie_id, *args, **kwargs)

        return wrapper

    return decorator
