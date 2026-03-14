"""Family Clock — Home Assistant Integration."""
from __future__ import annotations

import logging
import pathlib

from homeassistant.components.http import HomeAssistantView
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

DOMAIN = "family_clock"
STORAGE_KEY = "family_clock_schedule"
STORAGE_VERSION = 1


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Stub — setup happens via config entry."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Family Clock from a config entry."""

    # Serve the www folder under /local/family_clock/
    www_path = pathlib.Path(__file__).parent / "www"
    hass.http.register_static_path(
        "/local/family_clock", str(www_path), cache_headers=False
    )

    # Register sidebar panel
    hass.components.frontend.async_register_built_in_panel(
        component_name="iframe",
        sidebar_title="Family Clock",
        sidebar_icon="mdi:clock-outline",
        frontend_url_path="family-clock",
        config={"url": "/local/family_clock/family-clock.html"},
        require_admin=False,
    )

    # Register REST API
    store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
    hass.http.register_view(FamilyClockScheduleView(store))

    _LOGGER.info("Family Clock loaded — panel at /family-clock")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Family Clock config entry."""
    hass.components.frontend.async_remove_panel("family-clock")
    return True


class FamilyClockScheduleView(HomeAssistantView):
    """Handle schedule read/write via REST API."""

    url = "/api/family_clock/schedule"
    name = "api:family_clock:schedule"
    requires_auth = True

    def __init__(self, store: Store) -> None:
        self._store = store

    async def get(self, request):
        data = await self._store.async_load() or {}
        return self.json(data)

    async def post(self, request):
        try:
            body = await request.json()
        except Exception:
            return self.json_message("Invalid JSON", status_code=400)
        await self._store.async_save(body)
        return self.json({"status": "ok"})
