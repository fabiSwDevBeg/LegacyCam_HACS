import asyncio

import aiohttp
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DEFAULT_PORT, DEFAULT_TIMEOUT, DOMAIN, ENDPOINT_PING, MANUFACTURER, MODEL


def endpoint_url(ip: str, path: str, port: int = DEFAULT_PORT) -> str:
    return f"http://{ip}:{port}{path}"


async def test_camera(hass, ip: str) -> bool:
    url = endpoint_url(ip, ENDPOINT_PING)

    try:
        session = async_get_clientsession(hass)
        async with session.get(url, timeout=DEFAULT_TIMEOUT) as resp:
            return resp.status == 200
    except (aiohttp.ClientError, asyncio.TimeoutError, TimeoutError):
        return False


def device_info(ip: str, name: str):
    return {
        "identifiers": {(DOMAIN, ip)},
        "manufacturer": MANUFACTURER,
        "model": MODEL,
        "name": name,
    }
