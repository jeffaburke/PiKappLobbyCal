"""
Calendar Routes
"""
from flask import Blueprint, render_template
from google.auth.exceptions import GoogleAuthError
from googleapiclient.errors import HttpError
from services.calendar_service import GoogleCalendarAPI
from utils.logger import setup_logger

logger = setup_logger(__name__)
calendar_routes = Blueprint('calendar_routes', __name__)

@calendar_routes.route('/')
def index():
    """
    Renders the Index page
    Returns:
        Rendered template of the index page
    """
    try:
        calendar_api = GoogleCalendarAPI()
        logger.info("Authenticating with Google Calendar API")
        service = calendar_api.authenticate()

        logger.info("Fetching weekly events")
        weekly_events = calendar_api.get_weeks_events(service)

        logger.debug("Events fetched: %s", weekly_events)
        return render_template('index.html', events=weekly_events)
    except (GoogleAuthError, HttpError) as e:
        logger.error("Google Calendar API error: %s", str(e))
        return render_template('index.html', events={})
    except OSError as e:
        logger.error("File system error: %s", str(e))
        return render_template('index.html', events={})
