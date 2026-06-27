from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .core import DOMAIN, NAME
from .core.device import (
    MASSAGE_LEVELS,
    MASSAGE_ZONE_NAMES,
    MASSAGE_ZONES,
    massage_level_from_percentage,
)
from .core.entity import XEntity


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, add_entities: AddEntitiesCallback
):
    device = hass.data[DOMAIN][config_entry.entry_id]

    add_entities([XMassageLevelSelect(device, zone) for zone in MASSAGE_ZONES])


class XMassageLevelSelect(XEntity, SelectEntity):
    _attr_icon = "mdi:vibrate"
    _attr_options = list(MASSAGE_LEVELS)

    def __init__(self, device, zone: str):
        self.zone = zone
        super().__init__(device, f"{zone}_level")

        zone_name = MASSAGE_ZONE_NAMES[zone]
        self._attr_name = f"{device.name or NAME} Мощность массажа {zone_name}"

    def internal_update(self):
        attribute = self.device.attribute(self.zone)

        self._attr_current_option = massage_level_from_percentage(
            attribute.get("percentage")
        )

        if self.hass:
            self._async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        self.device.set_attribute(self.zone, MASSAGE_LEVELS[option])
