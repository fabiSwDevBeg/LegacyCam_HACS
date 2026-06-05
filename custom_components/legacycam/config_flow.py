import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN
from .util import test_camera

class LegacyCamConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:

            ip_ok = await test_camera(user_input["ip"])

            if not ip_ok:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=user_input["name"],
                    data=user_input
                )

        schema = vol.Schema({
            vol.Required("name", default="LegacyCam"): str,
            vol.Required("ip"): str,
            vol.Required("clip_seconds", default=10): vol.All(vol.Coerce(int), vol.Range(5, 300)),
            vol.Required("retention_hours", default=3): vol.All(vol.Coerce(int), vol.Range(1, 168)),
            vol.Required("rotation", default=0): vol.In([0, 90, 180, 270]),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors
        )