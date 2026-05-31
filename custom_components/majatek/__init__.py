from __future__ import annotations

from aiohttp import web
from homeassistant.components.http import HomeAssistantView
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import CATEGORIES, CONF_CURRENCY, CONF_TOKEN, DEFAULT_CURRENCY, DOMAIN, PLATFORMS


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(
        "state",
        {
            "currency": DEFAULT_CURRENCY,
            "token": None,
            "status": None,
            "values": {key: None for key in CATEGORIES},
            "entities": {},
            "status_entity": None,
            "total_entity": None,
        },
    )
    hass.http.register_view(MajatekPostView(hass))
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    state = hass.data[DOMAIN]["state"]
    state["currency"] = entry.data.get(CONF_CURRENCY, DEFAULT_CURRENCY)
    state["token"] = entry.data.get(CONF_TOKEN)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


class MajatekPostView(HomeAssistantView):
    url = "/api/majatek"
    name = "api:majatek"
    requires_auth = False

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass

    async def post(self, request: web.Request) -> web.Response:
        state = self.hass.data[DOMAIN]["state"]
        configured_token = state.get("token")
        auth_header = request.headers.get("Authorization", "")

        if not configured_token:
            return web.json_response({"ok": False, "error": "token not configured"}, status=503)

        expected = f"Bearer {configured_token}"
        if auth_header != expected:
            return web.json_response({"ok": False, "error": "unauthorized"}, status=401)

        payload = await request.json()
        currency = payload.get(CONF_CURRENCY, state["currency"])
        state["currency"] = str(currency)

        for key in CATEGORIES:
            if key not in payload:
                continue
            try:
                state["values"][key] = float(payload[key])
            except (TypeError, ValueError):
                continue

        if "status" in payload:
            state["status"] = str(payload["status"])

        for entity in state["entities"].values():
            entity.async_write_ha_state()

        if state["total_entity"] is not None:
            state["total_entity"].async_write_ha_state()

        if state["status_entity"] is not None:
            state["status_entity"].async_write_ha_state()

        return web.json_response({
            "ok": True,
            "currency": state["currency"],
            "accepted_keys": sorted([key for key in CATEGORIES if key in payload]),
            "total": sum(v for v in state["values"].values() if isinstance(v, (int, float))),
        })
