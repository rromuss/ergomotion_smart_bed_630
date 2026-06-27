from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .core import DOMAIN, NAME
from .core.device import (
    MASSAGE_ZONE_NAMES,
    MASSAGE_ZONES,
    SCENE_OPTIONS,
    TIMER_OPTIONS,
)
from .core.entity import XEntity


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, add_entities: AddEntitiesCallback
):
    device = hass.data[DOMAIN][config_entry.entry_id]

    add_entities(
        [XSceneButton(device, scene) for scene in SCENE_OPTIONS]
        + [
            XMassageTimerButton(device, zone, timer)
            for zone in MASSAGE_ZONES
            for timer in TIMER_OPTIONS
        ]
    )


class XSceneButton(XEntity, ButtonEntity):
    _attr_icon = "mdi:bed"

    def __init__(self, device, scene: str):
        self.scene = scene
        super().__init__(device, f"scene_{scene}")

    def internal_update(self):
        return

    async def async_press(self) -> None:
        self.device.set_attribute("scene", self.scene)


class XMassageTimerButton(XEntity, ButtonEntity):
    _attr_icon = "mdi:timer-play-outline"

    def __init__(self, device, zone: str, timer: str):
        self.zone = zone
        self.timer = timer
        super().__init__(device, f"{zone}_timer_{timer}")

        zone_name = MASSAGE_ZONE_NAMES[zone]
        self._attr_name = (
            f"{device.name or NAME} Таймер массажа {zone_name} {timer} минут"
        )

    def internal_update(self):
        return

    async def async_press(self) -> None:
        self.device.start_massage_timer(self.zone, self.timer)
