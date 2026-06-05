from homeassistant.components.camera import Camera
import requests

class LegacyCamCamera(Camera):

    def __init__(self, ip):
        super().__init__()
        self._ip = ip
        self._stream = f"http://{ip}:8080/stream"
        self._snapshot = f"http://{ip}:8080/snapshot.jpg"

    def camera_image(self):
        try:
            return requests.get(self._snapshot, timeout=5).content
        except:
            return None

    async def stream_source(self):
        return self._stream