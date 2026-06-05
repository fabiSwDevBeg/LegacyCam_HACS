import logging

_LOGGER = logging.getLogger(__name__)

DOMAIN = "legacycam"

async def async_setup_entry(hass, entry):
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data
    return True