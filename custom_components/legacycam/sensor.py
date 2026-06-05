from homeassistant.components.sensor import SensorEntity


async def async_setup_entry(
    hass,
    entry,
    async_add_entities
):
    async_add_entities([
        LegacyCamRetentionSensor(entry),
        LegacyCamClipSensor(entry),
    ])


class LegacyCamRetentionSensor(SensorEntity):

    def __init__(self, entry):
        self._entry = entry

    @property
    def name(self):
        return "LegacyCam Retention"

    @property
    def unique_id(self):
        return f"{self._entry.entry_id}_retention"

    @property
    def native_value(self):
        return self._entry.data["retention_hours"]

    @property
    def native_unit_of_measurement(self):
        return "h"


class LegacyCamClipSensor(SensorEntity):

    def __init__(self, entry):
        self._entry = entry

    @property
    def name(self):
        return "LegacyCam Clip Length"

    @property
    def unique_id(self):
        return f"{self._entry.entry_id}_clip"

    @property
    def native_value(self):
        return self._entry.data["clip_seconds"]

    @property
    def native_unit_of_measurement(self):
        return "s"