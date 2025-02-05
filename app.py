from flask import Flask, render_template
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path
import pickle
import datetime
from collections import defaultdict

app = Flask(__name__)

class GoogleCalendarAPI:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        self.creds = None

    def authenticate(self):
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                self.creds = flow.run_local_server(port=0)

            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

        return build('calendar', 'v3', credentials=self.creds)

    def get_weeks_events(self, service):
        # Get start of current week (Monday)
        today = datetime.datetime.now(datetime.UTC)
        start_of_week = today - datetime.timedelta(days=today.weekday())
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
            event_date = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
            day_name = event_date.strftime('%A')

            event_info = {
                'summary': event.get('summary', 'No Title'),
                'time': event_date.strftime('%I:%M %p'),
                'location': event.get('location', 'No Location')
            }
            events_by_day[day_name].append(event_info)

        return dict(events_by_day)

@app.route('/')
def index():
    calendar_api = GoogleCalendarAPI()
    service = calendar_api.authenticate()
    weekly_events = calendar_api.get_weeks_events(service)
    return render_template('index.html', events=weekly_events)

if __name__ == '__main__':
    app.run(debug=True)