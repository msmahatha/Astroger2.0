import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test the API integration
async def test_api():
    # Import after loading env
    import sys
    sys.path.append('/Users/madhusudanmahatha/Downloads/Astrology25/Astrology/Astrologer')
    from src.services.astro_service import get_astrologyapi_remedy
    
    print("Testing AstrologyAPI.com integration...")
    print(f"USER_ID: {os.getenv('ASTROLOGY_API_USER_ID')}")
    print(f"API_KEY: {'SET' if os.getenv('ASTROLOGY_API_KEY') else 'NOT SET'}")
    print()
    
    # Test with sample birth details
    birth_details = {
        "birthDate": "02 February 1996",
        "birthTime": "01:19",
        "birthLatitude": 22.5743545,
        "birthLongitude": 88.3628734
    }
    
    question = "show my kundali"
    
    try:
        result = await get_astrologyapi_remedy(question, birth_details)
        print("✅ API Call Successful!")
        print(f"Response length: {len(str(result))} characters")
        print(f"Response preview: {str(result)[:200]}...")
        return True
    except Exception as e:
        print(f"❌ API Call Failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_api())
    exit(0 if success else 1)
