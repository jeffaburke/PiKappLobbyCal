"""
Main Flask Application
"""
from flask import Flask
from routes.photo_routes import photo_routes
from routes.calendar_routes import calendar_routes

app = Flask(__name__)

# Register blueprints
app.register_blueprint(photo_routes)
app.register_blueprint(calendar_routes)

if __name__ == '__main__':
    app.run(debug=True)
