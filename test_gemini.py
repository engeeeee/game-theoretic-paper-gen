"""
Test Gemini API directly
"""
import os
from dotenv import load_dotenv

# Load config
load_dotenv(".env.example")

api_key = os.getenv("AGENT_B_API_KEY") or os.getenv("GOOGLE_API_KEY")
model_name = os.getenv("AGENT_B_MODEL", "gemini-1.5-flash")

print(f"Testing with model: {model_name}")
print(f"API Key: {api_key[:10]}..." if api_key else "No API key found!")

if not api_key:
    print("Please set AGENT_B_API_KEY in .env.example")
    exit(1)

import google.generativeai as genai

genai.configure(api_key=api_key)

# List available models
print("\n--- Available Models ---")
for m in genai.list_models():
    if "generateContent" in m.supported_generation_methods:
        print(f"  {m.name}")

print(f"\n--- Testing {model_name} ---")
try:
    model = genai.GenerativeModel(model_name)
    response = model.generate_content("Say hello in one word")
    print(f"Response: {response.text}")
    print("\n✓ API is working!")
except Exception as e:
    print(f"\n✗ Error: {e}")
