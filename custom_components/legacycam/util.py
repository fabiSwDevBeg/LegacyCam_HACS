import math
import os
import aiohttp

def calculate_snippets(retention_hours, clip_seconds):
    retention_seconds = retention_hours * 3600
    return math.ceil(retention_seconds / clip_seconds)


def enforce_retention(folder, max_files):
    files = sorted(
        [f for f in os.listdir(folder) if f.endswith(".mp4")]
    )

    while len(files) > max_files:
        os.remove(os.path.join(folder, files[0]))
        files.pop(0)

async def test_camera(ip: str) -> bool:
    url = f"http://{ip}:8080/snapshot.jpg"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as resp:
                return resp.status == 200
    except:
        return False