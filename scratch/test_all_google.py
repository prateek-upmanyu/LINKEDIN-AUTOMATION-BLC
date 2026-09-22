import requests
import json

key = 'AQ.Ab8RN6IuB9iVGuASa88ySS6IAjBUT_RRVEhmpxeK6yBXqlArSQ'
payload = {"contents": [{"parts": [{"text": "Hello"}]}]}

endpoints = [
    ("GenerativeLanguage v1beta query", f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}", {'Content-Type': 'application/json'}),
    ("GenerativeLanguage v1beta x-goog-api-key", "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent", {'Content-Type': 'application/json', 'x-goog-api-key': key}),
    ("GenerativeLanguage v1beta Bearer", "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent", {'Content-Type': 'application/json', 'Authorization': f'Bearer {key}'}),
    ("VertexAI us-central1 Bearer", "https://us-central1-aiplatform.googleapis.com/v1/projects/868539/locations/us-central1/publishers/google/models/gemini-1.5-flash:generateContent", {'Content-Type': 'application/json', 'Authorization': f'Bearer {key}'}),
    ("VertexAI us-central1 key query", f"https://us-central1-aiplatform.googleapis.com/v1/projects/868539/locations/us-central1/publishers/google/models/gemini-1.5-flash:generateContent?key={key}", {'Content-Type': 'application/json'}),
]

for name, url, headers in endpoints:
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=8)
        print(f"[{name}] Code: {r.status_code} | Res: {r.text[:120]}")
    except Exception as e:
        print(f"[{name}] Err: {e}")
