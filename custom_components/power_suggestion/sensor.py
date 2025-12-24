"""Sensors for Power Suggestion"""
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_DEVICE_NAME

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Power Suggestion sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        PowerSuggestionSensor(coordinator, entry),
    ]
    async_add_entities(entities)

class PowerSuggestionSensor(SensorEntity):
    """Representation of a Power Suggestion Status Sensor."""

    def __init__(self, coordinator, entry):
        self._coordinator = coordinator
        self._entry = entry
        self._attr_name = f"{entry.data[CONF_DEVICE_NAME]} Suggestion"
        self._attr_unique_id = f"{entry.entry_id}_suggestion"
        self._attr_icon = "mdi:washing-machine" # Default logic could improve this

    @property
    def state(self):
        """Return the state of the sensor."""
        return len(self._coordinator.cycles)

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "cycles_detected": self._coordinator.get_cycles(),
            "analyzing": self._coordinator._is_analyzing
        }

    async def async_update(self):
        """Update the sensor."""
        # This sensor state is largely pushed by the coordinator or actions
        pass
