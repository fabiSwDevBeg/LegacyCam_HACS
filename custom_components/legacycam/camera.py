from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_IP,
    CONF_NAME,
    DEFAULT_NAME,
    DOMAIN,
    ENDPOINT_STREAM,
)
from .util import device_info, endpoint_url


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    ip = entry.data[CONF_IP]
    name = entry.data.get(CONF_NAME, DEFAULT_NAME)
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    async_add_entities([LegacyCamCamera(coordinator, ip, name)])


class LegacyCamCamera(CoordinatorEntity, Camera):

    def __init__(self, coordinator, ip, name):
        CoordinatorEntity.__init__(self, coordinator)
        Camera.__init__(self)
        self._ip = ip
        self._name = name
        self._stream = endpoint_url(ip, ENDPOINT_STREAM)

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return f"legacycam_{self._ip}"

    @property
    def device_info(self):
        return device_info(self._ip, self._name)

    @property
    def available(self):
        return bool(self.coordinator.data.get("online"))

    async def stream_source(self):
        return self._stream
