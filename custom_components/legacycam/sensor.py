from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfTime
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_IP, CONF_NAME, DEFAULT_NAME, DOMAIN
from .util import device_info


async def async_setup_entry(hass, entry, async_add_entities):
    ip = entry.data[CONF_IP]
    name = entry.data.get(CONF_NAME, DEFAULT_NAME)
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    async_add_entities([
        LegacyCamUptimeSensor(coordinator, ip, name),
        LegacyCamStreamClientsSensor(coordinator, ip, name),
        LegacyCamVersionSensor(coordinator, ip, name),
    ])


class LegacyCamSensor(CoordinatorEntity, SensorEntity):

    def __init__(self, coordinator, ip, device_name):
        super().__init__(coordinator)
        self._ip = ip
        self._device_name = device_name

    @property
    def device_info(self):
        return device_info(self._ip, self._device_name)

    @property
    def available(self):
        return bool(self.coordinator.data.get("online"))


class LegacyCamUptimeSensor(LegacyCamSensor):

    @property
    def name(self):
        return "LegacyCam Uptime"

    @property
    def unique_id(self):
        return f"legacycam_uptime_{self._ip}"

    @property
    def native_value(self):
        return self.coordinator.data.get("uptime")

    @property
    def native_unit_of_measurement(self):
        return UnitOfTime.SECONDS


class LegacyCamStreamClientsSensor(LegacyCamSensor):

    @property
    def name(self):
        return "LegacyCam Stream Clients"

    @property
    def unique_id(self):
        return f"legacycam_stream_clients_{self._ip}"

    @property
    def native_value(self):
        return self.coordinator.data.get("stream_clients")


class LegacyCamVersionSensor(LegacyCamSensor):

    @property
    def name(self):
        return "LegacyCam Version"

    @property
    def unique_id(self):
        return f"legacycam_version_{self._ip}"

    @property
    def native_value(self):
        return self.coordinator.data.get("version")
