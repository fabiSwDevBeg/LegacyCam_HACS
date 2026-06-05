from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import aiohttp


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    ip = entry.data["ip"]
    async_add_entities([LegacyCamFlashSwitch(ip)])


class LegacyCamFlashSwitch(SwitchEntity):

    def __init__(self, ip):
        self._ip = ip
        self._state = False

    @property
    def name(self):
        return "LegacyCam Flash"

    @property
    def unique_id(self):
        return f"legacycam_flash_{self._ip}"
    
    @property
    def is_on(self):
        return self._state

    async def async_turn_on(self):
        await self._call(f"http://{self._ip}:8080/flash/on")
        self._state = True
        self.async_write_ha_state()

    async def async_turn_off(self):
        await self._call(f"http://{self._ip}:8080/flash/off")
        self._state = False
        self.async_write_ha_state()

    async def _call(self, url):
        async with aiohttp.ClientSession() as session:
            await session.get(url)