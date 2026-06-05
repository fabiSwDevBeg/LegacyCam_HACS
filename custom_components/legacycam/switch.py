import aiohttp
from homeassistant.components.switch import SwitchEntity

class LegacyCamFlashSwitch(SwitchEntity):

    def __init__(self, ip):
        self._ip = ip
        self._state = False

    @property
    def name(self):
        return "LegacyCam Flash"

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