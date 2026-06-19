import voluptuous as vol
from homeassistant import config_entries
from .const import (
    CONF_IP,
    CONF_MOTION_FLASH_HOLD_SECONDS,
    CONF_MOTION_SAMPLE_INTERVAL,
    CONF_MOTION_THRESHOLD,
    CONF_NAME,
    CONF_RECORDING_PATH,
    CONF_RECORDING_RETENTION_HOURS,
    CONF_RECORDING_SEGMENT_SECONDS,
    DEFAULT_MOTION_FLASH_HOLD_SECONDS,
    DEFAULT_MOTION_SAMPLE_INTERVAL,
    DEFAULT_MOTION_THRESHOLD,
    DEFAULT_NAME,
    DEFAULT_RECORDING_PATH,
    DEFAULT_RECORDING_RETENTION_HOURS,
    DEFAULT_RECORDING_SEGMENT_SECONDS,
    DOMAIN,
)
from .util import test_camera


class LegacyCamConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    @staticmethod
    def async_get_options_flow(config_entry):
        return LegacyCamOptionsFlow(config_entry)

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:

            ip_ok = await test_camera(user_input[CONF_IP])

            if not ip_ok:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data=user_input
                )

        schema = vol.Schema({
            vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
            vol.Required(CONF_IP): str,
        })
        
        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors
        )


class LegacyCamOptionsFlow(config_entries.OptionsFlow):

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = self.config_entry.options

        schema = vol.Schema({
            vol.Required(
                CONF_RECORDING_SEGMENT_SECONDS,
                default=options.get(CONF_RECORDING_SEGMENT_SECONDS, DEFAULT_RECORDING_SEGMENT_SECONDS),
            ): vol.All(vol.Coerce(int), vol.Range(min=5, max=300)),
            vol.Required(
                CONF_RECORDING_RETENTION_HOURS,
                default=options.get(CONF_RECORDING_RETENTION_HOURS, DEFAULT_RECORDING_RETENTION_HOURS),
            ): vol.All(vol.Coerce(int), vol.Range(min=1)),
            vol.Required(
                CONF_RECORDING_PATH,
                default=options.get(CONF_RECORDING_PATH, DEFAULT_RECORDING_PATH),
            ): str,
            vol.Required(
                CONF_MOTION_THRESHOLD,
                default=options.get(CONF_MOTION_THRESHOLD, DEFAULT_MOTION_THRESHOLD),
            ): vol.All(vol.Coerce(int), vol.Range(min=1, max=100)),
            vol.Required(
                CONF_MOTION_SAMPLE_INTERVAL,
                default=options.get(CONF_MOTION_SAMPLE_INTERVAL, DEFAULT_MOTION_SAMPLE_INTERVAL),
            ): vol.All(vol.Coerce(float), vol.Range(min=0.2, max=10)),
            vol.Required(
                CONF_MOTION_FLASH_HOLD_SECONDS,
                default=options.get(CONF_MOTION_FLASH_HOLD_SECONDS, DEFAULT_MOTION_FLASH_HOLD_SECONDS),
            ): vol.All(vol.Coerce(int), vol.Range(min=1, max=120)),
        })

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
        )
