# # # # from datetime import datetime
# # # # import swisseph as swe
# # # # import pytz
# # # # import time
# # # # from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
# # # # from timezonefinderL import TimezoneFinder
# # # # from geopy.geocoders import Nominatim
# # # # import logging
# # # # from typing import Dict
# # # # from src.models.kundli_model import KundliChart, Planet, House, Aspect


# # # # # Init helpers
# # # # geolocator = Nominatim(user_agent="kundli_backend")
# # # # tzfinder = TimezoneFinder(in_memory=True)

# # # # PLANETS = {
# # # #     'Sun': swe.SUN,
# # # #     'Moon': swe.MOON,
# # # #     'Mercury': swe.MERCURY,
# # # #     'Venus': swe.VENUS,
# # # #     'Mars': swe.MARS,
# # # #     'Jupiter': swe.JUPITER,
# # # #     'Saturn': swe.SATURN,
# # # #     'Uranus': swe.URANUS,
# # # #     'Neptune': swe.NEPTUNE,
# # # #     'Pluto': swe.PLUTO,
# # # #     'TrueNode': swe.TRUE_NODE,
# # # # }

# # # # SIGNS = [
# # # #     'Aries','Taurus','Gemini','Cancer','Leo','Virgo',
# # # #     'Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'
# # # # ]

# # # # NAKSHATRAS = [
# # # #     "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
# # # #     "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
# # # #     "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
# # # #     "Vishakha", "Anuradha", "Jyeshta", "Moola", "Purva Ashadha",
# # # #     "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
# # # #     "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
# # # # ]




# # # # def geocode_place(place: str):
# # # #     for attempt in range(2):  # Try twice
# # # #         try:
# # # #             loc = geolocator.geocode(place, timeout=5)
# # # #             if not loc:
# # # #                 raise ValueError(f"Could not geocode place: {place}")
# # # #             lat, lon = loc.latitude, loc.longitude
# # # #             tz = tzfinder.timezone_at(lat=lat, lng=lon)
# # # #             return lat, lon, tz or "UTC"
# # # #         except (GeocoderTimedOut, GeocoderUnavailable) as e:
# # # #             if attempt == 0:
# # # #                 time.sleep(1)  # wait 1 second before retrying
# # # #             else:
# # # #                 raise e
            
            
# # # # def parse_birth_datetime(birth_date: str, birth_time: str) -> datetime:
# # # #     try:
# # # #         return datetime.fromisoformat(f"{birth_date}T{birth_time}")
# # # #     except Exception:
# # # #         pass
# # # #     try:
# # # #         date_obj = datetime.strptime(birth_date, "%d-%m-%Y").date()
# # # #         if "T" in birth_time:
# # # #             birth_time = birth_time.split("T")[-1]
# # # #         time_obj = datetime.strptime(birth_time, "%H:%M").time()
# # # #         return datetime.combine(date_obj, time_obj)
# # # #     except Exception:
# # # #         logging.error(f"Failed to parse date/time: {birth_date} {birth_time}")
# # # #         raise ValueError("Invalid date/time format. Use YYYY-MM-DD + HH:MM or DD-MM-YYYY + HH:MM")


# # # # def datetime_to_jd(dt: datetime, tz: str) -> float:
# # # #     tz_obj = pytz.timezone(tz)
# # # #     local_dt = tz_obj.localize(dt)
# # # #     utc_dt = local_dt.astimezone(pytz.UTC)
# # # #     year, month, day = utc_dt.year, utc_dt.month, utc_dt.day
# # # #     hour = utc_dt.hour + utc_dt.minute / 60 + utc_dt.second / 3600
# # # #     return swe.julday(year, month, day, hour)


# # # # def get_nakshatra(longitude: float):
# # # #     """Return Nakshatra + Pada from longitude"""
# # # #     total_degrees = longitude % 360
# # # #     nakshatra_index = int(total_degrees // (360 / 27))
# # # #     pada = int((total_degrees % (360 / 27)) // (360 / 108)) + 1
# # # #     return NAKSHATRAS[nakshatra_index], pada


# # # # def get_aspects(planets: Dict[str, Planet]):
# # # #     """Basic aspects (Conjunction, Sextile, Square, Trine, Opposition)."""
# # # #     aspects = []
# # # #     aspect_types = {
# # # #         "Conjunction": 0,
# # # #         "Sextile": 60,
# # # #         "Square": 90,
# # # #         "Trine": 120,
# # # #         "Opposition": 180
# # # #     }
# # # #     planet_names = list(planets.keys())
# # # #     for i in range(len(planet_names)):
# # # #         for j in range(i + 1, len(planet_names)):
# # # #             p1 = planets[planet_names[i]]
# # # #             p2 = planets[planet_names[j]]
# # # #             diff = abs(p1.longitude - p2.longitude) % 360
# # # #             for name, angle in aspect_types.items():
# # # #                 if abs(diff - angle) <= 5:  # orb of 5 degrees
# # # #                     aspects.append(Aspect(
# # # #                         between=[p1.name, p2.name],
# # # #                         type=name,
# # # #                         angle=diff
# # # #                     ))
# # # #     return aspects


# # # # # --------------------------
# # # # # Core Computation
# # # # # --------------------------
# # # # def compute_kundli(birth_date: str, birth_time: str, place: str , gender : str) -> KundliChart:
# # # #     try: 
# # # #         lat, lon, tz = geocode_place(place)
# # # #         dt = parse_birth_datetime(birth_date, birth_time)
# # # #         jd_ut = datetime_to_jd(dt, tz)

# # # #         # houses
# # # #         cusps, asc_mc = swe.houses(jd_ut, lat, lon)
# # # #         houses: Dict[int, House] = {}
# # # #         for i, cusp in enumerate(cusps, start=1):
# # # #             sign_idx = int(cusp // 30)
# # # #             houses[i] = House(
# # # #                 number=i,
# # # #                 longitude=cusp,
# # # #                 sign=SIGNS[sign_idx],
# # # #                 degree=cusp % 30
# # # #             )

# # # #         # planets
# # # #         planets: Dict[str, Planet] = {}
# # # #         for name, pid in PLANETS.items():
# # # #             xx, ret = swe.calc_ut(jd_ut, pid)
# # # #             lon_deg, latp, dist, speed = xx[:4]
# # # #             sign_idx = int(lon_deg // 30)
# # # #             nakshatra, pada = get_nakshatra(lon_deg)
# # # #             # map planet to house
# # # #             planet_house = None
# # # #             for i in range(1, 13):
# # # #                 start = houses[i].longitude
# # # #                 end = houses[1].longitude if i == 12 else houses[i + 1].longitude
# # # #                 if start <= lon_deg < end or (i == 12 and lon_deg >= start):
# # # #                     planet_house = i
# # # #                     break
# # # #             planets[name] = Planet(
# # # #                 name=name,
# # # #                 longitude=lon_deg,
# # # #                 sign=SIGNS[sign_idx],
# # # #                 degree=lon_deg % 30,
# # # #                 retrograde=speed < 0,
# # # #                 house=planet_house,
# # # #                 nakshatra=nakshatra,
# # # #                 pada=pada
# # # #             )

# # # #         # aspects
# # # #         aspects = get_aspects(planets)

# # # #         return KundliChart(
# # # #             place=place,
# # # #             timezone=tz,
# # # #             julian_day=jd_ut,
# # # #             ascendant=asc_mc[0],
# # # #             mc=asc_mc[1],
# # # #             planets=planets,
# # # #             houses=houses,
# # # #             aspects=aspects
# # # #         )


# # # #     except Exception as e:
# # # #         logging.error(f"Error computing kundli: {e}")
# # # #         raise ValueError(f"Error computing kundli: {e}")


# # # from datetime import datetime
# # # import swisseph as swe
# # # import pytz
# # # import time
# # # from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
# # # from timezonefinderL import TimezoneFinder
# # # from geopy.geocoders import Nominatim
# # # import logging
# # # from typing import Dict, List, Tuple
# # # from src.models.kundli_model import KundliChart, Planet, House, Aspect

# # # # Init helpers
# # # geolocator = Nominatim(user_agent="kundli_backend")
# # # tzfinder = TimezoneFinder(in_memory=True)

# # # PLANETS = {
# # #     'Sun': swe.SUN,
# # #     'Moon': swe.MOON,
# # #     'Mercury': swe.MERCURY,
# # #     'Venus': swe.VENUS,
# # #     'Mars': swe.MARS,
# # #     'Jupiter': swe.JUPITER,
# # #     'Saturn': swe.SATURN,
# # #     'Uranus': swe.URANUS,
# # #     'Neptune': swe.NEPTUNE,
# # #     'Pluto': swe.PLUTO,
# # #     'TrueNode': swe.TRUE_NODE,
# # #     'Rahu': swe.MEAN_NODE,  # Added for Indian astrology
# # # }

# # # SIGNS = [
# # #     'Aries','Taurus','Gemini','Cancer','Leo','Virgo',
# # #     'Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'
# # # ]

