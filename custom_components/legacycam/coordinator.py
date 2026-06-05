from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from datetime import timedelta
import aiohttp

class LegacyCamCoordinator(DataUpdateCoordinator):

    def __init__(self, hass, ip):
        self.ip = ip

        super().__init__(
            hass,
            logger=None,
            name="legacycam",
            update_interval=timedelta(seconds=30),
        )

    async def _async_update_data(self):
        url = f"http://{self.ip}:8080/snapshot.jpg"

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as r:
                    return {"online": r.status == 200}
            except:
                return {"online": False}