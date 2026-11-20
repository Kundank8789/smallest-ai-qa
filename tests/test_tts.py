
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("SMALLEST_API_KEY")

if not API_KEY:
    raise RuntimeError("SMALLEST_API_KEY is missing from .env")

URL = "https://api.smallest.ai/waves/v1/tts"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Accept": "audio/wav",
}

payload = {
    "text": "Hello from Smallest AI. This is my first API test.",
    "voice_id": "meher",
    "model": "lightning_v3.1_pro",
    "language": "en",
    "sample_rate": 24000,
    "output_format": "wav"
}

print("Sending TTS request...")

start = time.perf_counter()

try:
    response = requests.post(
        URL,
        headers=headers,
        json=payload,
        timeout=60
    )

    elapsed = time.perf_counter() - start

    print("Status:", response.status_code)
    print(f"Request duration: {elapsed:.3f} seconds")

    if response.ok:
        if response.headers.get("Content-Type", "").startswith("audio/"):
            with open("logs/first_audio.wav", "wb") as f:
                f.write(response.content)

            print("Audio saved: logs/first_audio.wav")
            print("Audio bytes:", len(response.content))
        else:
            print("Unexpected response content type:")
            print(response.headers.get("Content-Type"))
            print(response.text[:1000])
    else:
        print("API error:", response.text[:2000])

except requests.RequestException as error:
    print("Request failed:", error)