# # # SIGN_LORDS = {
# # #     'Aries': 'Mars',
# # #     'Taurus': 'Venus', 
# # #     'Gemini': 'Mercury',
# # #     'Cancer': 'Moon',
# # #     'Leo': 'Sun',
# # #     'Virgo': 'Mercury',
# # #     'Libra': 'Venus',
# # #     'Scorpio': 'Mars',
# # #     'Sagittarius': 'Jupiter',
# # #     'Capricorn': 'Saturn',
# # #     'Aquarius': 'Saturn',
# # #     'Pisces': 'Jupiter'
# # # }

# # # NAKSHATRAS = [
# # #     "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
# # #     "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
# # #     "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
# # #     "Vishakha", "Anuradha", "Jyeshta", "Moola", "Purva Ashadha",
# # #     "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
# # #     "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
# # # ]

# # # NAKSHATRA_LORDS = {
# # #     "Ashwini": "Ketu", "Bharani": "Venus", "Krittika": "Sun", 
# # #     "Rohini": "Moon", "Mrigashira": "Mars", "Ardra": "Rahu",
# # #     "Punarvasu": "Jupiter", "Pushya": "Saturn", "Ashlesha": "Mercury",
# # #     "Magha": "Ketu", "Purva Phalguni": "Venus", "Uttara Phalguni": "Sun",
# # #     "Hasta": "Moon", "Chitra": "Mars", "Swati": "Rahu",
# # #     "Vishakha": "Jupiter", "Anuradha": "Saturn", "Jyeshta": "Mercury",
# # #     "Moola": "Ketu", "Purva Ashadha": "Venus", "Uttara Ashadha": "Sun",
# # #     "Shravana": "Moon", "Dhanishta": "Mars", "Shatabhisha": "Rahu",
# # #     "Purva Bhadrapada": "Jupiter", "Uttara Bhadrapada": "Saturn", "Revati": "Mercury"
# # # }

# # # # Planetary relationships (Friend/Enemy/Neutral)
# # # PLANETARY_RELATIONSHIPS = {
# # #     'Sun': {'friend': ['Moon', 'Mars', 'Jupiter'], 'enemy': ['Venus', 'Saturn'], 'neutral': ['Mercury']},
# # #     'Moon': {'friend': ['Sun', 'Mercury'], 'enemy': [], 'neutral': ['Mars', 'Venus', 'Jupiter', 'Saturn']},
# # #     'Mars': {'friend': ['Sun', 'Moon', 'Jupiter'], 'enemy': ['Mercury'], 'neutral': ['Venus', 'Saturn']},
# # #     'Mercury': {'friend': ['Sun', 'Venus'], 'enemy': ['Moon'], 'neutral': ['Mars', 'Jupiter', 'Saturn']},
# # #     'Jupiter': {'friend': ['Sun', 'Moon', 'Mars'], 'enemy': ['Mercury', 'Venus'], 'neutral': ['Saturn']},
# # #     'Venus': {'friend': ['Mercury', 'Saturn'], 'enemy': ['Sun', 'Moon'], 'neutral': ['Mars', 'Jupiter']},
# # #     'Saturn': {'friend': ['Mercury', 'Venus'], 'enemy': ['Sun', 'Moon', 'Mars'], 'neutral': ['Jupiter']}
# # # }

# # # # ---------------------------------------------------------
# # # # FIXED: Reliable Geocoding + Timezone Handling
# # # # ---------------------------------------------------------
# # # def geocode_place(place: str):
# # #     for attempt in range(2):
# # #         try:
# # #             loc = geolocator.geocode(place, timeout=5)
# # #             if not loc:
# # #                 raise ValueError(f"Could not geocode place: {place}")

# # #             lat, lon = loc.latitude, loc.longitude
# # #             tz = tzfinder.timezone_at(lat=lat, lng=lon)

# # #             if tz is None:
# # #                 tz = "Asia/Kolkata"  # fallback

# # #             return lat, lon, tz

# # #         except (GeocoderTimedOut, GeocoderUnavailable):
# # #             if attempt == 0:
# # #                 time.sleep(1)
# # #             else:
# # #                 raise

# # # # ---------------------------------------------------------
# # # # Parse Birth Datetime
# # # # ---------------------------------------------------------
# # # def parse_birth_datetime(birth_date: str, birth_time: str) -> datetime:
# # #     try:
# # #         return datetime.fromisoformat(f"{birth_date}T{birth_time}")
# # #     except Exception:
# # #         pass

# # #     try:
# # #         dt = datetime.strptime(f"{birth_date} {birth_time}", "%d-%m-%Y %H:%M")
# # #         return dt
# # #     except Exception:
# # #         raise ValueError("Invalid date/time format. Use YYYY-MM-DD + HH:MM or DD-MM-YYYY + HH:MM")

# # # # ---------------------------------------------------------
# # # # Convert to Julian Day (Correct Timezone)
# # # # ---------------------------------------------------------
# # # def datetime_to_jd(dt: datetime, tz: str) -> float:
# # #     tz_obj = pytz.timezone(tz)
# # #     dt_local = tz_obj.localize(dt)
# # #     dt_utc = dt_local.astimezone(pytz.UTC)

# # #     year, month, day = dt_utc.year, dt_utc.month, dt_utc.day
# # #     hour = dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600

# # #     return swe.julday(year, month, day, hour)

# # # # ---------------------------------------------------------
# # # # Nakshatra Calculation
# # # # ---------------------------------------------------------
# # # def get_nakshatra(longitude: float) -> Tuple[str, int]:
# # #     total = longitude % 360
# # #     nak_index = int(total // (360 / 27))
# # #     pada = int((total % (360 / 27)) // (360 / 108)) + 1
# # #     return NAKSHATRAS[nak_index], pada

# # # # ---------------------------------------------------------
# # # # Planetary Avastha (State)
# # # # ---------------------------------------------------------
# # # def get_planetary_avastha(planet_name: str, longitude: float, is_retrograde: bool) -> str:
# # #     """Determine planetary state based on position and motion"""
# # #     degree = longitude % 30
    
# # #     if is_retrograde:
# # #         return "Vriddha"  # Old state for retrograde
    
# # #     if degree <= 5:
# # #         return "Bala"  # Childhood
# # #     elif degree <= 10:
# # #         return "Kumara"  # Youth
# # #     elif degree <= 18:
# # #         return "Yuva"  # Young adult
# # #     elif degree <= 25:
# # #         return "Vriddha"  # Old
# # #     else:
# # #         return "Mrita"  # Dead

# # # # ---------------------------------------------------------
# # # # Planetary Relationship Status
# # # # ---------------------------------------------------------
# # # def get_planetary_status(planet_name: str, sign_lord: str) -> str:
# # #     """Determine if planet is friendly, enemy or neutral in current sign"""
# # #     if planet_name not in PLANETARY_RELATIONSHIPS:
# # #         return "Neutral"
    
# # #     relationships = PLANETARY_RELATIONSHIPS[planet_name]
    
# # #     if sign_lord in relationships['friend']:
# # #         return "Friendly"
# # #     elif sign_lord in relationships['enemy']:
# # #         return "Enemy"
# # #     else:
# # #         return "Neutral"

# # # # ---------------------------------------------------------
# # # # Check Combust
# # # # ---------------------------------------------------------
# # # def is_combust(planet_name: str, planet_long: float, sun_long: float) -> bool:
# # #     """Check if planet is combust (too close to Sun)"""
# # #     if planet_name in ['Sun', 'Moon']:
# # #         return False
    
# # #     distance = abs((planet_long - sun_long) % 360)
# # #     return distance <= 8  # Within 8 degrees of Sun

# # # # ---------------------------------------------------------
# # # # FIXED HOUSE MAPPING FUNCTION
# # # # ---------------------------------------------------------
# # # def find_house(lon_deg, cusps):
# # #     lon_deg = lon_deg % 360
# # #     for i in range(12):
# # #         start = cusps[i] % 360
# # #         end = cusps[(i + 1) % 12] % 360

# # #         if start < end:
# # #             if start <= lon_deg < end:
# # #                 return i + 1
# # #         else:
# # #             # wrap-around case
# # #             if lon_deg >= start or lon_deg < end:
# # #                 return i + 1

# # #     return 12

# # # # ---------------------------------------------------------
# # # # Aspect Calculation
# # # # ---------------------------------------------------------
# # # def get_aspects(planets: Dict[str, Planet]):
# # #     aspects = []
# # #     aspect_types = {
# # #         "Conjunction": 0,
# # #         "Sextile": 60,
# # #         "Square": 90,
# # #         "Trine": 120,
# # #         "Opposition": 180
# # #     }

# # #     names = list(planets.keys())

# # #     for i in range(len(names)):
# # #         for j in range(i + 1, len(names)):
# # #             p1 = planets[names[i]]
# # #             p2 = planets[names[j]]

# # #             diff = abs((p1.longitude - p2.longitude) % 360)

