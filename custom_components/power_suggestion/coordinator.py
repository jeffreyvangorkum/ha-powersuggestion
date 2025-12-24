"""Coordinator for Power Suggestion"""
import logging
from datetime import datetime, timedelta
import asyncio
from dataclasses import dataclass, asdict
import json

from homeassistant.core import HomeAssistant, callback
from homeassistant.components.recorder import history
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

@dataclass
class Cycle:
    """Represents a device cycle."""
    id: str
    name: str | None
    start: datetime
    end: datetime
    duration_minutes: float
    total_energy_kwh: float
    max_power_w: float
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "duration_minutes": self.duration_minutes,
            "total_energy_kwh": self.total_energy_kwh,
            "max_power_w": self.max_power_w
        }

class PowerSuggestionCoordinator:
    """Class to manage analysis and suggestions."""

    def __init__(self, hass: HomeAssistant, entry):
        self.hass = hass
        self.entry = entry
        self.device_name = entry.data["device_name"]
        self.power_entity = entry.data["power_entity"]
        self.cycles: list[Cycle] = []
        self._is_analyzing = False
        
        # Thresholds (could be configurable later)
        self.power_threshold_start = 5.0 # Watts
        self.power_threshold_end = 2.0 # Watts
        self.cycle_min_duration = 5 # Minutes

    async def async_analyze_history(self, days=30):
        """Analyze historical data from recorder."""
        if self._is_analyzing:
            _LOGGER.warning("Analysis already in progress")
            return

        self._is_analyzing = True
        _LOGGER.info(f"Starting analysis for {self.device_name} ({days} days)")
        
        start_time = dt_util.utcnow() - timedelta(days=days)
        end_time = dt_util.utcnow()

        def _get_history():
            return history.get_significant_states(
                self.hass,
                start_time,
                end_time,
                [self.power_entity],
                include_start_time_state=True,
                significant_changes_only=True,
            )

        history_data = await self.hass.async_add_executor_job(_get_history)
        
        entity_states = history_data.get(self.power_entity, [])
        if not entity_states:
            _LOGGER.warning(f"No history found for {self.power_entity}")
            self._is_analyzing = False
            return

        self.cycles = self._detect_cycles(entity_states)
        _LOGGER.info(f"Analysis complete. Found {len(self.cycles)} cycles.")
        self._is_analyzing = False

    def _detect_cycles(self, states) -> list[Cycle]:
        """Detect cycles from states."""
        cycles = []
        current_cycle_start = None
        max_power = 0
        energy_accumulator = 0 # Rude approximation
        
        # Simple finite state machine
        in_cycle = False
        
        for i in range(len(states) - 1):
            state = states[i]
            next_state = states[i+1]
            
            try:
                power = float(state.state)
            except (ValueError, TypeError):
                continue
                
            time_diff = (next_state.last_updated - state.last_updated).total_seconds() / 3600.0 # Hours
            
            if not in_cycle:
                if power > self.power_threshold_start:
                    in_cycle = True
                    current_cycle_start = state.last_updated
                    max_power = power
                    energy_accumulator = 0
            else:
                # Accumulate energy (Power * Time) = Wh
                energy_accumulator += (power * time_diff)
                if power > max_power:
                    max_power = power
                
                if power < self.power_threshold_end:
                    # Potential end of cycle
                    # Check if it stays low? For simplicity, we assume it ends here for now.
                    # A better approach uses a timeout buffer.
                    in_cycle = False
                    start_dt = current_cycle_start
                    end_dt = state.last_updated
                    duration_min = (end_dt - start_dt).total_seconds() / 60
                    
                    if duration_min >= self.cycle_min_duration:
                        cycle = Cycle(
                            id=f"{int(start_dt.timestamp())}",
                            name="Unknown Cycle",
                            start=start_dt,
                            end=end_dt,
                            duration_minutes=round(duration_min, 2),
                            total_energy_kwh=round(energy_accumulator / 1000.0, 3), # Wh to kWh
                            max_power_w=round(max_power, 2)
                        )
                        cycles.append(cycle)

        return cycles

    async def get_suggestion(self, cycle_id):
        """Generate a suggestion for a specific cycle."""
        # Find the cycle profile
        cycle = next((c for c in self.cycles if c.id == cycle_id), None)
        if not cycle:
            return None

        # Get solar forecast
        forecast_entity = self.entry.data["solar_forecast_entity"]
        
        # We need to get the state attributes of the forecast entity
        # forecast.solar usually has 'forecast' attribute with a list of dicts
        state = self.hass.states.get(forecast_entity)
        if not state:
            _LOGGER.warning("Solar forecast entity not available")
            return None
            
        # Example structure: attributes['forecast'] = [{'datetime': '...', 'watts': ...}, ...]
        forecast_data = state.attributes.get("forecast") # Check specific attribute name for integration
        if not forecast_data:
             # Try generic HA weather/forecast format? 
             # For now assume forecast_solar specific format or similar
             return None

        # Simple algorithm: find first time slot where forecast > average cycle power
        avg_power = (cycle.total_energy_kwh * 1000) / (cycle.duration_minutes / 60)
        
        best_start = None
        
        # This is a simplification. Real logic needs to verify the WHOLE duration.
        for point in forecast_data:
            watts = point.get("watts", 0) # or 'condition' mapped to watts
            ts_str = point.get("datetime") # ISO string
            if not ts_str:
                continue
            
            ts = datetime.fromisoformat(ts_str)
            if ts < dt_util.utcnow():
                continue

            if watts > avg_power:
                # Check if it sustains for duration?
                # Optimization: For now just return first matching time
                best_start = ts
                break
        
        if best_start:
            return {
                "cycle_id": cycle.id,
                "suggestion_time": best_start.isoformat(),
                "reason": "High solar forecast"
            }
        
        return None

    def get_cycles(self):
        """Return list of detected cycles."""
        return [c.to_dict() for c in self.cycles]
