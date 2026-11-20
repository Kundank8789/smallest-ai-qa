
import os
import json
import time
import asyncio
import websockets

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("SMALLEST_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")

WS_URL = "wss://api.smallest.ai/waves/v1/tts/live"
MODEL = "lightning_v3.1"

TEXT = (
    "This is a controlled concurrency test. "
    "We are checking whether multiple independent "
    "text to speech streams can complete successfully."
)

async def run_tts(request_number):
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    start = time.perf_counter()
    first_chunk = None
    chunks = 0
    completed = False
    error = None

    try:
        async with websockets.connect(
            WS_URL,
            additional_headers=headers,
            open_timeout=15,
            close_timeout=10
        ) as ws:

            await ws.send(json.dumps({
                "voice_id": VOICE_ID,
                "text": TEXT,
                "model": MODEL,
                "language": "en",
                "sample_rate": 24000,
                "request_id": f"qa-concurrency-{request_number}"
            }))

            async for message in ws:
                received_at = time.perf_counter()
                data = json.loads(message)

                status = data.get("status")

                if status == "chunk":
                    if first_chunk is None:
                        first_chunk = received_at - start
                    chunks += 1

                elif status == "complete":
                    completed = True
                    break

                elif status == "error":
                    error = data
                    break

    except Exception as exc:
        error = str(exc)

    duration = time.perf_counter() - start

    return {
        "request": request_number,
        "first_chunk": first_chunk,
        "chunks": chunks,
        "completed": completed,
        "duration": duration,
        "error": error
    }


async def main():
    if not API_KEY or not VOICE_ID:
        raise ValueError("Check API_KEY and VOICE_ID in .env")

    print("Starting 3 concurrent TTS requests...\n")

    results = await asyncio.gather(
        run_tts(1),
        run_tts(2),
        run_tts(3)
    )

    print("\n--- CONCURRENCY TEST RESULTS ---")

    for result in results:
        print(f"\nRequest {result['request']}")
        print("Completed:", result["completed"])
        print("Chunks:", result["chunks"])
        print("First chunk:", result["first_chunk"])
        print(f"Duration: {result['duration']:.3f}s")

        if result["error"]:
            print("Error:", result["error"])

    successful = sum(r["completed"] for r in results)

    print("\n--- SUMMARY ---")
    print("Successful:", successful, "/ 3")
    print("Failed:", 3 - successful)


if __name__ == "__main__":
    asyncio.run(main())