# # #             for asp_name, asp_angle in aspect_types.items():
# # #                 if abs(diff - asp_angle) <= 5:
# # #                     aspects.append(
# # #                         Aspect(
# # #                             between=[p1.name, p2.name],
# # #                             type=asp_name,
# # #                             angle=round(diff, 2)
# # #                         )
# # #                     )
# # #     return aspects

# # # # ---------------------------------------------------------
# # # # Convert degrees to degrees, minutes, seconds
# # # # ---------------------------------------------------------
# # # def deg_to_dms(deg: float) -> str:
# # #     degrees = int(deg)
# # #     minutes_decimal = (deg - degrees) * 60
# # #     minutes = int(minutes_decimal)
# # #     seconds = round((minutes_decimal - minutes) * 60)
    
# # #     return f"{degrees}°{minutes}'{seconds}\""

# # # # ---------------------------------------------------------
# # # # Vimshottari Dasha Calculation (Simplified)
# # # # ---------------------------------------------------------
# # # def calculate_vimshottari_dasha(moon_longitude: float, birth_date: datetime) -> List[Dict]:
# # #     """Calculate Vimshottari Dasha periods"""
# # #     # Find starting dasha based on Moon's nakshatra
# # #     nak_index = int((moon_longitude % 360) // (360 / 27))
    
# # #     # Dasha order and years
# # #     dasha_order = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
# # #     dasha_years = [7, 20, 6, 10, 7, 18, 16, 19, 17]
    
# # #     # Start from current nakshatra's lord
# # #     nak_lord = NAKSHATRA_LORDS[NAKSHATRAS[nak_index]]
    
# # #     # Find starting point in dasha order
# # #     start_index = dasha_order.index(nak_lord)
    
# # #     dashas = []
# # #     current_date = birth_date
    
# # #     # Calculate major periods
# # #     for i in range(9):
# # #         planet_index = (start_index + i) % 9
# # #         planet = dasha_order[planet_index]
# # #         years = dasha_years[planet_index]
        
# # #         end_date = current_date.replace(year=current_date.year + years)
        
# # #         dashas.append({
# # #             'planet': planet,
# # #             'start_date': current_date.strftime("%d-%b-%Y"),
# # #             'end_date': end_date.strftime("%d-%b-%Y"),
# # #             'type': 'Mahadasha'
# # #         })
        
# # #         current_date = end_date
    
# # #     return dashas

# # # # ---------------------------------------------------------
# # # # UPDATED MAIN KUNDLI ENGINE - AstroTalk Style
# # # # ---------------------------------------------------------
# # # def compute_kundli(birth_date: str, birth_time: str, place: str, gender: str) -> KundliChart:
# # #     try:
# # #         lat, lon, tz = geocode_place(place)
# # #         dt = parse_birth_datetime(birth_date, birth_time)
# # #         jd_ut = datetime_to_jd(dt, tz)

# # #         # Set ephemeris path (important for accurate calculations)
# # #         swe.set_ephe_path()

# # #         # Houses
# # #         cusps, asc_mc = swe.houses(jd_ut, lat, lon, b'P')  # Placidus house system

# # #         houses: Dict[int, House] = {}
# # #         for i in range(12):
# # #             cusp = cusps[i] % 360
# # #             houses[i+1] = House(
# # #                 number=i+1,
# # #                 longitude=cusp,
# # #                 sign=SIGNS[int(cusp // 30)],
# # #                 degree=round(cusp % 30, 2)
# # #             )

# # #         # Get Sun longitude for combustion calculation
# # #         sun_data, _ = swe.calc_ut(jd_ut, swe.SUN)
# # #         sun_long = sun_data[0]

# # #         # Planets with enhanced data
# # #         planets: Dict[str, Planet] = {}
# # #         for name, pid in PLANETS.items():
# # #             xx, ret = swe.calc_ut(jd_ut, pid)
# # #             lon_deg = xx[0]
# # #             sign_index = int(lon_deg // 30)
# # #             sign = SIGNS[sign_index]
# # #             nakshatra, pada = get_nakshatra(lon_deg)
            
# # #             planet_house = find_house(lon_deg, cusps)
# # #             is_retro = xx[3] < 0
# # #             is_combust_planet = is_combust(name, lon_deg, sun_long)
# # #             avastha = get_planetary_avastha(name, lon_deg, is_retro)
# # #             status = get_planetary_status(name, SIGN_LORDS[sign])

# # #             # Enhanced planet data
# # #             planets[name] = Planet(
# # #                 name=name,
# # #                 longitude=round(lon_deg, 2),
# # #                 sign=sign,
# # #                 sign_lord=SIGN_LORDS[sign],
# # #                 degree=round(lon_deg % 30, 2),
# # #                 retrograde=is_retro,
# # #                 nakshatra=nakshatra,
# # #                 nakshatra_lord=NAKSHATRA_LORDS[nakshatra],
# # #                 pada=pada,
# # #                 house=planet_house,
# # #                 combust=is_combust_planet,
# # #                 avastha=avastha,
# # #                 status=status,
# # #                 dms=deg_to_dms(lon_deg % 30)  # Degree-minute-second format
# # #             )

# # #         # Aspects
# # #         aspects = get_aspects(planets)

# # #         # Vimshottari Dasha
# # #         vimshottari_dasha = calculate_vimshottari_dasha(planets['Moon'].longitude, dt)

# # #         # Ascendant details
# # #         ascendant = cusps[0]
# # #         asc_sign = SIGNS[int(ascendant // 30)]
# # #         asc_nakshatra, asc_pada = get_nakshatra(ascendant)

# # #         return KundliChart(
# # #             place=place,
# # #             timezone=tz,
# # #             julian_day=jd_ut,
# # #             ascendant=round(ascendant, 2),
# # #             ascendant_sign=asc_sign,
# # #             ascendant_sign_lord=SIGN_LORDS[asc_sign],
# # #             ascendant_nakshatra=asc_nakshatra,
# # #             ascendant_nakshatra_lord=NAKSHATRA_LORDS[asc_nakshatra],
# # #             mc=round(asc_mc[1], 2),
# # #             planets=planets,
# # #             houses=houses,
# # #             aspects=aspects,
# # #             vimshottari_dasha=vimshottari_dasha,
# # #             gender=gender
# # #         )

# # #     except Exception as e:
# # #         logging.error(f"Error computing kundli: {e}")
# # #         raise ValueError(f"Error computing kundli: {e}")







# # from datetime import datetime
# # import swisseph as swe
# # import pytz
# # import time
# # from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
# # from timezonefinderL import TimezoneFinder
# # from geopy.geocoders import Nominatim
# # import logging
# # from typing import Dict, List, Tuple
# # from src.models.kundli_model import KundliChart, Planet, House, Aspect, DashaPeriod

# # # Init helpers
# # geolocator = Nominatim(user_agent="kundli_backend")
# # tzfinder = TimezoneFinder(in_memory=True)

# # PLANETS = {
# #     'Sun': swe.SUN,
# #     'Moon': swe.MOON,
# #     'Mercury': swe.MERCURY,
# #     'Venus': swe.VENUS,
# #     'Mars': swe.MARS,
# #     'Jupiter': swe.JUPITER,
# #     'Saturn': swe.SATURN,
# #     'Uranus': swe.URANUS,
# #     'Neptune': swe.NEPTUNE,
# #     'Pluto': swe.PLUTO,
# #     'TrueNode': swe.TRUE_NODE,
# #     'Rahu': swe.MEAN_NODE,
# # }

# # SIGNS = [
# #     'Aries','Taurus','Gemini','Cancer','Leo','Virgo',
# #     'Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'
# # ]

# # SIGN_LORDS = {
# #     'Aries': 'Mars',
# #     'Taurus': 'Venus', 
# #     'Gemini': 'Mercury',
# #     'Cancer': 'Moon',
# #     'Leo': 'Sun',
# #     'Virgo': 'Mercury',
# #     'Libra': 'Venus',
# #     'Scorpio': 'Mars',
# #     'Sagittarius': 'Jupiter',
# #     'Capricorn': 'Saturn',
# #     'Aquarius': 'Saturn',
# #     'Pisces': 'Jupiter'
# # }

# # NAKSHATRAS = [
# #     "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
# #     "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
# #     "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
# #     "Vishakha", "Anuradha", "Jyeshta", "Moola", "Purva Ashadha",
# #     "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
# #     "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
# # ]

# # NAKSHATRA_LORDS = {
# #     "Ashwini": "Ketu", "Bharani": "Venus", "Krittika": "Sun", 
# #     "Rohini": "Moon", "Mrigashira": "Mars", "Ardra": "Rahu",
# #     "Punarvasu": "Jupiter", "Pushya": "Saturn", "Ashlesha": "Mercury",
# #     "Magha": "Ketu", "Purva Phalguni": "Venus", "Uttara Phalguni": "Sun",
# #     "Hasta": "Moon", "Chitra": "Mars", "Swati": "Rahu",
# #     "Vishakha": "Jupiter", "Anuradha": "Saturn", "Jyeshta": "Mercury",
# #     "Moola": "Ketu", "Purva Ashadha": "Venus", "Uttara Ashadha": "Sun",
# #     "Shravana": "Moon", "Dhanishta": "Mars", "Shatabhisha": "Rahu",
# #     "Purva Bhadrapada": "Jupiter", "Uttara Bhadrapada": "Saturn", "Revati": "Mercury"
# # }

