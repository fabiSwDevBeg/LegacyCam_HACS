import asyncio
import logging

import aiohttp
from aiohttp import web
from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import (
    async_aiohttp_proxy_web,
    async_get_clientsession,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_IP,
    CONF_NAME,
    DEFAULT_TIMEOUT,
    DEFAULT_NAME,
    DOMAIN,
    ENDPOINT_STREAM,
)
from .util import device_info, endpoint_url

_LOGGER = logging.getLogger(__name__)

_JPEG_START = b"\xff\xd8"
_JPEG_END = b"\xff\xd9"
_MJPEG_CHUNK_SIZE = 4096


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
        self.content_type = "image/jpeg"

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
        return bool((self.coordinator.data or {}).get("online"))

    async def stream_source(self):
        return self._stream

    async def async_camera_image(self, width=None, height=None):
        session = async_get_clientsession(self.hass)
        buffer = bytearray()

        try:
            async with session.get(self._stream, timeout=DEFAULT_TIMEOUT) as response:
                if response.status != 200:
                    _LOGGER.debug("LegacyCam snapshot stream returned HTTP %s", response.status)
                    return None

                async for chunk in response.content.iter_chunked(_MJPEG_CHUNK_SIZE):
                    buffer.extend(chunk)
                    frame = _extract_jpeg_frame(buffer)

                    if frame:
                        return frame
        except (asyncio.TimeoutError, TimeoutError):
            _LOGGER.debug("Timeout getting LegacyCam snapshot from %s", self._stream)
        except aiohttp.ClientError as err:
            _LOGGER.debug("Error getting LegacyCam snapshot from %s: %s", self._stream, err)

        return None

    async def handle_async_mjpeg_stream(self, request: web.Request):
        session = async_get_clientsession(self.hass)
        stream_coro = session.get(self._stream)
        return await async_aiohttp_proxy_web(self.hass, request, stream_coro)


def _extract_jpeg_frame(buffer):
    start = buffer.find(_JPEG_START)

    if start < 0:
        if len(buffer) > 1024 * 1024:
            del buffer[:-2]
        return None

    end = buffer.find(_JPEG_END, start + 2)

    if end < 0:
        if start > 0:
            del buffer[:start]
        return None

    frame_end = end + 2
    frame = bytes(buffer[start:frame_end])
    del buffer[:frame_end]
    return frame
