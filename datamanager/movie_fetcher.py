"""
This module provides functionality to fetch movie data from the OMDb API.
It includes methods to interact with the API and retrieve detailed information
about movies based on their titles or other criteria.
"""
import os
import requests
from dotenv import load_dotenv
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException


def load_api_key() -> str:
    """
    Load the API key from environment variables.

    Returns:
        str: The loaded API key.

    Raises:
        ValueError: If the API key is missing or invalid.
    """
    load_dotenv()
    api_key = os.getenv('API_KEY')
    if not api_key:
        raise ValueError("Invalid or missing API key. Please check your .env file.")
    return api_key


class APIError(Exception):
    """Custom exception for handling API-related errors."""


class MovieInfoDownloader:
    """
    A class to fetch movie information using the OMDb API.

    Provides methods to retrieve detailed movie data such as title, year, IMDb rating, and more.
    """

    def __init__(self, api_url: str = None) -> None:
        """
        Initialize the MovieInfoDownloader with an API URL and key.

        Args:
            api_url (str, optional): API URL for fetching movie information. Defaults to OMDb API.
        """
        self._api_url = api_url or "http://www.omdbapi.com/"
        self._api_key = load_api_key()

    def fetch_movie_data(self, title) -> dict:
        """
        Fetch detailed information about a movie by its title.

        Args:
            title (str): Title of the movie to search for.


        Returns:
            dict: A dictionary containing movie details like title, year, IMDb rating, etc.

        Raises:
            APIError: If there is an issue with the request, response, or data processing.
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(HTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.5'
        }

        try:
            response = requests.get(
                f"{self._api_url}?t={title}&apikey={self._api_key}",
                headers=headers,
                timeout=10)
            print('hello')
            response.raise_for_status()
            data = response.json()

            if data.get('Response') == 'False':
                raise APIError(f"OMDb Error: {data.get('Error')}")

            return {
                'name': data.get('Title'),
                'year': int(data.get('Year')) if data.get('Year') else None,
                'rating': float(data.get('imdbRating')) if data.get('imdbRating') else None,
                'poster': data.get('Poster'),
                'director': data.get('Director'),
                'imdb_link': f"https://www.imdb.com/title/{data.get('imdbID')}/"
            }

        except (HTTPError, ConnectionError, Timeout) as req_err:
            raise APIError(f"Request error occurred: {req_err}") from req_err
        except ValueError as json_err:
            raise APIError(f"Error parsing JSON: {json_err}") from json_err
        except RequestException as err:
            raise APIError(f"Error fetching movie info: {err}") from err
