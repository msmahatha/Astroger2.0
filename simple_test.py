import requests
import json

url = "http://localhost:8000/astro/ask/"
headers = {
    "Content-Type": "application/json",
    "x-api-key": "supersecret@123A$trolzee"
}

# Test a serious astrological question
payload = {
    "question": "I have Saturn in 7th house and I'm 32 years old. Will this delay my marriage? What should I do?",
    "religion": "hindu"
}

print("Testing Astrologer Quality...")
print(f"Question: {payload['question']}")
print("-" * 80)
try:
    response = requests.post(url, json=payload, headers=headers, timeout=120)
    print(f"\nStatus Code: {response.status_code}\n")
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"CATEGORY: {result['category']}\n")
        print("=" * 80)
        print("ANSWER:")
        print("=" * 80)
        print(result['answer'])
        print("\n" + "=" * 80)
        print("REMEDY:")
        print("=" * 80)
        print(result['remedy'])
        print("\n" + "=" * 80)
        
        # Evaluate quality
        print("\nQUALITY ASSESSMENT:")
        print("-" * 80)
        answer_words = len(result['answer'].split())
        remedy_words = len(result['remedy'].split())
        
        print(f"✓ Answer length: {answer_words} words")
        print(f"✓ Remedy length: {remedy_words} words")
        
        # Check for professional tone indicators
        professional_indicators = [
            "chart" in result['answer'].lower() or "saturn" in result['answer'].lower(),
            len(result['answer']) > 200,
            len(result['remedy']) > 100,
            "shani" in result['answer'].lower() or "mantra" in result['remedy'].lower() or "practice" in result['remedy'].lower()
        ]
        
        print(f"✓ Astrological depth: {'Yes' if professional_indicators[0] else 'Needs improvement'}")
        print(f"✓ Comprehensive answer: {'Yes' if professional_indicators[1] else 'Too short'}")
        print(f"✓ Detailed remedy: {'Yes' if professional_indicators[2] else 'Too short'}")
        print(f"✓ Religion-specific guidance: {'Yes' if professional_indicators[3] else 'Could be more specific'}")
        
        overall = "EXCELLENT" if all(professional_indicators) else "GOOD" if sum(professional_indicators) >= 3 else "NEEDS IMPROVEMENT"
        print(f"\n🎯 OVERALL QUALITY: {overall}")
        
    else:
        print(f"Error: {response.text}")
        
except requests.exceptions.Timeout:
    print("❌ Request timed out after 120 seconds")
except Exception as e:
    print(f"❌ Error: {str(e)}")