# # PLANETARY_RELATIONSHIPS = {
# #     'Sun': {'friend': ['Moon', 'Mars', 'Jupiter'], 'enemy': ['Venus', 'Saturn'], 'neutral': ['Mercury']},
# #     'Moon': {'friend': ['Sun', 'Mercury'], 'enemy': [], 'neutral': ['Mars', 'Venus', 'Jupiter', 'Saturn']},
# #     'Mars': {'friend': ['Sun', 'Moon', 'Jupiter'], 'enemy': ['Mercury'], 'neutral': ['Venus', 'Saturn']},
# #     'Mercury': {'friend': ['Sun', 'Venus'], 'enemy': ['Moon'], 'neutral': ['Mars', 'Jupiter', 'Saturn']},
# #     'Jupiter': {'friend': ['Sun', 'Moon', 'Mars'], 'enemy': ['Mercury', 'Venus'], 'neutral': ['Saturn']},
# #     'Venus': {'friend': ['Mercury', 'Saturn'], 'enemy': ['Sun', 'Moon'], 'neutral': ['Mars', 'Jupiter']},
# #     'Saturn': {'friend': ['Mercury', 'Venus'], 'enemy': ['Sun', 'Moon', 'Mars'], 'neutral': ['Jupiter']}
# # }

# # def geocode_place(place: str):
# #     for attempt in range(2):
# #         try:
# #             loc = geolocator.geocode(place, timeout=5)
# #             if not loc:
# #                 raise ValueError(f"Could not geocode place: {place}")

# #             lat, lon = loc.latitude, loc.longitude
# #             tz = tzfinder.timezone_at(lat=lat, lng=lon)

# #             if tz is None:
# #                 tz = "Asia/Kolkata"

# #             return lat, lon, tz

# #         except (GeocoderTimedOut, GeocoderUnavailable):
# #             if attempt == 0:
# #                 time.sleep(1)
# #             else:
# #                 raise

# # def parse_birth_datetime(birth_date: str, birth_time: str) -> datetime:
# #     try:
# #         return datetime.fromisoformat(f"{birth_date}T{birth_time}")
# #     except Exception:
# #         pass

# #     try:
# #         dt = datetime.strptime(f"{birth_date} {birth_time}", "%d-%m-%Y %H:%M")
# #         return dt
# #     except Exception:
# #         raise ValueError("Invalid date/time format. Use YYYY-MM-DD + HH:MM or DD-MM-YYYY + HH:MM")

# # def datetime_to_jd(dt: datetime, tz: str) -> float:
# #     tz_obj = pytz.timezone(tz)
# #     dt_local = tz_obj.localize(dt)
# #     dt_utc = dt_local.astimezone(pytz.UTC)

# #     year, month, day = dt_utc.year, dt_utc.month, dt_utc.day
# #     hour = dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600

# #     return swe.julday(year, month, day, hour)

# # def get_nakshatra(longitude: float) -> Tuple[str, int]:
# #     total = longitude % 360
# #     nak_index = int(total // (360 / 27))
# #     pada = int((total % (360 / 27)) // (360 / 108)) + 1
# #     return NAKSHATRAS[nak_index], pada

# # def get_planetary_avastha(planet_name: str, longitude: float, is_retrograde: bool) -> str:
# #     degree = longitude % 30
    
# #     if is_retrograde:
# #         return "Vriddha"
    
# #     if degree <= 5:
# #         return "Bala"
# #     elif degree <= 10:
# #         return "Kumara"
# #     elif degree <= 18:
# #         return "Yuva"
# #     elif degree <= 25:
# #         return "Vriddha"
# #     else:
# #         return "Mrita"

# # def get_planetary_status(planet_name: str, sign_lord: str) -> str:
# #     if planet_name not in PLANETARY_RELATIONSHIPS:
# #         return "Neutral"
    
# #     relationships = PLANETARY_RELATIONSHIPS[planet_name]
    
# #     if sign_lord in relationships['friend']:
# #         return "Friendly"
# #     elif sign_lord in relationships['enemy']:
# #         return "Enemy"
# #     else:
# #         return "Neutral"

# # def is_combust(planet_name: str, planet_long: float, sun_long: float) -> bool:
# #     if planet_name in ['Sun', 'Moon']:
# #         return False
    
# #     distance = abs((planet_long - sun_long) % 360)
# #     return distance <= 8

# # def find_house(lon_deg, cusps):
# #     lon_deg = lon_deg % 360
# #     for i in range(12):
# #         start = cusps[i] % 360
# #         end = cusps[(i + 1) % 12] % 360

# #         if start < end:
# #             if start <= lon_deg < end:
# #                 return i + 1
# #         else:
# #             if lon_deg >= start or lon_deg < end:
# #                 return i + 1
# #     return 12

# # def get_aspects(planets: Dict[str, Planet]):
# #     aspects = []
# #     aspect_types = {
# #         "Conjunction": 0,
# #         "Sextile": 60,
# #         "Square": 90,
# #         "Trine": 120,
# #         "Opposition": 180
# #     }

# #     names = list(planets.keys())

# #     for i in range(len(names)):
# #         for j in range(i + 1, len(names)):
# #             p1 = planets[names[i]]
# #             p2 = planets[names[j]]

# #             diff = abs((p1.longitude - p2.longitude) % 360)

# #             for asp_name, asp_angle in aspect_types.items():
# #                 if abs(diff - asp_angle) <= 5:
# #                     aspects.append(
# #                         Aspect(
# #                             between=[p1.name, p2.name],
# #                             type=asp_name,
# #                             angle=round(diff, 2)
# #                         )
# #                     )
# #     return aspects

# # def deg_to_dms(deg: float) -> str:
# #     degrees = int(deg)
# #     minutes_decimal = (deg - degrees) * 60
# #     minutes = int(minutes_decimal)
# #     seconds = round((minutes_decimal - minutes) * 60)
    
# #     return f"{degrees}°{minutes}'{seconds}\""

# # def calculate_vimshottari_dasha(moon_longitude: float, birth_date: datetime) -> List[DashaPeriod]:
# #     nak_index = int((moon_longitude % 360) // (360 / 27))
    
# #     dasha_order = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
# #     dasha_years = [7, 20, 6, 10, 7, 18, 16, 19, 17]
    
# #     nak_lord = NAKSHATRA_LORDS[NAKSHATRAS[nak_index]]
# #     start_index = dasha_order.index(nak_lord)
    
# #     dashas = []
# #     current_date = birth_date
    
# #     for i in range(9):
# #         planet_index = (start_index + i) % 9
# #         planet = dasha_order[planet_index]
# #         years = dasha_years[planet_index]
        
# #         end_date = current_date.replace(year=current_date.year + years)
        
# #         dashas.append(DashaPeriod(
# #             planet=planet,
# #             start_date=current_date.strftime("%d-%b-%Y"),
# #             end_date=end_date.strftime("%d-%b-%Y"),
# #             type='Mahadasha'
# #         ))
        
# #         current_date = end_date
    
# #     return dashas

# # def compute_kundli(birth_date: str, birth_time: str, place: str, gender: str) -> KundliChart:
# #     try:
# #         lat, lon, tz = geocode_place(place)
# #         dt = parse_birth_datetime(birth_date, birth_time)
# #         jd_ut = datetime_to_jd(dt, tz)

# #         swe.set_ephe_path()

# #         cusps, asc_mc = swe.houses(jd_ut, lat, lon, b'P')

# #         houses: Dict[int, House] = {}
# #         for i in range(12):
# #             cusp = cusps[i] % 360
# #             houses[i+1] = House(
# #                 number=i+1,
# #                 longitude=cusp,
# #                 sign=SIGNS[int(cusp // 30)],
# #                 degree=round(cusp % 30, 2)
# #             )

# #         sun_data, _ = swe.calc_ut(jd_ut, swe.SUN)
# #         sun_long = sun_data[0]

# #         planets: Dict[str, Planet] = {}
# #         for name, pid in PLANETS.items():
# #             xx, ret = swe.calc_ut(jd_ut, pid)
# #             lon_deg = xx[0]
# #             sign_index = int(lon_deg // 30)
# #             sign = SIGNS[sign_index]
# #             nakshatra, pada = get_nakshatra(lon_deg)
            
# #             planet_house = find_house(lon_deg, cusps)
# #             is_retro = xx[3] < 0
# #             is_combust_planet = is_combust(name, lon_deg, sun_long)
# #             avastha = get_planetary_avastha(name, lon_deg, is_retro)
# #             status = get_planetary_status(name, SIGN_LORDS[sign])

