"""
Operating System Path Library
"""
import os.path
import pickle
import datetime
from collections import defaultdict
from flask import Flask, jsonify, render_template, url_for
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build

app = Flask(__name__)

class GoogleCalendarAPI:
    """
    Class to handle Google Calndar API authentication
    """
    def __init__(self):
        self.scopes = ['https://www.googleapis.com/auth/calendar.readonly']
        self.creds = None

    def authenticate(self):
        """
        Authenticates using the credentials.json file or token.pickle
        Returns:
            Build of the calendar API with the credentials
        """
        # First try to load existing token
        if os.path.exists('token.pickle'):
            try:
                with open('token.pickle', 'rb') as token:
                    self.creds = pickle.load(token)

                # Test if token is valid or can be refreshed
                if not self.creds.valid:
                    if self.creds.expired and self.creds.refresh_token:
                        try:
                            self.creds.refresh(Request())
                        except RefreshError:
                            # If refresh fails, remove token and force re-authentication
                            os.remove('token.pickle')
                            self.creds = None
                    else:
                        os.remove('token.pickle')
                        self.creds = None

            except Exception:
                # If there's any error loading/using token, remove it
                os.remove('token.pickle')
                self.creds = None

        # If no valid credentials available, do the OAuth flow
        if not self.creds:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', self.scopes)
            self.creds = flow.run_local_server(port=0)
            # Save the new credentials
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

        return build('calendar', 'v3', credentials=self.creds)

    def get_weeks_events(self, service):
        """
        Collect the events for the upcoming week starting from next Sunday
        (or current Sunday if today is Sunday)
        Args:
            service: Takes a Google API build
        """
        today = datetime.datetime.now(datetime.UTC)

        # Calculate days until next Sunday
        days_until_sunday = (6 - today.weekday()) % 7

        # If today is not Sunday, start from next Sunday
        # If today is Sunday, start from today
        if days_until_sunday > 0:
            start_of_week = today + datetime.timedelta(days=days_until_sunday)
        else:  # today is Sunday
            start_of_week = today

        # Set to beginning of the day (midnight)
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_week = start_of_week + datetime.timedelta(days=7)

        events_result = service.events().list(
            calendarId='t15olu87ufqa11j6oc2f19kvao@group.calendar.google.com',
            timeMin=start_of_week.isoformat(),
            timeMax=end_of_week.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        # Organize events by day
        events_by_day = defaultdict(list)
        for event in events_result.get('items', []):
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))

            # Handle all-day events
            if 'T' not in start:  # This is an all-day event
                # Make timezone-aware by adding UTC timezone
                start_date = datetime.datetime.fromisoformat(start).replace(tzinfo=datetime.UTC)
                # For all-day events, end date is exclusive, so subtract one day
                end_date = datetime.datetime.fromisoformat(end).replace(tzinfo=datetime.UTC) - datetime.timedelta(days=1)

                # For each day in the event's duration
                current_date = start_date
                while current_date <= end_date:
                    if start_of_week <= current_date < end_of_week:
                        day_name = current_date.strftime('%A')
                        event_info = {
                            'summary': event.get('summary', 'No Title'),
                            'time': 'All Day',
                            'location': event.get('location', 'No Location'),
                            'isAllDay': True
                        }
                        # Insert all-day events at the beginning of the day's list
                        events_by_day[day_name].insert(0, event_info)
                    current_date += datetime.timedelta(days=1)
            else:
                # Handle regular timed events
                event_date = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
                if start_of_week <= event_date < end_of_week:
                    day_name = event_date.strftime('%A')
                    event_info = {
                        'summary': event.get('summary', 'No Title'),
                        'time': event_date.strftime('%I:%M %p'),
                        'location': event.get('location', 'No Location'),
                        'isAllDay': False
                    }
                    events_by_day[day_name].append(event_info)

        return dict(events_by_day)

@app.route('/')
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

@app.route('/get_photos')
def get_photos():
    """
    Grabs a json list of the photos in the album
    """
    album_path = os.path.join(app.static_folder, 'album')
    photos = []
    for file in os.listdir(album_path):
        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
            photos.append(url_for('static', filename=f'album/{file}'))
    return jsonify(photos)

if __name__ == '__main__':
    app.run(debug=True)
