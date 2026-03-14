"""Family Clock — Home Assistant Integration."""
from __future__ import annotations

import logging
import pathlib

from homeassistant.components import frontend
from homeassistant.components.http import HomeAssistantView, StaticPathConfig
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
    await hass.http.async_register_static_paths(
        [StaticPathConfig("/local/family_clock", str(www_path), cache_headers=False)]
    )

    # Register sidebar panel
    frontend.async_register_built_in_panel(
        hass,
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
    hass.http.register_view(FamilyClockEntitiesView(hass))

    # Log available persons and zones so issues are visible in HA logs
    persons = [s.entity_id for s in hass.states.async_all() if s.entity_id.startswith("person.")]
    zones = [s.entity_id for s in hass.states.async_all() if s.entity_id.startswith("zone.")]
    _LOGGER.info("Family Clock loaded — panel at /family-clock")
    _LOGGER.info("Family Clock: found %d person(s): %s", len(persons), persons)
    _LOGGER.info("Family Clock: found %d zone(s): %s", len(zones), zones)
    if not persons:
        _LOGGER.warning(
            "Family Clock: no person.* entities found at startup — "
            "make sure the 'Person' integration is configured in Home Assistant"
        )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Family Clock config entry."""
    frontend.async_remove_panel(hass, "family-clock")
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


class FamilyClockEntitiesView(HomeAssistantView):
    """Return person and zone entities directly from HA state machine."""

    url = "/api/family_clock/entities"
    name = "api:family_clock:entities"
    requires_auth = True

    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass

    async def get(self, request):
        persons = [
            {
                "entity_id": s.entity_id,
                "state": s.state,
                "attributes": dict(s.attributes),
            }
            for s in self._hass.states.async_all()
            if s.entity_id.startswith("person.")
        ]
        zones = [
            {
                "entity_id": s.entity_id,
                "state": s.state,
                "attributes": dict(s.attributes),
            }
            for s in self._hass.states.async_all()
            if s.entity_id.startswith("zone.")
        ]
        _LOGGER.debug(
            "Family Clock /entities requested — returning %d person(s), %d zone(s)",
            len(persons),
            len(zones),
        )
        if not persons:
            _LOGGER.warning(
                "Family Clock /entities: no person.* entities found in state machine"
            )
        return self.json({"persons": persons, "zones": zones})
