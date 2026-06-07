import voluptuous as vol
from homeassistant import config_entries
from .const import CONF_IP, CONF_NAME, DEFAULT_NAME, DOMAIN
from .util import test_camera

class LegacyCamConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

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
