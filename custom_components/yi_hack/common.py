"""Common utils for yi-hack cam."""

from datetime import timedelta
import logging

import requests
from requests.auth import HTTPBasicAuth

from homeassistant.const import (
    CONF_HOST,
    CONF_MAC,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import (
    CONNECTION_NETWORK_MAC,
    DeviceInfo,
)
from homeassistant.util import dt as dt_util

from .const import (
    CONF_FIRMWARE_VERSION,
    CONF_HACK_NAME,
    CONF_HARDWARE_VERSION,
    CONF_MODEL,
    CONF_SERIAL,
    DEFAULT_BRAND,
    DOMAIN,
    HTTP_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)


def get_device_info(config_entry: ConfigEntry) -> DeviceInfo:
    """Build device registry information for a camera."""
    data = config_entry.data
    host = data[CONF_HOST]
    port = data[CONF_PORT]
    configuration_url = f"http://{host}"
    if port != 80:
        configuration_url += f":{port}"

    device_info = DeviceInfo(
        name=data[CONF_NAME],
        connections={(CONNECTION_NETWORK_MAC, data[CONF_MAC])},
        identifiers={(DOMAIN, data[CONF_MAC])},
        manufacturer=DEFAULT_BRAND,
        model=data.get(CONF_MODEL, data.get(CONF_HACK_NAME, DOMAIN)),
        configuration_url=configuration_url,
    )

    optional_fields = {
        "serial_number": data.get(CONF_SERIAL),
        "sw_version": data.get(CONF_FIRMWARE_VERSION),
        "hw_version": data.get(CONF_HARDWARE_VERSION),
    }
    for key, value in optional_fields.items():
        if value not in (None, "", "N/A"):
            device_info[key] = value

    return device_info


def get_status(config):
    """Get system status from camera."""
    host = config[CONF_HOST]
    port = config[CONF_PORT]
    user = config[CONF_USERNAME]
    password = config[CONF_PASSWORD]
    error = False

    auth = None
    if user or password:
        auth = HTTPBasicAuth(user, password)

    response = None
    try:
        response = requests.get("http://" + host + ":" + str(port) + "/cgi-bin/status.json", timeout=HTTP_TIMEOUT, auth=auth)
        if response.status_code >= 300:
            _LOGGER.error("Failed to get status from device %s", host)
            error = True
    except requests.exceptions.RequestException as e:
        _LOGGER.error("Failed to get status from device %s: error %s", host, e)
        error = True

    if error:
        response = None
        return None

    return response.json()

def get_system_conf(config):
    """Get system configuration from camera."""
    host = config[CONF_HOST]
    port = config[CONF_PORT]
    user = config[CONF_USERNAME]
    password = config[CONF_PASSWORD]
    error = False

    auth = None
    if user or password:
        auth = HTTPBasicAuth(user, password)

    response = None
    try:
        response = requests.get("http://" + host + ":" + str(port) + "/cgi-bin/get_configs.sh?conf=system", timeout=HTTP_TIMEOUT, auth=auth)
        if response.status_code >= 300:
            _LOGGER.error("Failed to get system configuration from device %s", host)
            error = True
    except requests.exceptions.RequestException as e:
        _LOGGER.error("Failed to get system configuration from device %s: error %s", host, e)
        error = True

    if error:
        response = None
        return None

    return response.json()

def get_mqtt_conf(config):
    """Get mqtt configuration from camera."""
    host = config[CONF_HOST]
    port = config[CONF_PORT]
    user = config[CONF_USERNAME]
    password = config[CONF_PASSWORD]
    error = False

    auth = None
    if user or password:
        auth = HTTPBasicAuth(user, password)

    response = None
    try:
        response = requests.get("http://" + host + ":" + str(port) + "/cgi-bin/get_configs.sh?conf=mqtt", timeout=HTTP_TIMEOUT, auth=auth)
        if response.status_code >= 300:
            _LOGGER.error("Failed to get mqtt configuration from device %s", host)
            error = True
    except requests.exceptions.RequestException as e:
        _LOGGER.error("Failed to get mqtt configuration from device %s: error %s", host, e)
        error = True

    if error:
        response = None
        return None

    return response.json()
