from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .core import DOMAIN
from .core.device import SCENE_OPTIONS
from .core.entity import XEntity


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, add_entities: AddEntitiesCallback
):
    device = hass.data[DOMAIN][config_entry.entry_id]

    add_entities([XSceneButton(device, scene) for scene in SCENE_OPTIONS])


class XSceneButton(XEntity, ButtonEntity):
    _attr_icon = "mdi:bed"

    def __init__(self, device, scene: str):
        self.scene = scene
        super().__init__(device, f"scene_{scene}")

    def internal_update(self):
        return

    async def async_press(self) -> None:
        self.device.set_attribute("scene", self.scene)
