"""Family Clock - Home Assistant Integration."""
from __future__ import annotations

import json
import logging
import os

from homeassistant.components.http import HomeAssistantView
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

DOMAIN = "family_clock"
STORAGE_KEY = "family_clock_schedule"
STORAGE_VERSION = 1


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Family Clock integration."""

    # Register the frontend panel
    hass.components.frontend.async_register_built_in_panel(
        component_name="iframe",
        sidebar_title="Family Clock",
        sidebar_icon="mdi:clock-outline",
        frontend_url_path="family-clock",
        config={"url": "/local/family_clock/family-clock.html"},
        require_admin=False,
    )

    # Register API views
    hass.http.register_view(FamilyClockScheduleView(hass))

    _LOGGER.info("Family Clock integration loaded")
    return True


class FamilyClockScheduleView(HomeAssistantView):
    """Handle schedule read/write via REST API."""

    url = "/api/family_clock/schedule"
    name = "api:family_clock:schedule"
    requires_auth = True

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize."""
        self.hass = hass
        self._store = hass.helpers.storage.Store(
            STORAGE_VERSION, STORAGE_KEY
        )

    async def get(self, request):
        """Return the current schedule."""
        data = await self._store.async_load() or {}
        return self.json(data)

    async def post(self, request):
        """Save the schedule."""
        try:
            body = await request.json()
        except Exception:
            return self.json_message("Invalid JSON", status_code=400)

        await self._store.async_save(body)
        return self.json({"status": "ok"})
