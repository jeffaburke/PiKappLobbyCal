"""
Main Flask Application
"""
from flask import Flask
from routes.photo_routes import photo_routes
from routes.calendar_routes import calendar_routes
from utils.logger import setup_logger
from config import get_config

# Get configuration based on environment
config = get_config()

# Setup main application logger with environment-specific level
logger = setup_logger(__name__, log_level=config.LOG_LEVEL)

app = Flask(__name__)
app.config.from_object(config)

@app.errorhandler(Exception)
def handle_exception(e):
    """Log unhandled exceptions"""
    logger.error("Unhandled exception: %s", str(e), exc_info=True)
    return "Internal Server Error", 500

# Register blueprints
try:
    app.register_blueprint(photo_routes)
    app.register_blueprint(calendar_routes)
    logger.info("Successfully registered all blueprints")
except Exception as e:
    logger.error("Failed to register blueprints: %s", str(e))
    raise

if __name__ == '__main__':
    logger.info("Starting Flask application in %s mode",
                "production" if app.config['ENV'] == 'production' else "development")
    app.run(debug=app.config['DEBUG'])
