from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er

from .core import DOMAIN
from .core.device import Device

PLATFORMS = ["binary_sensor", "button", "cover", "light", "select", "switch"]
LEGACY_MASSAGE_FAN_ATTRIBUTES = ("head_massage", "foot_massage")


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    devices = hass.data.setdefault(DOMAIN, {})
    _async_cleanup_legacy_massage_fans(hass, entry.data["mac"])

    @callback
    def update_ble(
        service_info: bluetooth.BluetoothServiceInfoBleak,
        change: bluetooth.BluetoothChange,
    ) -> None:
        if devices.get(entry.entry_id):
            return

        devices[entry.entry_id] = Device(entry.title, service_info.device)

        async def setup_platforms() -> None:
            await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
            _async_cleanup_legacy_massage_fans(
                hass, service_info.device.address
            )

        hass.create_task(setup_platforms())

    # https://developers.home-assistant.io/docs/core/bluetooth/api/
    entry.async_on_unload(
        bluetooth.async_register_callback(
            hass,
            update_ble,
            {"address": entry.data["mac"], "connectable": True},
            bluetooth.BluetoothScanningMode.ACTIVE,
        )
    )

    return True


@callback
def _async_cleanup_legacy_massage_fans(
    hass: HomeAssistant, mac_address: str
) -> None:
    registry = er.async_get(hass)
    mac = mac_address.replace(":", "").lower()
    legacy_unique_ids = {
        f"{mac}_{attr}" for attr in LEGACY_MASSAGE_FAN_ATTRIBUTES
    }

    for entity_id, entity_entry in list(registry.entities.items()):
        if not entity_id.startswith("fan."):
            continue
        if entity_entry.platform != DOMAIN:
            continue
        if entity_entry.unique_id.lower() not in legacy_unique_ids:
            continue

        registry.async_remove(entity_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    if entry.entry_id not in hass.data[DOMAIN]:
        return True

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
