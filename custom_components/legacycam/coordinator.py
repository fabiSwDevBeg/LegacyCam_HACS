import logging
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from datetime import timedelta

from .const import (
    DEFAULT_TIMEOUT,
    ENDPOINT_STATUS,
    UPDATE_INTERVAL_SECONDS,
)
from .util import endpoint_url

_LOGGER = logging.getLogger(__name__)


class LegacyCamCoordinator(DataUpdateCoordinator):

    def __init__(self, hass, ip):
        self.ip = ip
        self.session = async_get_clientsession(hass)

        super().__init__(
            hass,
            logger=_LOGGER,
            name="legacycam",
            update_interval=timedelta(seconds=UPDATE_INTERVAL_SECONDS),
        )

    async def _async_update_data(self):
        url = endpoint_url(self.ip, ENDPOINT_STATUS)

        try:
            async with self.session.get(url, timeout=DEFAULT_TIMEOUT) as response:
                if response.status != 200:
                    return self._offline_data()

                payload = await response.json(content_type=None)

                return {
                    "online": bool(payload.get("online", True)),
                    "flash": bool(payload.get("flash", False)),
                    "uptime": payload.get("uptime"),
                    "version": payload.get("version", ""),
                    "device": payload.get("device", ""),
                    "stream_clients": int(payload.get("stream_clients", 0)),
                }
        except Exception as err:
            _LOGGER.debug("LegacyCam status update failed: %s", err)
            return self._offline_data()

    def _offline_data(self):
        return {
            "online": False,
            "flash": False,
            "uptime": None,
            "version": "",
            "device": "",
            "stream_clients": 0,
        }
