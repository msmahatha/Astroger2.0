from datetime import datetime
import swisseph as swe
import pytz
import time
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from timezonefinderL import TimezoneFinder
from geopy.geocoders import Nominatim
import logging
from typing import Dict
from src.models.kundli_model import KundliChart, Planet, House, Aspect


# Init helpers
geolocator = Nominatim(user_agent="kundli_backend")
tzfinder = TimezoneFinder(in_memory=True)

PLANETS = {
    'Sun': swe.SUN,
    'Moon': swe.MOON,
    'Mercury': swe.MERCURY,
    'Venus': swe.VENUS,
    'Mars': swe.MARS,
    'Jupiter': swe.JUPITER,
    'Saturn': swe.SATURN,
    'Uranus': swe.URANUS,
    'Neptune': swe.NEPTUNE,
    'Pluto': swe.PLUTO,
    'TrueNode': swe.TRUE_NODE,
}

SIGNS = [
    'Aries','Taurus','Gemini','Cancer','Leo','Virgo',
    'Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
    "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshta", "Moola", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]




def geocode_place(place: str):
    for attempt in range(2):  # Try twice
        try:
            loc = geolocator.geocode(place, timeout=5)
            if not loc:
                raise ValueError(f"Could not geocode place: {place}")
            lat, lon = loc.latitude, loc.longitude
            tz = tzfinder.timezone_at(lat=lat, lng=lon)
            return lat, lon, tz or "UTC"
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            if attempt == 0:
                time.sleep(1)  # wait 1 second before retrying
            else:
                raise e
            
            
def parse_birth_datetime(birth_date: str, birth_time: str) -> datetime:
    try:
        return datetime.fromisoformat(f"{birth_date}T{birth_time}")
    except Exception:
        pass
    try:
        date_obj = datetime.strptime(birth_date, "%d-%m-%Y").date()
        if "T" in birth_time:
            birth_time = birth_time.split("T")[-1]
        time_obj = datetime.strptime(birth_time, "%H:%M").time()
        return datetime.combine(date_obj, time_obj)
    except Exception:
        logging.error(f"Failed to parse date/time: {birth_date} {birth_time}")
        raise ValueError("Invalid date/time format. Use YYYY-MM-DD + HH:MM or DD-MM-YYYY + HH:MM")


def datetime_to_jd(dt: datetime, tz: str) -> float:
    tz_obj = pytz.timezone(tz)
    local_dt = tz_obj.localize(dt)
    utc_dt = local_dt.astimezone(pytz.UTC)
    year, month, day = utc_dt.year, utc_dt.month, utc_dt.day
    hour = utc_dt.hour + utc_dt.minute / 60 + utc_dt.second / 3600
    return swe.julday(year, month, day, hour)


def get_nakshatra(longitude: float):
    """Return Nakshatra + Pada from longitude"""
    total_degrees = longitude % 360
    nakshatra_index = int(total_degrees // (360 / 27))
    pada = int((total_degrees % (360 / 27)) // (360 / 108)) + 1
    return NAKSHATRAS[nakshatra_index], pada


def get_aspects(planets: Dict[str, Planet]):
    """Basic aspects (Conjunction, Sextile, Square, Trine, Opposition)."""
    aspects = []
    aspect_types = {
        "Conjunction": 0,
        "Sextile": 60,
        "Square": 90,
        "Trine": 120,
        "Opposition": 180
    }
    planet_names = list(planets.keys())
    for i in range(len(planet_names)):
        for j in range(i + 1, len(planet_names)):
            p1 = planets[planet_names[i]]
            p2 = planets[planet_names[j]]
            diff = abs(p1.longitude - p2.longitude) % 360
            for name, angle in aspect_types.items():
                if abs(diff - angle) <= 5:  # orb of 5 degrees
                    aspects.append(Aspect(
                        between=[p1.name, p2.name],
                        type=name,
                        angle=diff
                    ))
    return aspects


# --------------------------
# Core Computation
# --------------------------
def compute_kundli(birth_date: str, birth_time: str, place: str , gender : str) -> KundliChart:
    try: 
        lat, lon, tz = geocode_place(place)
        dt = parse_birth_datetime(birth_date, birth_time)
        jd_ut = datetime_to_jd(dt, tz)

        # houses
        cusps, asc_mc = swe.houses(jd_ut, lat, lon)
        houses: Dict[int, House] = {}
        for i, cusp in enumerate(cusps, start=1):
            sign_idx = int(cusp // 30)
            houses[i] = House(
                number=i,
                longitude=cusp,
                sign=SIGNS[sign_idx],
                degree=cusp % 30
            )

        # planets
        planets: Dict[str, Planet] = {}
        for name, pid in PLANETS.items():
            xx, ret = swe.calc_ut(jd_ut, pid)
            lon_deg, latp, dist, speed = xx[:4]
            sign_idx = int(lon_deg // 30)
            nakshatra, pada = get_nakshatra(lon_deg)
            # map planet to house
            planet_house = None
            for i in range(1, 13):
                start = houses[i].longitude
                end = houses[1].longitude if i == 12 else houses[i + 1].longitude
                if start <= lon_deg < end or (i == 12 and lon_deg >= start):
                    planet_house = i
                    break
            planets[name] = Planet(
                name=name,
                longitude=lon_deg,
                sign=SIGNS[sign_idx],
                degree=lon_deg % 30,
                retrograde=speed < 0,
                house=planet_house,
                nakshatra=nakshatra,
                pada=pada
            )

        # aspects
        aspects = get_aspects(planets)

        return KundliChart(
            place=place,
            timezone=tz,
            julian_day=jd_ut,
            ascendant=asc_mc[0],
            mc=asc_mc[1],
            planets=planets,
            houses=houses,
            aspects=aspects
        )


    except Exception as e:
        logging.error(f"Error computing kundli: {e}")
        raise ValueError(f"Error computing kundli: {e}")