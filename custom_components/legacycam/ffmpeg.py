import subprocess
import datetime
import os

def record_clip(ip, duration, output_dir="/config/www/legacycam"):
    os.makedirs(output_dir, exist_ok=True)

    filename = datetime.datetime.now().strftime("clip_%Y%m%d_%H%M%S.mp4")
    path = os.path.join(output_dir, filename)

    url = f"http://{ip}:8080/stream"

    cmd = [
        "ffmpeg",
        "-i", url,
        "-t", str(duration),
        "-vcodec", "copy",
        path
    ]

    subprocess.Popen(cmd)

    return path