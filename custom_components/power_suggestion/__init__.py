"""The Power Suggestion integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import PowerSuggestionCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Power Suggestion from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    coordinator = PowerSuggestionCoordinator(hass, entry)
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # Trigger initial analysis in background? or wait for user?
    # For now, let's trigger it so data appears
    hass.async_create_task(coordinator.async_analyze_history())

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    async def handle_analyze(call):
        """Handle analysis service."""
        # Find entry? Or iterate all?
        # For simplicity, we analyze all or filter by device_id
        for entry_id, coordinator in hass.data[DOMAIN].items():
            await coordinator.async_analyze_history()

    async def handle_suggestion(call) -> dict:
        """Handle suggestion service."""
        cycle_id = call.data.get("cycle_id")
        # Logic to find the correct coordinator could be improved (e.g. pass entity_id)
        # Just searching first match for now
        for entry_id, coordinator in hass.data[DOMAIN].items():
            suggestion = await coordinator.get_suggestion(cycle_id)
            if suggestion:
                return suggestion
        return {"error": "No suggestion found"}

    hass.services.async_register(DOMAIN, "analyze_device", handle_analyze)
    hass.services.async_register(
        DOMAIN, 
        "get_suggestion", 
        handle_suggestion,
        supports_response=any
    )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        # Clean up data
        pass
        # hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
