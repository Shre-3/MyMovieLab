# PACKAGES
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from flask_bootstrap import Bootstrap5
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize the app and database instances
app = Flask(__name__)
bootstrap = Bootstrap5(app)
db = SQLAlchemy()
# app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')  #REPLACE THE BELOW SECRET KEY CODE WITH THIS LINE AT TIME OF PRODUCTION
app.config['SECRET_KEY'] = os.urandom(24)
# MYSQL DB INITIALIZATION
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@localhost/{os.getenv('MYSQL_DB')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)

# Function to create the app
def create_app():
    # Register Blueprints here if needed
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Other configurations, if needed
    with app.app_context():
        print("App context loaded. Creating tables...")
        db.create_all()
        print("Tables created successfully!")

    return app
