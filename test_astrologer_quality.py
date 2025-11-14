import requests
import json
import time

# Test questions to evaluate astrologer quality
test_questions = [
    {
        "question": "I have Saturn in 7th house. Will this delay my marriage?",
        "religion": "hindu"
    },
    {
        "question": "What does Mars in 10th house mean for my career?",
        "religion": "secular"
    }
]

url = "http://localhost:8000/astro/ask/"
headers = {
    "x-api-key": "supersecret@123A$trolzee",
    "Content-Type": "application/json"
}

print("=" * 80)
print("TESTING ASTROLOGER AI QUALITY")
print("=" * 80)

for i, test in enumerate(test_questions, 1):
    print(f"\n\n{'='*80}")
    print(f"TEST {i}: {test['religion'].upper()} Astrology")
    print(f"{'='*80}")
    print(f"\nQuestion: {test['question']}")
    print("\nSending request... (this may take 10-30 seconds)")
    
    try:
        start_time = time.time()
        response = requests.post(url, headers=headers, json=test, timeout=60)
        elapsed_time = time.time() - start_time
        
        print(f"\nResponse Time: {elapsed_time:.2f} seconds")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n{'─'*80}")
            print(f"CATEGORY: {data.get('category', 'N/A')}")
            print(f"{'─'*80}")
            print(f"\nANSWER:")
            print(data.get('answer', 'No answer provided'))
            print(f"\n{'─'*80}")
            print(f"\nREMEDY:")
            print(data.get('remedy', 'No remedy provided'))
            print(f"{'─'*80}")
            
            # Quality check
            answer_length = len(data.get('answer', ''))
            remedy_length = len(data.get('remedy', ''))
            print(f"\n📊 QUALITY METRICS:")
            print(f"   Answer Length: {answer_length} characters")
            print(f"   Remedy Length: {remedy_length} characters")
            
            if answer_length > 500 and remedy_length > 300:
                print(f"   ✅ Response is comprehensive!")
            else:
                print(f"   ⚠️ Response might be too short")
                
        else:
            print(f"\n❌ ERROR: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except requests.exceptions.Timeout:
        print("\n❌ Request timed out after 60 seconds")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    
    if i < len(test_questions):
        print(f"\nWaiting 3 seconds before next test...")
        time.sleep(3)

print(f"\n\n{'='*80}")
print("TESTING COMPLETE")
print(f"{'='*80}\n")
