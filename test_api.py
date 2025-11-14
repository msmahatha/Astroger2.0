import requests
import json

# Test the API endpoint
url = "http://localhost:8000/astro/ask/"
headers = {
    "x-api-key": "supersecret@123A$trolzee",
    "Content-Type": "application/json"
}
data = {
    "question": "What does Jupiter in the 9th house signify for career growth?",
    "religion": "hindu"
}

print("Testing Astrolozee-AI API...")
print(f"URL: {url}")
print(f"Question: {data['question']}")
print(f"Religion: {data['religion']}")
print("\nSending request...\n")

try:
    response = requests.post(url, headers=headers, json=data, timeout=60)
    print(f"Status Code: {response.status_code}")
    print("\nResponse:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