# #             planets[name] = Planet(
# #                 name=name,
# #                 longitude=round(lon_deg, 2),
# #                 sign=sign,
# #                 sign_lord=SIGN_LORDS[sign],
# #                 degree=round(lon_deg % 30, 2),
# #                 retrograde=is_retro,
# #                 house=planet_house,
# #                 nakshatra=nakshatra,
# #                 nakshatra_lord=NAKSHATRA_LORDS[nakshatra],
# #                 pada=pada,
# #                 combust=is_combust_planet,
# #                 avastha=avastha,
# #                 status=status,
# #                 dms=deg_to_dms(lon_deg % 30)
# #             )

# #         aspects = get_aspects(planets)
# #         vimshottari_dasha = calculate_vimshottari_dasha(planets['Moon'].longitude, dt)

# #         ascendant = cusps[0]
# #         asc_sign = SIGNS[int(ascendant // 30)]
# #         asc_nakshatra, asc_pada = get_nakshatra(ascendant)

# #         return KundliChart(
# #             place=place,
# #             timezone=tz,
# #             julian_day=jd_ut,
# #             ascendant=round(ascendant, 2),
# #             ascendant_sign=asc_sign,
# #             ascendant_sign_lord=SIGN_LORDS[asc_sign],
# #             ascendant_nakshatra=asc_nakshatra,
# #             ascendant_nakshatra_lord=NAKSHATRA_LORDS[asc_nakshatra],
# #             mc=round(asc_mc[1], 2),
# #             planets=planets,
# #             houses=houses,
# #             aspects=aspects,
# #             vimshottari_dasha=vimshottari_dasha
# #         )

# #     except Exception as e:
# #         logging.error(f"Error computing kundli: {e}")
# #         raise ValueError(f"Error computing kundli: {e}")



# from datetime import datetime
# import swisseph as swe
# import pytz
# import time
# from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
# from timezonefinderL import TimezoneFinder
# from geopy.geocoders import Nominatim
# import logging
# from typing import Dict, List, Tuple
# from src.models.kundli_model import KundliChart, Planet, House, Aspect, DashaPeriod

# # Init helpers
# geolocator = Nominatim(user_agent="kundli_backend")
# tzfinder = TimezoneFinder(in_memory=True)

# PLANETS = {
#     'Sun': swe.SUN,
#     'Moon': swe.MOON,
#     'Mercury': swe.MERCURY,
#     'Venus': swe.VENUS,
#     'Mars': swe.MARS,
#     'Jupiter': swe.JUPITER,
#     'Saturn': swe.SATURN,
#     'Uranus': swe.URANUS,
#     'Neptune': swe.NEPTUNE,
#     'Pluto': swe.PLUTO,
#     'TrueNode': swe.TRUE_NODE,
#     'Rahu': swe.MEAN_NODE,
#     'Ketu': swe.MEAN_NODE,  # Ketu is opposite to Rahu
# }

# SIGNS = [
#     'Aries','Taurus','Gemini','Cancer','Leo','Virgo',
#     'Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'
# ]

# SIGN_LORDS = {
#     'Aries': 'Mars',
#     'Taurus': 'Venus', 
#     'Gemini': 'Mercury',
#     'Cancer': 'Moon',
#     'Leo': 'Sun',
#     'Virgo': 'Mercury',
#     'Libra': 'Venus',
#     'Scorpio': 'Mars',
#     'Sagittarius': 'Jupiter',
#     'Capricorn': 'Saturn',
#     'Aquarius': 'Saturn',
#     'Pisces': 'Jupiter'
# }

# NAKSHATRAS = [
#     "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
#     "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
#     "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
#     "Vishakha", "Anuradha", "Jyeshta", "Moola", "Purva Ashadha",
#     "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
#     "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
# ]

# NAKSHATRA_LORDS = {
#     "Ashwini": "Ketu", "Bharani": "Venus", "Krittika": "Sun", 
#     "Rohini": "Moon", "Mrigashira": "Mars", "Ardra": "Rahu",
#     "Punarvasu": "Jupiter", "Pushya": "Saturn", "Ashlesha": "Mercury",
#     "Magha": "Ketu", "Purva Phalguni": "Venus", "Uttara Phalguni": "Sun",
#     "Hasta": "Moon", "Chitra": "Mars", "Swati": "Rahu",
#     "Vishakha": "Jupiter", "Anuradha": "Saturn", "Jyeshta": "Mercury",
#     "Moola": "Ketu", "Purva Ashadha": "Venus", "Uttara Ashadha": "Sun",
#     "Shravana": "Moon", "Dhanishta": "Mars", "Shatabhisha": "Rahu",
#     "Purva Bhadrapada": "Jupiter", "Uttara Bhadrapada": "Saturn", "Revati": "Mercury"
# }

# PLANETARY_RELATIONSHIPS = {
#     'Sun': {'friend': ['Moon', 'Mars', 'Jupiter'], 'enemy': ['Venus', 'Saturn'], 'neutral': ['Mercury']},
#     'Moon': {'friend': ['Sun', 'Mercury'], 'enemy': [], 'neutral': ['Mars', 'Venus', 'Jupiter', 'Saturn']},
#     'Mars': {'friend': ['Sun', 'Moon', 'Jupiter'], 'enemy': ['Mercury'], 'neutral': ['Venus', 'Saturn']},
#     'Mercury': {'friend': ['Sun', 'Venus'], 'enemy': ['Moon'], 'neutral': ['Mars', 'Jupiter', 'Saturn']},
#     'Jupiter': {'friend': ['Sun', 'Moon', 'Mars'], 'enemy': ['Mercury', 'Venus'], 'neutral': ['Saturn']},
#     'Venus': {'friend': ['Mercury', 'Saturn'], 'enemy': ['Sun', 'Moon'], 'neutral': ['Mars', 'Jupiter']},
#     'Saturn': {'friend': ['Mercury', 'Venus'], 'enemy': ['Sun', 'Moon', 'Mars'], 'neutral': ['Jupiter']}
# }

# def geocode_place(place: str):
#     for attempt in range(2):
#         try:
#             loc = geolocator.geocode(place, timeout=5)
#             if not loc:
#                 raise ValueError(f"Could not geocode place: {place}")

#             lat, lon = loc.latitude, loc.longitude
#             tz = tzfinder.timezone_at(lat=lat, lng=lon)

#             if tz is None:
#                 tz = "Asia/Kolkata"

#             return lat, lon, tz

#         except (GeocoderTimedOut, GeocoderUnavailable):
#             if attempt == 0:
#                 time.sleep(1)
#             else:
#                 raise

# def parse_birth_datetime(birth_date: str, birth_time: str) -> datetime:
#     try:
#         return datetime.fromisoformat(f"{birth_date}T{birth_time}")
#     except Exception:
#         pass

#     try:
#         dt = datetime.strptime(f"{birth_date} {birth_time}", "%d-%m-%Y %H:%M")
#         return dt
#     except Exception:
#         raise ValueError("Invalid date/time format. Use YYYY-MM-DD + HH:MM or DD-MM-YYYY + HH:MM")

# def datetime_to_jd(dt: datetime, tz: str) -> float:
#     tz_obj = pytz.timezone(tz)
#     dt_local = tz_obj.localize(dt)
#     dt_utc = dt_local.astimezone(pytz.UTC)

#     year, month, day = dt_utc.year, dt_utc.month, dt_utc.day
#     hour = dt_utc.hour + dt_utc.minute / 60 + dt_utc.second / 3600

#     return swe.julday(year, month, day, hour)

# def get_nakshatra(longitude: float) -> Tuple[str, int]:
#     total = longitude % 360
#     nak_index = int(total // (360 / 27))
#     pada = int((total % (360 / 27)) // (360 / 108)) + 1
#     return NAKSHATRAS[nak_index], pada

# def get_planetary_avastha(planet_name: str, longitude: float, is_retrograde: bool) -> str:
#     degree = longitude % 30
    
#     if is_retrograde:
#         return "Vriddha"
    
#     if degree <= 5:
#         return "Bala"
#     elif degree <= 10:
#         return "Kumara"
#     elif degree <= 18:
#         return "Yuva"
#     elif degree <= 25:
#         return "Vriddha"
#     else:
#         return "Mrita"

# def get_planetary_status(planet_name: str, sign_lord: str) -> str:
#     if planet_name not in PLANETARY_RELATIONSHIPS:
#         return "Neutral"
    
#     relationships = PLANETARY_RELATIONSHIPS[planet_name]
    
#     if sign_lord in relationships['friend']:
#         return "Friendly"
#     elif sign_lord in relationships['enemy']:
#         return "Enemy"
#     else:
#         return "Neutral"

# def is_combust(planet_name: str, planet_long: float, sun_long: float) -> bool:
#     if planet_name in ['Sun', 'Moon', 'Rahu', 'Ketu']:
#         return False
    
#     distance = abs((planet_long - sun_long) % 360)
#     # Different planets have different combustion distances
#     combustion_limits = {
#         'Mercury': 14,
#         'Venus': 10,
#         'Mars': 17,
#         'Jupiter': 11,
#         'Saturn': 15,
#         'Uranus': 8,
#         'Neptune': 8,
#         'Pluto': 8
#     }
#     limit = combustion_limits.get(planet_name, 8)
#     return distance <= limit

