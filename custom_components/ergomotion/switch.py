from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .core import DOMAIN, NAME
from .core.device import (
    DEFAULT_MASSAGE_PERCENTAGE,
    MASSAGE_ZONE_NAMES,
    MASSAGE_ZONES,
)
from .core.entity import XEntity


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, add_entities: AddEntitiesCallback
):
    device = hass.data[DOMAIN][config_entry.entry_id]

    add_entities([XMassageSwitch(device, zone) for zone in MASSAGE_ZONES])


class XMassageSwitch(XEntity, SwitchEntity):
    _attr_icon = "mdi:vibrate"

    def __init__(self, device, zone: str):
        self.zone = zone
        super().__init__(device, f"{zone}_switch")

        zone_name = MASSAGE_ZONE_NAMES[zone]
        self._attr_name = f"{device.name or NAME} Массаж {zone_name}"

    def internal_update(self):
        attribute = self.device.attribute(self.zone)

        self._attr_is_on = bool(attribute.get("percentage"))

        if self.hass:
            self._async_write_ha_state()

    async def async_turn_on(self, **kwargs) -> None:
        self.device.set_attribute(self.zone, DEFAULT_MASSAGE_PERCENTAGE)

    async def async_turn_off(self, **kwargs) -> None:
        self.device.set_attribute(self.zone, 0)
