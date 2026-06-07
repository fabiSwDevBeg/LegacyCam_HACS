import aiohttp

from .const import DEFAULT_PORT, DEFAULT_TIMEOUT, DOMAIN, ENDPOINT_PING, MANUFACTURER, MODEL


def endpoint_url(ip: str, path: str, port: int = DEFAULT_PORT) -> str:
    return f"http://{ip}:{port}{path}"


async def test_camera(ip: str) -> bool:
    url = endpoint_url(ip, ENDPOINT_PING)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=DEFAULT_TIMEOUT) as resp:
                return resp.status == 200
    except Exception:
        return False


def device_info(ip: str, name: str):
    return {
        "identifiers": {(DOMAIN, ip)},
        "manufacturer": MANUFACTURER,
        "model": MODEL,
        "name": name,
    }