# def find_house(lon_deg, cusps):
#     lon_deg = lon_deg % 360
#     for i in range(12):
#         start = cusps[i] % 360
#         end = cusps[(i + 1) % 12] % 360

#         if start < end:
#             if start <= lon_deg < end:
#                 return i + 1
#         else:
#             if lon_deg >= start or lon_deg < end:
#                 return i + 1
#     return 12

# def get_aspects(planets: Dict[str, Planet]):
#     aspects = []
#     aspect_types = {
#         "Conjunction": 0,
#         "Sextile": 60,
#         "Square": 90,
#         "Trine": 120,
#         "Opposition": 180
#     }

#     names = list(planets.keys())

#     for i in range(len(names)):
#         for j in range(i + 1, len(names)):
#             p1 = planets[names[i]]
#             p2 = planets[names[j]]

#             diff = abs((p1.longitude - p2.longitude) % 360)

#             for asp_name, asp_angle in aspect_types.items():
#                 if abs(diff - asp_angle) <= 5:
#                     aspects.append(
#                         Aspect(
#                             between=[p1.name, p2.name],
#                             type=asp_name,
#                             angle=round(diff, 2)
#                         )
#                     )
#     return aspects

# def deg_to_dms(deg: float) -> str:
#     degrees = int(deg)
#     minutes_decimal = (deg - degrees) * 60
#     minutes = int(minutes_decimal)
#     seconds = round((minutes_decimal - minutes) * 60)
    
#     return f"{degrees}°{minutes}'{seconds}\""

# def calculate_vimshottari_dasha(moon_longitude: float, birth_date: datetime) -> List[DashaPeriod]:
#     nak_index = int((moon_longitude % 360) // (360 / 27))
    
#     dasha_order = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
#     dasha_years = [7, 20, 6, 10, 7, 18, 16, 19, 17]
    
#     nak_lord = NAKSHATRA_LORDS[NAKSHATRAS[nak_index]]
#     start_index = dasha_order.index(nak_lord)
    
#     dashas = []
#     current_date = birth_date
    
#     for i in range(9):
#         planet_index = (start_index + i) % 9
#         planet = dasha_order[planet_index]
#         years = dasha_years[planet_index]
        
#         end_date = current_date.replace(year=current_date.year + years)
        
#         dashas.append(DashaPeriod(
#             planet=planet,
#             start_date=current_date.strftime("%d-%b-%Y"),
#             end_date=end_date.strftime("%d-%b-%Y"),
#             type='Mahadasha'
#         ))
        
#         current_date = end_date
    
#     return dashas

# def format_planet_table(planets: Dict[str, Planet], ascendant_deg: float) -> str:
#     """Format planets in AstroTalk table style"""
#     table_lines = []
#     headers = ["Planet", "Sign", "Sign Lord", "Nakshatra", "Naksh Lord", "Degree", "Retro(R)", "Combust", "Avastha", "House", "Status"]
    
#     # Add Ascendant row
#     asc_sign = SIGNS[int(ascendant_deg // 30)]
#     asc_nakshatra, asc_pada = get_nakshatra(ascendant_deg)
    
#     table_lines.append(f"{'':<12} {'':<12} {'':<12} {'':<12} {'':<12} {'Degree':<15} {'':<10} {'':<8} {'':<8} {'':<6} {'':<8}")
#     table_lines.append(f"{'Ascendant':<12} {asc_sign:<12} {SIGN_LORDS[asc_sign]:<12} {asc_nakshatra:<12} {NAKSHATRA_LORDS[asc_nakshatra]:<12} {deg_to_dms(ascendant_deg % 30):<15} {'Direct':<10} {'No':<8} {'--':<8} {'1':<6} {'--':<8}")
    
#     # Add planet rows
#     for planet_name in ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Rahu', 'Ketu', 'Uranus', 'Neptune', 'Pluto']:
#         if planet_name in planets:
#             p = planets[planet_name]
#             retro_status = "Retro" if p.retrograde else "Direct"
#             combust_status = "Yes" if p.combust else "No"
            
#             table_lines.append(
#                 f"{p.name:<12} {p.sign:<12} {p.sign_lord:<12} {p.nakshatra:<12} {p.nakshatra_lord:<12} {p.dms:<15} {retro_status:<10} {combust_status:<8} {p.avastha:<8} {p.house:<6} {p.status:<8}"
#             )
    
#     return "\n".join(table_lines)

# def generate_astrotalk_report(kundli: KundliChart, name: str, birth_date: str, birth_time: str, gender: str) -> Dict:
#     """Generate complete AstroTalk style report"""
    
#     report = {
#         "chart_types": ["North Indian", "South Indian", "Lagna / Ascendant / Basic Birth Chart", "Navamsa"],
#         "planet_table": format_planet_table(kundli.planets, kundli.ascendant),
#         "vimshottari_dasha": {
#             "periods": kundli.vimshottari_dasha,
#             "current_dasha": kundli.vimshottari_dasha[0] if kundli.vimshottari_dasha else None
#         },
#         "key_yogas": find_planetary_yogas(kundli.planets, kundli.houses),
#         "summary": generate_chart_summary(kundli, name, gender)
#     }
    
#     return report

# def find_planetary_yogas(planets: Dict[str, Planet], houses: Dict[int, House]) -> List[str]:
#     """Find important planetary yogas"""
#     yogas = []
    
#     # Check for Raj Yoga (planets in Kendras and Trikonas)
#     kendra_houses = [1, 4, 7, 10]
#     trikona_houses = [1, 5, 9]
    
#     for planet_name, planet in planets.items():
#         if planet.house in kendra_houses:
#             # Check if there are planets in trikona from this planet
#             for other_planet_name, other_planet in planets.items():
#                 if other_planet_name != planet_name and other_planet.house in trikona_houses:
#                     yogas.append(f"Raj Yoga potential between {planet_name} and {other_planet_name}")
    
#     # Check for Dhana Yoga (planets in 2nd, 5th, 9th, 11th)
#     dhana_houses = [2, 5, 9, 11]
#     dhana_planets = [p for p in planets.values() if p.house in dhana_houses]
#     if len(dhana_planets) >= 2:
#         yogas.append("Dhana Yoga (Wealth) indicated")
    
#     return yogas[:5]  # Return top 5 yogas

# def generate_chart_summary(kundli: KundliChart, name: str, gender: str) -> str:
#     """Generate professional chart summary"""
    
#     asc_sign = kundli.ascendant_sign
#     moon_sign = kundli.planets['Moon'].sign
#     sun_sign = kundli.planets['Sun'].sign
    
#     summary = f"""
# Chart Summary for {name}
# ═══════════════════════════════════════════════════════════════════════════════

# BASIC INFORMATION:
# • Ascendant (Lagna): {asc_sign} ({kundli.ascendant_sign_lord})
# • Moon Sign (Rashi): {moon_sign}
# • Sun Sign: {sun_sign}
# • Birth Star: {kundli.planets['Moon'].nakshatra}

# PROMINENT PLACEMENTS:
# • Sun in {kundli.planets['Sun'].house}th house - Career and public life focus
# • Moon in {kundli.planets['Moon'].house}th house - Emotional nature and home life
# • Jupiter in {kundli.planets['Jupiter'].house}th house - Wisdom and expansion areas

# CURRENT DASHA:
# • {kundli.vimshottari_dasha[0].planet} Mahadasha until {kundli.vimshottari_dasha[0].end_date}

# KEY OBSERVATIONS:
# • Ascendant lord {kundli.ascendant_sign_lord} placement influences personality
# • Planetary aspects indicate relationship dynamics
# • House placements reveal life focus areas
#     """
    
#     return summary

# def compute_kundli(birth_date: str, birth_time: str, place: str, gender: str) -> KundliChart:
#     try:
#         lat, lon, tz = geocode_place(place)
#         dt = parse_birth_datetime(birth_date, birth_time)
#         jd_ut = datetime_to_jd(dt, tz)

#         swe.set_ephe_path()

#         # Use whole sign system for more accurate house calculation
#         cusps, asc_mc = swe.houses(jd_ut, lat, lon, b'P')

#         houses: Dict[int, House] = {}
#         for i in range(12):
#             cusp = cusps[i] % 360
#             houses[i+1] = House(
#                 number=i+1,
#                 longitude=cusp,
#                 sign=SIGNS[int(cusp // 30)],
#                 degree=round(cusp % 30, 2)
#             )

#         sun_data, _ = swe.calc_ut(jd_ut, swe.SUN)
#         sun_long = sun_data[0]

#         planets: Dict[str, Planet] = {}
#         for name, pid in PLANETS.items():
#             xx, ret = swe.calc_ut(jd_ut, pid)
#             lon_deg = xx[0]
            
#             # Handle Rahu/Ketu calculation
#             if name == 'Ketu':
#                 lon_deg = (xx[0] + 180) % 360
            
#             sign_index = int(lon_deg // 30)
#             sign = SIGNS[sign_index]
#             nakshatra, pada = get_nakshatra(lon_deg)
            
