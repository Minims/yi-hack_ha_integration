"""Support for yi-hack camera buttons."""

from __future__ import annotations

import logging

import requests
from requests.auth import HTTPBasicAuth

from homeassistant.components.button import ButtonDeviceClass, ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_MAC,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DEFAULT_BRAND, DOMAIN, HTTP_TIMEOUT

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the yi-hack camera buttons."""
    async_add_entities([YiHackRestartButton(config_entry)])


class YiHackRestartButton(ButtonEntity):
    """Button that restarts a yi-hack camera."""

    _attr_device_class = ButtonDeviceClass.RESTART
    _attr_entity_category = EntityCategory.CONFIG
    _attr_has_entity_name = True

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize the restart button."""
        self._host = config_entry.data[CONF_HOST]
        self._port = config_entry.data[CONF_PORT]
        self._username = config_entry.data[CONF_USERNAME]
        self._password = config_entry.data[CONF_PASSWORD]

        mac = config_entry.data[CONF_MAC]
        device_name = config_entry.data[CONF_NAME]
        configuration_url = f"http://{self._host}"
        if self._port != 80:
            configuration_url += f":{self._port}"

        self._attr_unique_id = f"{mac}_restart"
        self._attr_device_info = {
            "name": device_name,
            "connections": {(CONNECTION_NETWORK_MAC, mac)},
            "identifiers": {(DOMAIN, mac)},
            "manufacturer": DEFAULT_BRAND,
            "model": DOMAIN,
            "configuration_url": configuration_url,
        }

    def press(self) -> None:
        """Restart the camera."""
        auth = None
        if self._username or self._password:
            auth = HTTPBasicAuth(self._username, self._password)

        try:
            response = requests.get(
                f"http://{self._host}:{self._port}/cgi-bin/reboot.sh",
                timeout=HTTP_TIMEOUT,
                auth=auth,
            )
            if response.status_code >= 300:
                _LOGGER.error(
                    "Failed to send restart command to device %s", self._host
                )
        except requests.exceptions.RequestException as error:
            _LOGGER.error(
                "Failed to send restart command to device %s: %s",
                self._host,
                error,
            )
