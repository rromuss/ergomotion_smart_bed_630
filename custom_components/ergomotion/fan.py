from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .core import DOMAIN
from .core.entity import XEntity

DEFAULT_MASSAGE_PERCENTAGE = 50
SPEED_COUNT = 6


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, add_entities: AddEntitiesCallback
):
    device = hass.data[DOMAIN][config_entry.entry_id]

    add_entities([XFan(device, "head_massage"), XFan(device, "foot_massage")])


class XFan(XEntity, FanEntity):
    _attr_speed_count = SPEED_COUNT
    _attr_supported_features = (
        FanEntityFeature.SET_SPEED
        | FanEntityFeature.PRESET_MODE
        | FanEntityFeature.TURN_ON
        | FanEntityFeature.TURN_OFF
    )

    def internal_update(self):
        attribute = self.device.attribute(self.attr)

        percentage = attribute.get("percentage")

        self._attr_is_on = bool(percentage)
        self._attr_percentage = percentage
        self._attr_preset_mode = attribute.get("current")
        self._attr_preset_modes = attribute.get("options")

        if self.hass:
            self._async_write_ha_state()

    async def async_turn_on(
        self, percentage: int = None, preset_mode: str = None, **kwargs
    ) -> None:
        if percentage is None:
            percentage = DEFAULT_MASSAGE_PERCENTAGE

        await self.async_set_percentage(percentage)

        if preset_mode:
            await self.async_set_preset_mode(preset_mode)

    async def async_turn_off(self) -> None:
        self.device.set_attribute(self.attr, 0)

    async def async_set_percentage(self, percentage: int) -> None:
        if percentage <= 0:
            percentage = 0
        else:
            speed = max(1, round(percentage / 100 * SPEED_COUNT))
            percentage = int(speed / SPEED_COUNT * 100)

        self.device.set_attribute(self.attr, percentage)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        self.device.set_attribute("timer_target", preset_mode)
