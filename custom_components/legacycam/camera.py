from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import requests


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    ip = entry.data["ip"]
    name = entry.data.get("name", "LegacyCam")

    async_add_entities([LegacyCamCamera(ip, name)])


class LegacyCamCamera(Camera):

    def __init__(self, ip, name):
        super().__init__()
        self._ip = ip
        self._name = name
        self._stream = f"http://{ip}:8080/stream"
        self._snapshot = f"http://{ip}:8080/snapshot.jpg"

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return f"legacycam_{self._ip}"

    @property
    def available(self):
        return True

    def camera_image(self):
        try:
            return requests.get(self._snapshot, timeout=5).content
        except:
            return None

    async def stream_source(self):
        return self._stream