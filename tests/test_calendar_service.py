"""Unit tests for calendar service"""
# pylint: disable=protected-access, redefined-outer-name
import datetime
from collections import defaultdict
from unittest.mock import Mock, patch

import pytest
from services.calendar_service import GoogleCalendarAPI, EventContext, TimedEventContext

@pytest.fixture
def calendar_api():
    """Fixture for calendar API instance"""
    return GoogleCalendarAPI()

@pytest.fixture
def mock_service():
    """Fixture for mocked Google Calendar service"""
    mock = Mock()
    mock.events().list().execute.return_value = {
        'items': [
            {
                'summary': 'All Day Event',
                'start': {'date': '2024-03-20'},
                'end': {'date': '2024-03-22'},
                'location': 'Room 101'
            },
            {
                'summary': 'Timed Event',
                'start': {'dateTime': '2024-03-20T10:00:00Z'},
                'end': {'dateTime': '2024-03-20T11:00:00Z'},
                'location': 'Room 102'
            }
        ]
    }
    return mock

@pytest.fixture
def mock_datetime(monkeypatch):
    """Mock datetime to return a fixed date"""
    FIXED_DATE = datetime.datetime(2024, 3, 20, tzinfo=datetime.UTC)

    class MockDateTime(datetime.datetime):
        @classmethod
        def now(cls, tz=None):
            return FIXED_DATE

    monkeypatch.setattr(datetime, 'datetime', MockDateTime)

# pylint: disable=protected-access
def test_handle_all_day_event(calendar_api):
    """Test handling of all-day events"""
    events_by_day = defaultdict(list)
    context = EventContext(
        start='2024-03-20',
        end='2024-03-22',
        start_of_week=datetime.datetime(2024, 3, 18, tzinfo=datetime.UTC),
        end_of_week=datetime.datetime(2024, 3, 25, tzinfo=datetime.UTC),
        events_by_day=events_by_day
    )

    event = {
        'summary': 'Test Event',
        'location': 'Test Location'
    }

    calendar_api._handle_all_day_event(event, context)

    assert len(events_by_day['Wednesday']) == 1
    assert len(events_by_day['Thursday']) == 1
    assert events_by_day['Wednesday'][0]['isAllDay'] is True
    assert events_by_day['Wednesday'][0]['time'] == 'All Day'

# pylint: disable=protected-access
def test_handle_timed_event(calendar_api):
    """Test handling of timed events"""
    events_by_day = defaultdict(list)
    event_date = datetime.datetime(2024, 3, 20, 10, 0, tzinfo=datetime.UTC)
    context = TimedEventContext(
        event_date=event_date,
        start_of_week=datetime.datetime(2024, 3, 18, tzinfo=datetime.UTC),
        end_of_week=datetime.datetime(2024, 3, 25, tzinfo=datetime.UTC),
        events_by_day=events_by_day
    )

    event = {
        'summary': 'Test Event',
        'location': 'Test Location'
    }

    calendar_api._handle_timed_event(event, context)

    assert len(events_by_day['Wednesday']) == 1
    assert events_by_day['Wednesday'][0]['isAllDay'] is False
    assert events_by_day['Wednesday'][0]['time'] == '10:00 AM'

@patch('services.calendar_service.build')
@patch('services.calendar_service.pickle')
def test_get_weeks_events(mock_pickle, mock_build, calendar_api, mock_service, mock_datetime):  # pylint: disable=unused-argument
    """Test fetching weekly events"""
    mock_build.return_value = mock_service
    mock_pickle.load.return_value = Mock(valid=True)

    events = calendar_api.get_weeks_events(mock_service)

    assert 'Wednesday' in events
    assert len(events['Wednesday']) == 2
    assert any(e['isAllDay'] for e in events['Wednesday'])
    assert any(not e['isAllDay'] for e in events['Wednesday'])
