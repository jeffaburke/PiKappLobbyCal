"""
Calendar Routes
"""
import datetime

from flask import Blueprint, render_template, current_app
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
        calendar_api = GoogleCalendarAPI(calendar_id=current_app.config['CALENDAR_ID'])
        logger.info("Authenticating with Google Calendar API")
        service = calendar_api.authenticate()

        logger.info("Fetching weekly events")
        weekly_events = calendar_api.get_weeks_events(service)

        current_day = datetime.datetime.now().strftime('%A')
        logger.debug("Events fetched: %s", weekly_events)
        return render_template('index.html', events=weekly_events, current_day=current_day)
    except (GoogleAuthError, HttpError) as e:
        logger.error("Google Calendar API error: %s", str(e))
        return render_template('index.html', events={}, current_day=datetime.datetime.now().strftime('%A'))
    except OSError as e:
        logger.error("File system error: %s", str(e))
        return render_template('index.html', events={})
