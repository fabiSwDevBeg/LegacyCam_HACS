from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_IP,
    CONF_NAME,
    DEFAULT_NAME,
    DEFAULT_TIMEOUT,
    DOMAIN,
    ENDPOINT_FLASH_OFF,
    ENDPOINT_FLASH_ON,
)
from .util import device_info, endpoint_url


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    ip = entry.data[CONF_IP]
    name = entry.data.get(CONF_NAME, DEFAULT_NAME)
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    async_add_entities([
        LegacyCamFlashSwitch(coordinator, ip, name),
        LegacyCamMotionDetectionSwitch(coordinator, ip, name),
        LegacyCamRecordingSwitch(coordinator, ip, name),
    ])


class LegacyCamFlashSwitch(CoordinatorEntity, SwitchEntity):

    def __init__(self, coordinator, ip, name):
        super().__init__(coordinator)
        self._ip = ip
        self._device_name = name

    @property
    def name(self):
        return "LegacyCam Flash"

    @property
    def unique_id(self):
        return f"legacycam_flash_{self._ip}"
    
    @property
    def device_info(self):
        return device_info(self._ip, self._device_name)

    @property
    def available(self):
        return bool((self.coordinator.data or {}).get("online"))

    @property
    def is_on(self):
        return bool((self.coordinator.data or {}).get("flash"))

    async def async_turn_on(self):
        await self._call(ENDPOINT_FLASH_ON)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self):
        await self._call(ENDPOINT_FLASH_OFF)
        await self.coordinator.async_request_refresh()

    async def _call(self, path):
        session = async_get_clientsession(self.hass)

        async with session.get(endpoint_url(self._ip, path), timeout=DEFAULT_TIMEOUT):
            return


class LegacyCamRuntimeSwitch(CoordinatorEntity, SwitchEntity):

    def __init__(self, coordinator, ip, device_name):
        super().__init__(coordinator)
        self._ip = ip
        self._device_name = device_name

    @property
    def device_info(self):
        return device_info(self._ip, self._device_name)

    @property
    def available(self):
        return bool((self.coordinator.data or {}).get("online"))


class LegacyCamMotionDetectionSwitch(LegacyCamRuntimeSwitch):

    @property
    def name(self):
        return "LegacyCam Motion Detection"

    @property
    def unique_id(self):
        return f"legacycam_motion_detection_{self._ip}"

    @property
    def is_on(self):
        return bool((self.coordinator.data or {}).get("motion_detection"))

    async def async_turn_on(self):
        await self.coordinator.async_set_motion_detection_enabled(True)

    async def async_turn_off(self):
        await self.coordinator.async_set_motion_detection_enabled(False)


class LegacyCamRecordingSwitch(LegacyCamRuntimeSwitch):

    @property
    def name(self):
        return "LegacyCam Recording"

    @property
    def unique_id(self):
        return f"legacycam_recording_{self._ip}"

    @property
    def is_on(self):
        return bool((self.coordinator.data or {}).get("recording"))

    @property
    def extra_state_attributes(self):
        return {
            "path": (self.coordinator.data or {}).get("recording_path"),
            "error": (self.coordinator.data or {}).get("recording_error"),
        }

    async def async_turn_on(self):
        await self.coordinator.async_set_recording_enabled(True)

    async def async_turn_off(self):
        await self.coordinator.async_set_recording_enabled(False)
