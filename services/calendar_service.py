"""
Google Calendar API Service
"""
import os.path
import pickle
import datetime
from collections import defaultdict
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build

class GoogleCalendarAPI:
    """
    Class to handle Google Calendar API authentication and data fetching
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
        Args:
            service: Takes a Google API build
        Returns:
            Dictionary of events organized by day
        """
        today = datetime.datetime.now(datetime.UTC)
        days_until_sunday = (6 - today.weekday()) % 7

        if days_until_sunday > 0:
            start_of_week = today + datetime.timedelta(days=days_until_sunday)
        else:  # today is Sunday
            start_of_week = today

        start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_week = start_of_week + datetime.timedelta(days=7)

        events_result = service.events().list(
            calendarId='t15olu87ufqa11j6oc2f19kvao@group.calendar.google.com',
            timeMin=start_of_week.isoformat(),
            timeMax=end_of_week.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        return self._organize_events(events_result, start_of_week, end_of_week)

    def _organize_events(self, events_result, start_of_week, end_of_week):
        """
        Organizes events by day and handles all-day events
        """
        events_by_day = defaultdict(list)
        for event in events_result.get('items', []):
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))

            if 'T' not in start:  # All-day event
                self._handle_all_day_event(event, start, end, start_of_week, end_of_week, events_by_day)
            else:
                self._handle_timed_event(event, start, start_of_week, end_of_week, events_by_day)

        return dict(events_by_day)

    def _handle_all_day_event(self, event, start, end, start_of_week, end_of_week, events_by_day):
        """
        Handles processing of all-day events
        """
        start_date = datetime.datetime.fromisoformat(start).replace(tzinfo=datetime.UTC)
        end_date = datetime.datetime.fromisoformat(end).replace(tzinfo=datetime.UTC) - datetime.timedelta(days=1)

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
                events_by_day[day_name].insert(0, event_info)
            current_date += datetime.timedelta(days=1)

    def _handle_timed_event(self, event, start, start_of_week, end_of_week, events_by_day):
        """
        Handles processing of regular timed events
        """
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
