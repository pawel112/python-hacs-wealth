from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CATEGORIES, DEVICE_ID, DEVICE_NAME, DOMAIN, MANUFACTURER, MODEL, TOTAL_KEY, TOTAL_NAME


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    state = hass.data[DOMAIN]["state"]
    entities = []

    for key, label in CATEGORIES.items():
        entity = MajatekValueSensor(hass, key, label)
        state["entities"][key] = entity
        entities.append(entity)

    total_entity = MajatekTotalSensor(hass)
    state["total_entity"] = total_entity
    entities.append(total_entity)

    status_entity = MajatekStatusSensor(hass)
    state["status_entity"] = status_entity
    entities.append(status_entity)

    async_add_entities(entities)


class MajatekBaseEntity(SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, DEVICE_ID)},
            name=DEVICE_NAME,
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def available(self) -> bool:
        return True

    @property
    def _state(self) -> dict:
        return self.hass.data[DOMAIN]["state"]


class MajatekValueSensor(MajatekBaseEntity):
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_icon = "mdi:cash-multiple"

    def __init__(self, hass: HomeAssistant, key: str, label: str) -> None:
        super().__init__(hass)
        self.key = key
        self._attr_name = label
        self._attr_unique_id = f"{DEVICE_ID}_{key}"

    @property
    def native_value(self):
        return self._state["values"].get(self.key)

    @property
    def native_unit_of_measurement(self):
        return self._state["currency"]

    @property
    def extra_state_attributes(self):
        return {"category_key": self.key}


class MajatekTotalSensor(MajatekBaseEntity):
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_icon = "mdi:calculator"
    _attr_name = TOTAL_NAME
    _attr_unique_id = f"{DEVICE_ID}_{TOTAL_KEY}"

    @property
    def native_value(self):
        values = self._state["values"].values()
        total = sum(value for value in values if isinstance(value, (int, float)))
        return round(total, 2)

    @property
    def native_unit_of_measurement(self):
        return self._state["currency"]


class MajatekStatusSensor(MajatekBaseEntity):
    _attr_name = "Status"
    _attr_unique_id = f"{DEVICE_ID}_status"
    _attr_icon = "mdi:text-box-check-outline"

    @property
    def native_value(self):
        return self._state["status"]
