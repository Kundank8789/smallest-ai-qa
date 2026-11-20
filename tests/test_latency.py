
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("SMALLEST_API_KEY")
URL = "https://api.smallest.ai/waves/v1/tts"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Accept": "audio/wav",
}

payload = {
    "text": "Hello from Smallest AI. This is a latency measurement test.",
    "voice_id": "meher",
    "model": "lightning_v3.1_pro",
    "language": "en",
    "sample_rate": 24000,
    "output_format": "wav"
}

times = []

for i in range(5):
    print(f"\nRequest {i + 1}/5")
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
        print(f"Duration: {elapsed:.3f} seconds")

        if response.ok:
            times.append(elapsed)
        else:
            print("Error:", response.text[:500])

    except requests.RequestException as error:
        print("Request failed:", error)

if times:
    print("\n--- LATENCY SUMMARY ---")
    print("Successful requests:", len(times))
    print(f"Average: {sum(times) / len(times):.3f}s")
    print(f"Minimum: {min(times):.3f}s")
    print(f"Maximum: {max(times):.3f}s")
else:
    print("No successful requests.")
