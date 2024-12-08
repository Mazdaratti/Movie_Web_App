# MovieWeb App 🎥

MovieWeb App is a simple, Flask-based application designed to manage and display favorite movies. It demonstrates the use of Flask for dynamic web content, integration with the OMDb API, and responsive design for a smooth user experience.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)
- [Project Requirements](#project-requirements)
- [Contributing](#contributing)
- [License](#license)

## Features 🛠

- **User Management**: Add, view and delete users.
- **Movie Management**: Add movies to a user's list by fetching data from the OMDb API.
- **Update and Delete Movies**: Modify or remove movies from a user's favorites.
- **Dynamic Data Display**: Fetch and display movies with detailed information like IMDb ratings and posters.
- **Responsive Design**: Clean and user-friendly interface styled with Bootstrap.
- **RESTful API for programmatic access**
- 
## Installation ⚙

### Prerequisites
- **Python**: Version 3.7 or higher.
- **pip**: Python package manager.

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/Mazdaratti/Movie_Web_App.git
2. Navigate to the project directory:
   ```bash
   cd MovieWeb_App
3. Create a virtual environment (optional but recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # For Windows: venv\Scripts\activate
4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
5. Set up your OMDb API key:
   - Create a .env file in the project root.
   - Add the following line:
     ```makefile
     OMDB_API_KEY=your_api_key_here
6. Run the application:
   ```bash
   flask run
7. Open your browser and navigate to:
   ```arduino
   http://127.0.0.1:5000
   
## Usage 📖

To use the MovieWeb App:

1. Home Page:
   - View featured movies fetched from the database.
2. Users Page:
   - View a list of all users.
   - Add new users or manage existing ones.
3. Movie Management:
   - Add movies to a user's list using the OMDb API.
   - Edit or delete movies from the user's favorites.
4. Error Handling:
   - Friendly error messages are displayed for server or user-related issues.

## Project Structure 📂
```
MovieWeb_App/
├── datamanager/
│   ├── __init__.py                # Package initializer
│   ├── data_manager.py            # Main logic for data operations
│   ├── models.py                  # ORM models
│   ├── movie_fetcher.py           # OMDb API integration
│   └── sqlite_data_manager.py     # SQLite data manager implementation   
├── helpers/
│   ├── __init__.py                # Package initializer
│   ├── api_helpers.py             # Helper functions for API-related tasks
│   ├── html_helpers.py            # Helper functions for HTML rendering
│   └── logger.py                  # Logger configuration module
├── routes/
│   ├── __init__.py                # Package initializer
│   ├── api_routes.py              # API routes for managing movies and users
│   ├── error_handlers.py          # Error handler routes
│   └── html_routes.py             # HTML routes for managing user interface
├── decorators/
│   ├── api_decorators.py          # API-specific decorators
│   ├── html_decorators.py         # HTML-specific decorators
│   └── shared_decorators.py       # Common/shared decorators
├── static/
│   ├── form-validation.js         # Client-side form validation
│   └── style.css                  # Custom styles
├── storage/
│   ├── __init__.py                # Package initializer
│   └── movieweb.sqlite            # SQLite database file
├── templates/
│   ├── 404.html                   # Page not found
│   ├── 500.html                   # Internal server error
│   ├── add_movie.html             # Add movie form
│   ├── add_user.html              # Add user form
│   ├── base.html                  # Base layout
│   ├── error.html                 # Error page
│   ├── home.html                  # Home page
│   ├── update_movie.html          # Edit movie form
│   ├── user_movies.html           # User's favorite movies
│   └── users.html                 # Users list page
├── app.log                        # Application logs
├── app.py                         # Main application file
├── initial.py                     # Initialization and app setup file
├── README.md                      # Project documentation
└── requirements.txt               # Dependencies

```
## Technologies Used 💻

   - Flask: Backend framework.
   - Jinja2: Templating engine for dynamic HTML rendering.
   - Bootstrap: Frontend framework for responsive design.
   - SQLite: Database for user and movie storage.
   - OMDb API: External API for fetching movie data.

## Project Requirements 📦

   - Python 3.x
   - Flask 3.0.3
   - Jinja2 3.1.4
   - OMDb API Key

## Contributing 🤝

Contributions are welcome! To contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature-branch
3. Commit your changes:
   ```bash
   git commit -am 'Add new feature'
4. Push to the branch:
   ```bash
   git push origin feature-branch
5. Create a Pull Request.

## Lisense 📜

---

This revised version adds a table of contents, a more detailed usage section, and a clear project structure outline. It’s designed for easy navigation and user-friendliness for anyone setting up or contributing to the project.