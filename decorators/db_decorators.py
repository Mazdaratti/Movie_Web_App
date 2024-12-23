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
