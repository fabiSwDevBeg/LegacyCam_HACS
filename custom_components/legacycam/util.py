import math
import os

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