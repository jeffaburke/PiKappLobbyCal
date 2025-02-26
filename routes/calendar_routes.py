"""
Calendar Routes
"""
from flask import Blueprint, render_template
from services.calendar_service import GoogleCalendarAPI

calendar_routes = Blueprint('calendar_routes', __name__)

@calendar_routes.route('/')
def index():
    """
    Renders the Index page
    Returns:
        Rendered template of the index page
    """
    calendar_api = GoogleCalendarAPI()
    service = calendar_api.authenticate()
    weekly_events = calendar_api.get_weeks_events(service)
    return render_template('index.html', events=weekly_events)
