"""
Google Calendar API Service
"""
# pylint: disable=line-too-long, disable=broad-exception-caught

import os.path
import pickle
import datetime
from collections import defaultdict
from dataclasses import dataclass

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from utils.logger import setup_logger

logger = setup_logger(__name__)

@dataclass
class EventContext:
    """Context for event handling"""
    start: str
    end: str
    start_of_week: datetime.datetime
    end_of_week: datetime.datetime
    events_by_day: defaultdict


@dataclass
class TimedEventContext:
    """Context for timed event handling"""
    event_date: datetime.datetime
    start_of_week: datetime.datetime
    end_of_week: datetime.datetime
    events_by_day: defaultdict


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
        try:
            if not os.path.exists('token.pickle'):
                return self._create_new_credentials()

            self.creds = self._load_existing_credentials()
            if not self.creds:
                return self._create_new_credentials()

            if not self.creds.valid:
                self.creds = self._refresh_credentials()
                if not self.creds:
                    return self._create_new_credentials()

            return build('calendar', 'v3', credentials=self.creds)

        except Exception as e:
            logger.error("Authentication failed: %s", str(e))
            raise

    def _load_existing_credentials(self):
        """Load credentials from token file"""
        try:
            with open('token.pickle', 'rb') as token:
                return pickle.load(token)
        except Exception as e:
            logger.error("Error loading token: %s", str(e))
            if os.path.exists('token.pickle'):
                os.remove('token.pickle')
            return None

    def _refresh_credentials(self):
        """Refresh expired credentials"""
        if not self.creds.expired or not self.creds.refresh_token:
            return None

        try:
            self.creds.refresh(Request())
            return self.creds
        except RefreshError:
            logger.warning("Failed to refresh token, forcing re-authentication")
            if os.path.exists('token.pickle'):
                os.remove('token.pickle')
            return None

    def _create_new_credentials(self):
        """Create new credentials using OAuth flow"""
        logger.info("Starting OAuth flow")
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', self.scopes)
        self.creds = flow.run_local_server(port=0)
        logger.info("OAuth flow completed successfully")

        with open('token.pickle', 'wb') as token:
            pickle.dump(self.creds, token)
            logger.debug("Saved new credentials to token.pickle")

        return build('calendar', 'v3', credentials=self.creds)

    def get_weeks_events(self, service):
        """
        Collect the events for the current week starting from Monday
        Args:
            service: Takes a Google API build
        Returns:
            Dictionary of events organized by day
        """
        today = datetime.datetime.now(datetime.UTC)

        # Calculate days since Monday (0 = Monday, 6 = Sunday)
        days_since_monday = today.weekday()

        # Go back to Monday of current week
        start_of_week = today - datetime.timedelta(days=days_since_monday)
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

        # End of week is 7 days after start
        end_of_week = start_of_week + datetime.timedelta(days=7)

        events_result = service.events().list(
            calendarId='t15olu87ufqa11j6oc2f19kvao@group.calendar.google.com',
            timeMin=start_of_week.isoformat(),
            timeMax=end_of_week.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        logger.info("Successfully fetched weekly events")
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
                self._handle_all_day_event(event, EventContext(start, end, start_of_week, end_of_week, events_by_day))
            else:
                self._handle_timed_event(event, TimedEventContext(datetime.datetime.fromisoformat(start.replace('Z', '+00:00')), start_of_week, end_of_week, events_by_day))

        return dict(events_by_day)

    def _handle_all_day_event(self, event: dict, context: EventContext):
        """Handles processing of all-day events"""
        start_date = datetime.datetime.fromisoformat(context.start).replace(tzinfo=datetime.UTC)
        end_date = datetime.datetime.fromisoformat(context.end).replace(tzinfo=datetime.UTC) - datetime.timedelta(days=1)

        current_date = start_date
        while current_date <= end_date:
            if context.start_of_week <= current_date < context.end_of_week:
                day_name = current_date.strftime('%A')
                event_info = {
                    'summary': event.get('summary', 'No Title'),
                    'time': 'All Day',
                    'location': event.get('location', 'No Location'),
                    'isAllDay': True
                }
                context.events_by_day[day_name].insert(0, event_info)
            current_date += datetime.timedelta(days=1)

    def _handle_timed_event(self, event: dict, context: TimedEventContext):
        """Handles processing of regular timed events"""
        if context.start_of_week <= context.event_date < context.end_of_week:
            day_name = context.event_date.strftime('%A')
            event_info = {
                'summary': event.get('summary', 'No Title'),
                'time': context.event_date.strftime('%I:%M %p'),
                'location': event.get('location', 'No Location'),
                'isAllDay': False
            }
            context.events_by_day[day_name].append(event_info)
