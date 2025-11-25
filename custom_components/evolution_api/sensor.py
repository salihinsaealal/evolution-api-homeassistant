"""Sensor platform for Evolution API."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import EvolutionApiClient, EvolutionApiError
from .const import CONF_INSTANCE_ID, CONF_SERVER_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=1)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Evolution API sensor based on a config entry."""
    client: EvolutionApiClient = hass.data[DOMAIN][entry.entry_id]["client"]
    instance_id = entry.data[CONF_INSTANCE_ID]
    server_url = entry.data[CONF_SERVER_URL]

    coordinator = EvolutionApiCoordinator(hass, client, instance_id)
    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        [
            EvolutionApiConnectionSensor(coordinator, entry, instance_id, server_url),
        ]
    )


class EvolutionApiCoordinator(DataUpdateCoordinator):
    """Coordinator to manage Evolution API data updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: EvolutionApiClient,
        instance_id: str,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"Evolution API {instance_id}",
            update_interval=SCAN_INTERVAL,
        )
        self.client = client
        self.instance_id = instance_id

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from Evolution API."""
        try:
            connection_state = await self.client.get_connection_state()
            return {
                "state": connection_state.get("instance", {}).get("state", "unknown"),
                "instance": connection_state.get("instance", {}),
            }
        except EvolutionApiError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err


class EvolutionApiConnectionSensor(CoordinatorEntity, SensorEntity):
    """Sensor showing the connection status of the WhatsApp instance."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:whatsapp"

    def __init__(
        self,
        coordinator: EvolutionApiCoordinator,
        entry: ConfigEntry,
        instance_id: str,
        server_url: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_connection_status"
        self._attr_name = "Connection Status"
        self._instance_id = instance_id
        self._server_url = server_url
        self._entry = entry

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=f"Evolution API ({self._instance_id})",
            manufacturer="Evolution API",
            model="WhatsApp Instance",
            configuration_url=self._server_url,
        )

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        if self.coordinator.data:
            state = self.coordinator.data.get("state", "unknown")
            return state.lower()
        return "unknown"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        if self.coordinator.data:
            instance_data = self.coordinator.data.get("instance", {})
            return {
                "instance_id": self._instance_id,
                "server_url": self._server_url,
                "owner": instance_data.get("owner", ""),
                "profile_name": instance_data.get("profileName", ""),
                "profile_picture": instance_data.get("profilePictureUrl", ""),
            }
        return {
            "instance_id": self._instance_id,
            "server_url": self._server_url,
        }

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success
