import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN

class LegacyCamConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title=f"LegacyCam {user_input['ip']}",
                data=user_input
            )

        schema = vol.Schema({
            vol.Required("ip"): str,

            vol.Required("clip_seconds", default=10): vol.All(
                vol.Coerce(int),
                vol.Range(min=5, max=300)
            ),

            vol.Required("retention_hours", default=3): vol.All(
                vol.Coerce(int),
                vol.Range(min=1, max=168)
            ),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema
        )