#             planet_house = find_house(lon_deg, cusps)
#             is_retro = xx[3] < 0
#             is_combust_planet = is_combust(name, lon_deg, sun_long)
#             avastha = get_planetary_avastha(name, lon_deg, is_retro)
#             status = get_planetary_status(name, SIGN_LORDS[sign])

#             planets[name] = Planet(
#                 name=name,
#                 longitude=round(lon_deg, 2),
#                 sign=sign,
#                 sign_lord=SIGN_LORDS[sign],
#                 degree=round(lon_deg % 30, 2),
#                 retrograde=is_retro,
#                 house=planet_house,
#                 nakshatra=nakshatra,
#                 nakshatra_lord=NAKSHATRA_LORDS[nakshatra],
#                 pada=pada,
#                 combust=is_combust_planet,
#                 avastha=avastha,
#                 status=status,
#                 dms=deg_to_dms(lon_deg % 30)
#             )

#         aspects = get_aspects(planets)
#         vimshottari_dasha = calculate_vimshottari_dasha(planets['Moon'].longitude, dt)

#         ascendant = cusps[0]
#         asc_sign = SIGNS[int(ascendant // 30)]
#         asc_nakshatra, asc_pada = get_nakshatra(ascendant)

#         return KundliChart(
#             place=place,
#             timezone=tz,
#             julian_day=jd_ut,
#             ascendant=round(ascendant, 2),
#             ascendant_sign=asc_sign,
#             ascendant_sign_lord=SIGN_LORDS[asc_sign],
#             ascendant_nakshatra=asc_nakshatra,
#             ascendant_nakshatra_lord=NAKSHATRA_LORDS[asc_nakshatra],
#             mc=round(asc_mc[1], 2),
#             planets=planets,
#             houses=houses,
#             aspects=aspects,
#             vimshottari_dasha=vimshottari_dasha
#         )

#     except Exception as e:
#         logging.error(f"Error computing kundli: {e}")
#         raise ValueError(f"Error computing kundli: {e}")

# # New function to generate the complete AstroTalk response
# def generate_astrotalk_response(kundli_request):
#     """Generate complete AstroTalk style response"""
#     kundli = compute_kundli(
#         kundli_request.birth_date,
#         kundli_request.birth_time,
#         kundli_request.place,
#         kundli_request.gender
#     )
    
#     report = generate_astrotalk_report(
#         kundli, 
#         kundli_request.name,
#         kundli_request.birth_date,
#         kundli_request.birth_time,
#         kundli_request.gender
#     )
    
#     return {
#         "name": kundli_request.name,
#         "birth_date": kundli_request.birth_date,
#         "birth_time": kundli_request.birth_time,
#         "place": kundli_request.place,
#         "gender": kundli_request.gender,
#         "chart": kundli.dict(),
#         "astrotalk_report": report
#     }


from datetime import datetime
import swisseph as swe
import pytz
import time
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from timezonefinderL import TimezoneFinder
from geopy.geocoders import Nominatim
import logging
from typing import Dict, List, Tuple
from src.models.kundli_model import KundliChart, Planet, House, Aspect, DashaPeriod


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
    'Rahu': swe.MEAN_NODE,
    'Ketu': swe.MEAN_NODE,  # Ketu is opposite to Rahu
}

SIGNS = [
    'Aries','Taurus','Gemini','Cancer','Leo','Virgo',
    'Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'
]

SIGN_LORDS = {
    'Aries': 'Mars',
    'Taurus': 'Venus', 
    'Gemini': 'Mercury',
    'Cancer': 'Moon',
    'Leo': 'Sun',
    'Virgo': 'Mercury',
    'Libra': 'Venus',
    'Scorpio': 'Mars',
    'Sagittarius': 'Jupiter',
    'Capricorn': 'Saturn',
    'Aquarius': 'Saturn',
    'Pisces': 'Jupiter'
}

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
    "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshta", "Moola", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

NAKSHATRA_LORDS = {
    "Ashwini": "Ketu", "Bharani": "Venus", "Krittika": "Sun", 
    "Rohini": "Moon", "Mrigashira": "Mars", "Ardra": "Rahu",
    "Punarvasu": "Jupiter", "Pushya": "Saturn", "Ashlesha": "Mercury",
    "Magha": "Ketu", "Purva Phalguni": "Venus", "Uttara Phalguni": "Sun",
    "Hasta": "Moon", "Chitra": "Mars", "Swati": "Rahu",
    "Vishakha": "Jupiter", "Anuradha": "Saturn", "Jyeshta": "Mercury",
    "Moola": "Ketu", "Purva Ashadha": "Venus", "Uttara Ashadha": "Sun",
    "Shravana": "Moon", "Dhanishta": "Mars", "Shatabhisha": "Rahu",
    "Purva Bhadrapada": "Jupiter", "Uttara Bhadrapada": "Saturn", "Revati": "Mercury"
}

PLANETARY_RELATIONSHIPS = {
    'Sun': {'friend': ['Moon', 'Mars', 'Jupiter'], 'enemy': ['Venus', 'Saturn'], 'neutral': ['Mercury']},
    'Moon': {'friend': ['Sun', 'Mercury'], 'enemy': [], 'neutral': ['Mars', 'Venus', 'Jupiter', 'Saturn']},
    'Mars': {'friend': ['Sun', 'Moon', 'Jupiter'], 'enemy': ['Mercury'], 'neutral': ['Venus', 'Saturn']},
    'Mercury': {'friend': ['Sun', 'Venus'], 'enemy': ['Moon'], 'neutral': ['Mars', 'Jupiter', 'Saturn']},
    'Jupiter': {'friend': ['Sun', 'Moon', 'Mars'], 'enemy': ['Mercury', 'Venus'], 'neutral': ['Saturn']},
    'Venus': {'friend': ['Mercury', 'Saturn'], 'enemy': ['Sun', 'Moon'], 'neutral': ['Mars', 'Jupiter']},
    'Saturn': {'friend': ['Mercury', 'Venus'], 'enemy': ['Sun', 'Moon', 'Mars'], 'neutral': ['Jupiter']}
}




def geocode_place(place: str):
    """Enhanced geocoding with better accuracy for Kundli calculations"""
    for attempt in range(3):  # Try 3 times for reliability
        try:
            loc = geolocator.geocode(place, timeout=10)
            if not loc:
                raise ValueError(f"Could not geocode place: {place}")
            lat, lon = loc.latitude, loc.longitude
            tz = tzfinder.timezone_at(lat=lat, lng=lon)
            
            # Better timezone fallback
            if tz is None:
                if 68 <= lon <= 97:  # India range
                    tz = "Asia/Kolkata"
                else:
                    tz = "UTC"
            
            logging.info(f"Geocoded: {place} -> lat={lat:.4f}, lon={lon:.4f}, tz={tz}")
            return lat, lon, tz
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            if attempt < 2:
                time.sleep(1.5)
            else:
                raise ValueError(f"Unable to locate place: {place}. Try with more details.")
            
            
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
    """Convert datetime to Julian Day with microsecond precision"""
    tz_obj = pytz.timezone(tz)
    
    # Handle both naive and aware datetimes
    if dt.tzinfo is None:
        local_dt = tz_obj.localize(dt)
    else:
        local_dt = dt.astimezone(tz_obj)
    
    utc_dt = local_dt.astimezone(pytz.UTC)
    year, month, day = utc_dt.year, utc_dt.month, utc_dt.day
    # Include microseconds for astronomical precision
    hour = utc_dt.hour + utc_dt.minute / 60 + utc_dt.second / 3600 + utc_dt.microsecond / 3600000000
    return swe.julday(year, month, day, hour)


