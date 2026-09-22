import os
import requests
import json

key = 'AQ.Ab8RN6IuB9iVGuASa88ySS6IAjBUT_RRVEhmpxeK6yBXqlArSQ'

print("--- Testing Gemini API Backend (Read-Only Test - No Posting) ---")

# Test 1: Rest API v1beta
url_v1beta = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
payload = {
    "contents": [{
        "parts": [{"text": "Give one punchy sales quote and author name."}]
    }]
}

try:
    r1 = requests.post(url_v1beta, json=payload, timeout=10)
    print(f"[v1beta gemini-1.5-flash] Status: {r1.status_code}")
    if r1.status_code == 200:
        text = r1.json()['candidates'][0]['content']['parts'][0]['text']
        print("SUCCESS! Generated quote:\n", text)
    else:
        print("Response Error:", r1.text[:250])
except Exception as e:
    print("Exception:", e)

# Test 2: Rest API v1
url_v1 = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={key}"
try:
    r2 = requests.post(url_v1, json=payload, timeout=10)
    print(f"\n[v1 gemini-1.5-flash] Status: {r2.status_code}")
    if r2.status_code == 200:
        text = r2.json()['candidates'][0]['content']['parts'][0]['text']
        print("SUCCESS! Generated quote:\n", text)
    else:
        print("Response Error:", r2.text[:250])
except Exception as e:
    print("Exception:", e)

# Test 3: google.generativeai SDK
try:
    import google.generativeai as genai
    genai.configure(api_key=key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    resp = model.generate_content("Give one punchy sales quote and author name.")
    print("\n[google.generativeai SDK] SUCCESS! Generated quote:\n", resp.text)
except Exception as e:
    print("\n[google.generativeai SDK] Error:", e)
