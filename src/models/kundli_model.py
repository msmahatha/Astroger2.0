# from pydantic import BaseModel
# from typing import Dict, List, Optional



# class Planet(BaseModel):
#     name: str
#     longitude: float
#     sign: str
#     degree: float
#     retrograde: bool
#     house: Optional[int]
#     nakshatra: str
#     pada: int

# class House(BaseModel):
#     number: int
#     longitude: float
#     sign: str
#     degree: float

# class Aspect(BaseModel):
#     between: List[str]
#     type: str
#     angle: float

# class KundliChart(BaseModel):
#     place: str
#     timezone: str
#     julian_day: float
#     ascendant: float
#     mc: float
#     planets: Dict[str, Planet]
#     houses: Dict[int, House]
#     aspects: List[Aspect]

# class KundliResponse(BaseModel):
#     name: str
#     birth_date: str  # Use YYYY-MM-DD + HH:MM or DD-MM-YYYY + HH:MM
#     birth_time: str
#     place: str
#     gender: str
#     chart: KundliChart



# class KundliRequest(BaseModel):
#     name: str
#     birth_date: str  # e.g. "1985-05-10"
#     birth_time: str  # e.g. "09:45"
#     place: str       # e.g. "Bangalore, India"
#     gender: str      # e.g. "Male"




from pydantic import BaseModel
from typing import Dict, List, Optional

class Planet(BaseModel):
    name: str
    longitude: float
    sign: str
    sign_lord: str = ""
    degree: float
    retrograde: bool
    house: Optional[int]
    nakshatra: str
    nakshatra_lord: str = ""
    pada: int
    combust: bool = False
    avastha: str = ""
    status: str = ""
    dms: str = ""

class House(BaseModel):
    number: int
    longitude: float
    sign: str
    degree: float

class Aspect(BaseModel):
    between: List[str]
    type: str
    angle: float

class DashaPeriod(BaseModel):
    planet: str
    start_date: str
    end_date: str
    type: str

class KundliChart(BaseModel):
    place: str
    timezone: str
    julian_day: float
    ascendant: float
    ascendant_sign: str = ""
    ascendant_sign_lord: str = ""
    ascendant_nakshatra: str = ""
    ascendant_nakshatra_lord: str = ""
    mc: float
    planets: Dict[str, Planet]
    houses: Dict[int, House]
    aspects: List[Aspect]
    vimshottari_dasha: List[DashaPeriod] = []

class KundliResponse(BaseModel):
    name: str
    birth_date: str  # Use YYYY-MM-DD + HH:MM:SS or DD-MM-YYYY + HH:MM:SS (seconds optional)
    birth_time: str  # Displays with seconds if provided
    place: str
    gender: str
    chart: KundliChart

class KundliRequest(BaseModel):
    name: str
    birth_date: str  # e.g. "1985-05-10"
    birth_time: str  # e.g. "09:45:30" or "09:45" (seconds optional but recommended for accuracy)
    place: str       # e.g. "Bangalore, India"
    gender: str      # e.g. "Male"
