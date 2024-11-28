from flask import Flask, render_template
from datamanager.sqlite_data_manager import SQLiteDataManager
from storage import PATH
from datamanager.models import db

# Create the Flask app
app = Flask(__name__)

# Set up SQLite database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the SQLiteDataManager
data_manager = SQLiteDataManager(app)


@app.route('/users')
def list_users():
    """
    Fetches all users and renders the users list page.
    """
    users = data_manager.get_all_users()
    return render_template('users.html', users=users)


if __name__ == "__main__":
    app.run(debug=True)
