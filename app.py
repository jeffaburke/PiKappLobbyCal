"""
Main Flask Application
"""
from flask import Flask
from routes.photo_routes import photo_routes
from routes.calendar_routes import calendar_routes
from utils.logger import setup_logger

# Setup main application logger
logger = setup_logger(__name__)

app = Flask(__name__)

# Register blueprints
try:
    app.register_blueprint(photo_routes)
    app.register_blueprint(calendar_routes)
    logger.info("Successfully registered all blueprints")
except Exception as e:
    logger.error("Failed to register blueprints: %s", str(e))
    raise

if __name__ == '__main__':
    logger.info("Starting Flask application")
    app.run(debug=True)
