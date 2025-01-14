from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from geopy import Nominatim
from timezonefinder import TimezoneFinder
import pytz


def process_date_tz(base_date, time_zone):
    base_utc = datetime.strptime(base_date, '%Y-%m-%dT%H:%M:%SZ')
    utc_timezone = pytz.utc
    base_utc = utc_timezone.localize(base_utc)

    return base_utc.astimezone(time_zone)

def get_timezone_from_location(location: str) -> pytz.timezone:
    geolocator = Nominatim(user_agent="github-locator")
    location_data = geolocator.geocode(location)

    if location_data:
        latitude = location_data.latitude
        longitude = location_data.longitude

        tz_finder = TimezoneFinder()
        timezone_str = tz_finder.timezone_at(lng=longitude, lat=latitude)

        if timezone_str:
            timezone = pytz.timezone(timezone_str)
            return timezone
        else:
            raise Exception('Not able to find timezone')
    else:
        raise Exception("Could not find location data")


def get_target_date(timezone, delta=0, utc=False):
    matched_date = datetime.now(timezone) - timedelta(days=delta)

    start_of_day = matched_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = matched_date.replace(hour=23, minute=59, second=59, microsecond=0)
    if utc:
        return end_of_day.astimezone(ZoneInfo('UTC')).strftime('%Y-%m-%dT%H:%M:%SZ'), start_of_day.astimezone(ZoneInfo('UTC')).strftime('%Y-%m-%dT%H:%M:%SZ')
    return end_of_day.strftime('%Y-%m-%dT%H:%M:%SZ'), start_of_day.strftime('%Y-%m-%dT%H:%M:%SZ')