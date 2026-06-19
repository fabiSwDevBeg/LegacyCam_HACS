from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_IP, CONF_NAME, DEFAULT_NAME, DOMAIN
from .util import device_info


async def async_setup_entry(hass, entry, async_add_entities):
    ip = entry.data[CONF_IP]
    name = entry.data.get(CONF_NAME, DEFAULT_NAME)
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    async_add_entities([
        LegacyCamOnlineBinarySensor(coordinator, ip, name),
        LegacyCamMotionBinarySensor(coordinator, ip, name),
    ])


class LegacyCamOnlineBinarySensor(CoordinatorEntity, BinarySensorEntity):

    def __init__(self, coordinator, ip, device_name):
        super().__init__(coordinator)
        self._ip = ip
        self._device_name = device_name

    @property
    def name(self):
        return "LegacyCam Online"

    @property
    def unique_id(self):
        return f"legacycam_online_{self._ip}"

    @property
    def device_info(self):
        return device_info(self._ip, self._device_name)

    @property
    def is_on(self):
        return bool((self.coordinator.data or {}).get("online"))


class LegacyCamMotionBinarySensor(CoordinatorEntity, BinarySensorEntity):

    def __init__(self, coordinator, ip, device_name):
        super().__init__(coordinator)
        self._ip = ip
        self._device_name = device_name

    @property
    def name(self):
        return "LegacyCam Motion"

    @property
    def unique_id(self):
        return f"legacycam_motion_{self._ip}"

    @property
    def device_info(self):
        return device_info(self._ip, self._device_name)

    @property
    def available(self):
        data = self.coordinator.data or {}
        return bool(data.get("online")) and bool(
            data.get("motion_detection")
        )

    @property
    def device_class(self):
        return BinarySensorDeviceClass.MOTION

    @property
    def is_on(self):
        return bool((self.coordinator.data or {}).get("motion_detected"))
