import requests
import json

url = "http://localhost:8000/astro/ask/"
headers = {
    "Content-Type": "application/json",
    "x-api-key": "supersecret@123A$trolzee"
}

# Test with Christian religion
payload = {
    "question": "What does my Venus in 5th house mean for my romantic life and creativity?",
    "religion": "christian"
}

print("Testing CHRISTIAN Astrologer Persona...")
print(f"Question: {payload['question']}")
print("-" * 80)
try:
    response = requests.post(url, json=payload, headers=headers, timeout=120)
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\nCATEGORY: {result['category']}\n")
        print("=" * 80)
        print("ANSWER:")
        print("=" * 80)
        print(result['answer'])
        print("\n" + "=" * 80)
        print("REMEDY:")
        print("=" * 80)
        print(result['remedy'])
        print("\n" + "=" * 80)
        
        # Check for Christian-specific references
        christian_indicators = [
            "prayer" in result['remedy'].lower() or "faith" in result['remedy'].lower(),
            "god" in result['remedy'].lower() or "lord" in result['remedy'].lower(),
            "blessing" in result['remedy'].lower() or "grace" in result['remedy'].lower()
        ]
        
        print("\nCHRISTIAN-SPECIFIC ELEMENTS:")
        print(f"✓ Contains prayer/faith references: {'Yes' if christian_indicators[0] else 'No'}")
        print(f"✓ References God/Lord: {'Yes' if christian_indicators[1] else 'No'}")
        print(f"✓ Mentions blessings/grace: {'Yes' if christian_indicators[2] else 'No'}")
        
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")
