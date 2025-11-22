import asyncio
import httpx
import json
from dotenv import load_dotenv
import os

load_dotenv()

async def generate_full_kundali():
    """Generate complete kundali with all details"""
    
    USER_ID = os.getenv("ASTROLOGY_API_USER_ID")
    API_KEY = os.getenv("ASTROLOGY_API_KEY")
    BASE_URL = "https://json.astrologyapi.com/v1/"
    
    # Birth details
    payload = {
        "day": 2,
        "month": 2,
        "year": 1996,
        "hour": 1,
        "min": 19,
        "lat": 22.5743545,
        "lon": 88.3628734,
        "tzone": 5.5
    }
    
    print("=" * 100)
    print("COMPLETE KUNDALI - Madhusudanmahatha")
    print("Birth: 02 February 1996, 01:19 AM, Kolkata, West Bengal")
    print("=" * 100)
    print()
    
    async with httpx.AsyncClient() as client:
        # 1. Birth Details
        print("📋 BIRTH DETAILS")
        print("-" * 100)
        try:
            response = await client.post(
                f"{BASE_URL}birth_details",
                json=payload,
                auth=(USER_ID, API_KEY),
                timeout=10.0
            )
            birth_data = response.json()
            print(json.dumps(birth_data, indent=2))
        except Exception as e:
            print(f"Error: {e}")
        print()
        
        # 2. Planetary Positions
        print("🌟 PLANETARY POSITIONS")
        print("-" * 100)
        try:
            response = await client.post(
                f"{BASE_URL}planets",
                json=payload,
                auth=(USER_ID, API_KEY),
                timeout=10.0
            )
            planets_data = response.json()
            print(json.dumps(planets_data, indent=2))
        except Exception as e:
            print(f"Error: {e}")
        print()
        
        # 3. Ascendant (Lagna)
        print("🔺 ASCENDANT (LAGNA)")
        print("-" * 100)
        try:
            response = await client.post(
                f"{BASE_URL}ascendant",
                json=payload,
                auth=(USER_ID, API_KEY),
                timeout=10.0
            )
            ascendant_data = response.json()
            print(json.dumps(ascendant_data, indent=2))
        except Exception as e:
            print(f"Error: {e}")
        print()
        
        # 4. Moon Sign (Rashi)
        print("🌙 MOON SIGN (RASHI)")
        print("-" * 100)
        try:
            response = await client.post(
                f"{BASE_URL}moon_sign",
                json=payload,
                auth=(USER_ID, API_KEY),
                timeout=10.0
            )
            moon_data = response.json()
            print(json.dumps(moon_data, indent=2))
        except Exception as e:
            print(f"Error: {e}")
        print()
        
        # 5. Birth Nakshatra
        print("⭐ BIRTH NAKSHATRA")
        print("-" * 100)
        try:
            response = await client.post(
                f"{BASE_URL}birth_nakshatra",
                json=payload,
                auth=(USER_ID, API_KEY),
                timeout=10.0
            )
            nakshatra_data = response.json()
            print(json.dumps(nakshatra_data, indent=2))
        except Exception as e:
            print(f"Error: {e}")
        print()
        
        # 6. Current Vimshottari Dasha
        print("⏰ CURRENT VIMSHOTTARI DASHA")
        print("-" * 100)
        try:
            response = await client.post(
                f"{BASE_URL}current_vdasha",
                json=payload,
                auth=(USER_ID, API_KEY),
                timeout=10.0
            )
            dasha_data = response.json()
            print(json.dumps(dasha_data, indent=2))
        except Exception as e:
            print(f"Error: {e}")
        print()
        
        # 7. Chart (Rashi Chart)
        print("📊 RASHI CHART (D1)")
        print("-" * 100)
        try:
            response = await client.post(
                f"{BASE_URL}horo_chart/D1",
                json=payload,
                auth=(USER_ID, API_KEY),
                timeout=10.0
            )
            chart_data = response.json()
            print(json.dumps(chart_data, indent=2))
        except Exception as e:
            print(f"Error: {e}")
        print()
        
        print("=" * 100)
        print("✅ KUNDALI GENERATION COMPLETE")
        print("=" * 100)

if __name__ == "__main__":
    asyncio.run(generate_full_kundali())
