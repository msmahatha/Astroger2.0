import asyncio
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def show_api_response():
    import sys
    sys.path.append('/Users/madhusudanmahatha/Downloads/Astrology25/Astrology/Astrologer')
    from src.services.astro_service import get_astrologyapi_remedy
    
    print("=" * 80)
    print("ASTROLOGYAPI.COM - FULL JSON RESPONSE")
    print("=" * 80)
    print()
    
    # Test with your birth details
    birth_details = {
        "birthDate": "02 February 1996",
        "birthTime": "01:19",
        "birthLatitude": 22.5743545,
        "birthLongitude": 88.3628734
    }
    
    print("REQUEST:")
    print(f"Question: 'show my kundali'")
    print(f"Birth Details: {json.dumps(birth_details, indent=2)}")
    print()
    print("-" * 80)
    print()
    
    try:
        result = await get_astrologyapi_remedy("show my kundali", birth_details)
        
        print("RESPONSE:")
        print()
        
        # Try to parse as JSON if it's a dict/string
        if isinstance(result, dict):
            print(json.dumps(result, indent=2))
        elif isinstance(result, str):
            try:
                parsed = json.loads(result)
                print(json.dumps(parsed, indent=2))
            except:
                print(result)
        else:
            print(result)
        
        print()
        print("=" * 80)
        print(f"✅ SUCCESS - Response length: {len(str(result))} characters")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(show_api_response())
