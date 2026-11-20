
import os
import json
import time
import base64
import asyncio
from pathlib import Path

import websockets
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("SMALLEST_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")

WS_URL = "wss://api.smallest.ai/waves/v1/tts/live"
MODEL = "lightning_v3.1"

TEXT = (
    "Hello, this is a real-time text to speech streaming test. "
    "We are measuring the time taken to receive the first audio chunk."
)


async def test_websocket():
    if not API_KEY or not VOICE_ID:
        raise ValueError("Missing API key or voice ID in .env")

    headers = {"Authorization": f"Bearer {API_KEY}"}

    test_start = time.perf_counter()
    connected_at = None
    sent_at = None
    first_chunk_time = None
    chunk_times = []
    audio_chunks = []
    completed = False
    api_error = None

    try:
        async with websockets.connect(
            WS_URL,
            additional_headers=headers,
            open_timeout=15,
            close_timeout=10
        ) as ws:

            connected_at = time.perf_counter()
            connection_time = connected_at - test_start

            print("WebSocket connected successfully")
            print(f"Connection time: {connection_time:.3f}s")

            await ws.send(json.dumps({
                "voice_id": VOICE_ID,
                "text": TEXT,
                "model": MODEL,
                "language": "en",
                "sample_rate": 24000,
                "request_id": "qa-websocket-002"
            }))

            sent_at = time.perf_counter()

            async for message in ws:
                received_at = time.perf_counter()
                response = json.loads(message)

                status = response.get("status")
                data = response.get("data") or {}

                if status == "chunk":
                    audio = data.get("audio")

                    if audio:
                        if first_chunk_time is None:
                            first_chunk_time = received_at - sent_at
                            print(
                                f"\nFirst audio chunk: "
                                f"{first_chunk_time:.3f}s"
                            )

                        chunk_times.append(received_at)
                        audio_chunks.append(base64.b64decode(audio))

                        print(
                            f"Audio chunk {len(audio_chunks)} received"
                        )

                elif status == "word_timestamp":
                    print(
                        "Word:", data.get("word"),
                        "Start:", data.get("start"),
                        "End:", data.get("end")
                    )

                elif status == "complete":
                    completed = True
                    print("Synthesis completed")
                    break

                elif status == "error":
                    api_error = response
                    print("API error:", response)
                    break

    except Exception as error:
        api_error = str(error)
        print("WebSocket test failed:", error)

    total_duration = (
        time.perf_counter() - sent_at if sent_at else None
    )

    intervals = [
        chunk_times[i] - chunk_times[i - 1]
        for i in range(1, len(chunk_times))
    ]

    Path("logs").mkdir(exist_ok=True)

    audio_path = Path("logs/websocket_audio.bin")
    audio_path.write_bytes(b"".join(audio_chunks))

    print("\n--- WEBSOCKET TEST SUMMARY ---")
    print("Connection time:",
          round(connection_time, 3) if connected_at else "Failed")

    print("Send to first audio chunk:",
          round(first_chunk_time, 3)
          if first_chunk_time is not None else "Not received")

    print("Chunks received:", len(audio_chunks))
    print("Average inter-chunk interval:",
          f"{sum(intervals) / len(intervals):.4f}s"
          if intervals else "N/A")

    print("Maximum inter-chunk interval:",
          f"{max(intervals):.4f}s"
          if intervals else "N/A")

    print("Completed:", completed)
    print("Total synthesis duration:",
          round(total_duration, 3)
          if total_duration is not None else "N/A")

    print("API error:", api_error if api_error else "None")
    print("Audio saved:", audio_path)


if __name__ == "__main__":
    asyncio.run(test_websocket())
