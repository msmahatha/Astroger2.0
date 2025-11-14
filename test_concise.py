import requests
import json

url = "http://localhost:8000/astro/ask/"
headers = {
    "Content-Type": "application/json",
    "x-api-key": "supersecret@123A$trolzee"
}

# Test with career question
payload = {
    "question": "What does Jupiter in 10th house mean for my career growth and success?",
    "religion": "hindu"
}

print("Testing CONCISE Professional Response...")
print(f"Question: {payload['question']}")
print("-" * 80)

response = requests.post(url, json=payload, headers=headers, timeout=120)

if response.status_code == 200:
    result = response.json()
    
    print(f"\nCATEGORY: {result['category']}\n")
    print("ANSWER:")
    print("-" * 80)
    print(result['answer'])
    
    print("\n\nREMEDY:")
    print("-" * 80)
    print(result['remedy'])
    
    # Word count analysis
    answer_words = len(result['answer'].split())
    remedy_words = len(result['remedy'].split())
    
    print("\n" + "=" * 80)
    print("CONCISENESS CHECK:")
    print(f"✓ Answer: {answer_words} words (target: 150-200)")
    print(f"✓ Remedy: {remedy_words} words (target: 100-120)")
    print(f"✓ Professional tone: {'Yes' if 'Jupiter' in result['answer'] else 'Check'}")
    print(f"✓ Actionable remedies: {'Yes' if any(word in result['remedy'].lower() for word in ['mantra', 'thursday', 'guru', 'yellow', 'topaz']) else 'Check'}")
