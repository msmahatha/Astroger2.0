import asyncio
import sys
sys.path.append('/Users/madhusudanmahatha/Downloads/Astrology25/Astrology/Astrologer')

async def test_kundali():
    from dotenv import load_dotenv
    load_dotenv()
    
    from src.services.astro_service import get_astrologyapi_remedy
    
    birth_details = {
        "birthDate": "02 February 1996",
        "birthTime": "01:19",
        "birthLatitude": 22.5743545,
        "birthLongitude": 88.3628734,
        "birthPlace": "Kolkata, West Bengal"
    }
    
    print("Testing comprehensive kundali generation...")
    print("=" * 80)
    
    result = await get_astrologyapi_remedy("show my kundali", birth_details)
    
    print(result)
    print("=" * 80)
    print(f"✅ Length: {len(result)} characters")

if __name__ == "__main__":
    asyncio.run(test_kundali())