def get_nakshatra(longitude: float) -> Tuple[str, int]:
    """Return Nakshatra + Pada from longitude"""
    total_degrees = longitude % 360
    nakshatra_index = int(total_degrees // (360 / 27))
    pada = int((total_degrees % (360 / 27)) // (360 / 108)) + 1
    return NAKSHATRAS[nakshatra_index], pada


def get_planetary_avastha(planet_name: str, longitude: float, is_retrograde: bool) -> str:
    """Determine planetary state based on position and motion"""
    degree = longitude % 30
    
    if is_retrograde:
        return "Vriddha"  # Old state for retrograde
    
    if degree <= 5:
        return "Bala"  # Childhood
    elif degree <= 10:
        return "Kumara"  # Youth
    elif degree <= 18:
        return "Yuva"  # Young adult
    elif degree <= 25:
        return "Vriddha"  # Old
    else:
        return "Mrita"  # Dead


def get_planetary_status(planet_name: str, sign_lord: str) -> str:
    """Determine if planet is friendly, enemy or neutral in current sign"""
    if planet_name not in PLANETARY_RELATIONSHIPS:
        return "Neutral"
    
    relationships = PLANETARY_RELATIONSHIPS[planet_name]
    
    if sign_lord in relationships['friend']:
        return "Friendly"
    elif sign_lord in relationships['enemy']:
        return "Enemy"
    else:
        return "Neutral"


def is_combust(planet_name: str, planet_long: float, sun_long: float) -> bool:
    """Check if planet is combust (too close to Sun)"""
    if planet_name in ['Sun', 'Moon', 'Rahu', 'Ketu']:
        return False
    
    distance = abs((planet_long - sun_long) % 360)
    # Different planets have different combustion distances
    combustion_limits = {
        'Mercury': 14,
        'Venus': 10,
        'Mars': 17,
        'Jupiter': 11,
        'Saturn': 15
    }
    limit = combustion_limits.get(planet_name, 8)
    return distance <= limit


def find_house(lon_deg: float, cusps: List[float]) -> int:
    """Fixed house mapping with proper boundary handling"""
    lon_deg = lon_deg % 360
    for i in range(12):
        start = cusps[i] % 360
        end = cusps[(i + 1) % 12] % 360

        if start < end:
            if start <= lon_deg < end:
                return i + 1
        else:
            # wrap-around case
            if lon_deg >= start or lon_deg < end:
                return i + 1
    return 12


def deg_to_dms(deg: float) -> str:
    """Convert degrees to degrees, minutes, seconds"""
    degrees = int(deg)
    minutes_decimal = (deg - degrees) * 60
    minutes = int(minutes_decimal)
    seconds = round((minutes_decimal - minutes) * 60)
    
    return f"{degrees}°{minutes}'{seconds}\""


def calculate_vimshottari_dasha(moon_longitude: float, birth_date: datetime) -> List[DashaPeriod]:
    """Calculate Vimshottari Dasha periods"""
    # Find starting dasha based on Moon's nakshatra
    nak_index = int((moon_longitude % 360) // (360 / 27))
    
    # Dasha order and years
    dasha_order = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
    dasha_years = [7, 20, 6, 10, 7, 18, 16, 19, 17]
    
    # Start from current nakshatra's lord
    nak_lord = NAKSHATRA_LORDS[NAKSHATRAS[nak_index]]
    
    # Find starting point in dasha order
    start_index = dasha_order.index(nak_lord)
    
    dashas = []
    current_date = birth_date
    
    # Calculate major periods
    for i in range(9):
        planet_index = (start_index + i) % 9
        planet = dasha_order[planet_index]
        years = dasha_years[planet_index]
        
        end_date = current_date.replace(year=current_date.year + years)
        
        dashas.append(DashaPeriod(
            planet=planet,
            start_date=current_date.strftime("%d-%b-%Y"),
            end_date=end_date.strftime("%d-%b-%Y"),
            type='Mahadasha'
        ))
        
        current_date = end_date
    
    return dashas


def get_aspects(planets: Dict[str, Planet]) -> List[Aspect]:
    """Calculate Vedic planetary aspects (Drishti/Graha Drishti)"""
    aspects = []
    
    # Vedic astrology aspects based on houses (not degrees like Western)
    # All planets have 7th house aspect (opposition)
    # Mars has 4th and 8th house aspects
    # Jupiter has 5th and 9th house aspects  
    # Saturn has 3rd and 10th house aspects
    
    aspect_types = {
        "Yuti (Conjunction)": 0,  # Same house/sign
        "Saptama Drishti (7th Aspect)": 180,  # Opposition - all planets have this
        "Kendra Drishti (Square Aspect)": 90,  # Beneficial in Vedic
        "Trikona Drishti (Trine Aspect)": 120  # Most beneficial
    }
    
    names = list(planets.keys())
    
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            p1 = planets[names[i]]
            p2 = planets[names[j]]
            
            # Calculate house difference for Vedic aspects
            house_diff = abs(p1.house - p2.house) if p1.house and p2.house else 0
            degree_diff = abs((p1.longitude - p2.longitude) % 360)
            
            # Conjunction (same house or within 10° orb)
            if house_diff == 0 or degree_diff <= 10:
                aspects.append(
                    Aspect(
                        between=[p1.name, p2.name],
                        type="Yuti (Conjunction)",
                        angle=round(degree_diff, 2)
                    )
                )
            # 7th house aspect (opposition) - within 10° orb
            elif abs(degree_diff - 180) <= 10:
                aspects.append(
                    Aspect(
                        between=[p1.name, p2.name],
                        type="Saptama Drishti (7th Aspect)",
                        angle=round(degree_diff, 2)
                    )
                )
            # Trine aspect (120°) - beneficial
            elif abs(degree_diff - 120) <= 8:
                aspects.append(
                    Aspect(
                        between=[p1.name, p2.name],
                        type="Trikona Drishti (Trine)",
                        angle=round(degree_diff, 2)
                    )
                )
            # Square aspect (90°) - in Vedic this is Kendra (beneficial)
            elif abs(degree_diff - 90) <= 8:
                aspects.append(
                    Aspect(
                        between=[p1.name, p2.name],
                        type="Kendra Drishti (Square)",
                        angle=round(degree_diff, 2)
                    )
                )
    
    return aspects


# --------------------------
# Core Computation - Enhanced Vedic Astrology
# --------------------------
def compute_kundli(birth_date: str, birth_time: str, place: str, gender: str) -> KundliChart:
    try:
        lat, lon, tz = geocode_place(place)
        dt = parse_birth_datetime(birth_date, birth_time)
        jd_ut = datetime_to_jd(dt, tz)

        # Set ephemeris path for accurate calculations
        swe.set_ephe_path()
        
        # Set Lahiri Ayanamsa (standard for Vedic astrology)
        # This adjusts for precession of equinoxes - critical for accuracy
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        
        # Calculate ayanamsa value for reference
        ayanamsa = swe.get_ayanamsa_ut(jd_ut)
        logging.info(f"Using Lahiri Ayanamsa: {ayanamsa:.4f}°")

        # Calculate houses using Whole Sign House system (standard in Vedic astrology)
        # In Vedic, each house = one complete sign (30°)
        # 'W' = Whole Sign House system
        cusps, asc_mc = swe.houses(jd_ut, lat, lon, b'W')

        # Vedic houses (Bhavas) - each house is exactly 30° (one complete sign)
        houses: Dict[int, House] = {}
        for i in range(12):
            cusp = cusps[i] % 360
            houses[i+1] = House(
                number=i+1,
                longitude=round(cusp, 2),
                sign=SIGNS[int(cusp // 30)],
                degree=round(cusp % 30, 2)
            )

        # Get Sun longitude for combustion calculation
        sun_data, _ = swe.calc_ut(jd_ut, swe.SUN)
        sun_long = sun_data[0]

        # Calculate planets with TRUE Vedic sidereal positions
        # FLG_SIDEREAL applies Lahiri Ayanamsa correction for 100% Vedic accuracy
        # FLG_SPEED calculates velocity for precise retrograde detection
        planets: Dict[str, Planet] = {}
        for name, pid in PLANETS.items():
            xx, ret = swe.calc_ut(jd_ut, pid, swe.FLG_SIDEREAL | swe.FLG_SPEED)
            lon_deg = xx[0]
            
            # Handle Ketu (opposite to Rahu)
            if name == 'Ketu':
                lon_deg = (xx[0] + 180) % 360
            
            sign_index = int(lon_deg // 30)
            sign = SIGNS[sign_index]
            nakshatra, pada = get_nakshatra(lon_deg)
            
            planet_house = find_house(lon_deg, cusps)
            is_retro = xx[3] < 0
            is_combust_planet = is_combust(name, lon_deg, sun_long)
            avastha = get_planetary_avastha(name, lon_deg, is_retro)
            status = get_planetary_status(name, SIGN_LORDS[sign])

            planets[name] = Planet(
                name=name,
                longitude=round(lon_deg, 2),
                sign=sign,
                sign_lord=SIGN_LORDS[sign],
                degree=round(lon_deg % 30, 2),
                retrograde=is_retro,
                house=planet_house,
                nakshatra=nakshatra,
                nakshatra_lord=NAKSHATRA_LORDS[nakshatra],
                pada=pada,
                combust=is_combust_planet,
                avastha=avastha,
                status=status,
                dms=deg_to_dms(lon_deg % 30)
            )

        # Calculate aspects
        aspects = get_aspects(planets)
        
        # Calculate Vimshottari Dasha
        vimshottari_dasha = calculate_vimshottari_dasha(planets['Moon'].longitude, dt)

        # Ascendant details
        ascendant = cusps[0]
        asc_sign = SIGNS[int(ascendant // 30)]
        asc_nakshatra, asc_pada = get_nakshatra(ascendant)

        return KundliChart(
            place=place,
            timezone=tz,
            julian_day=jd_ut,
            ascendant=round(ascendant, 2),
            ascendant_sign=asc_sign,
            ascendant_sign_lord=SIGN_LORDS[asc_sign],
            ascendant_nakshatra=asc_nakshatra,
            ascendant_nakshatra_lord=NAKSHATRA_LORDS[asc_nakshatra],
            mc=round(asc_mc[1], 2),
            planets=planets,
            houses=houses,
            aspects=aspects,
            vimshottari_dasha=vimshottari_dasha
        )

    except Exception as e:
        logging.error(f"Error computing kundli: {e}")
        raise ValueError(f"Error computing kundli: {e}")