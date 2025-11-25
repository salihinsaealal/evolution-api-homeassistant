"""Button platform for Evolution API."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.button import ButtonEntity, ButtonDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import EvolutionApiClient, EvolutionApiError
from .const import CONF_INSTANCE_ID, CONF_SERVER_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Evolution API buttons based on a config entry."""
    client: EvolutionApiClient = hass.data[DOMAIN][entry.entry_id]["client"]
    instance_id = entry.data[CONF_INSTANCE_ID]
    server_url = entry.data[CONF_SERVER_URL]

    async_add_entities(
        [
            RefreshGroupsButton(hass, client, entry, instance_id, server_url),
            RefreshConnectionButton(hass, client, entry, instance_id, server_url),
        ]
    )


class EvolutionApiButtonBase(ButtonEntity):
    """Base class for Evolution API buttons."""

    _attr_has_entity_name = True

    def __init__(
        self,
        hass: HomeAssistant,
        client: EvolutionApiClient,
        entry: ConfigEntry,
        instance_id: str,
        server_url: str,
    ) -> None:
        """Initialize the button."""
        self.hass = hass
        self._client = client
        self._entry = entry
        self._instance_id = instance_id
        self._server_url = server_url

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


class RefreshGroupsButton(EvolutionApiButtonBase):
    """Button to refresh groups list."""

    _attr_icon = "mdi:account-group-outline"
    _attr_name = "Refresh Groups"

    def __init__(
        self,
        hass: HomeAssistant,
        client: EvolutionApiClient,
        entry: ConfigEntry,
        instance_id: str,
        server_url: str,
    ) -> None:
        """Initialize the button."""
        super().__init__(hass, client, entry, instance_id, server_url)
        self._attr_unique_id = f"{entry.entry_id}_refresh_groups"

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            _LOGGER.info("Refreshing groups for instance %s", self._instance_id)
            groups = await self._client.fetch_all_groups(get_participants=False)
            
            entry_data = self.hass.data[DOMAIN][self._entry.entry_id]
            
            # Store groups in hass.data for other entities to use
            entry_data["groups"] = groups
            entry_data["groups_count"] = len(groups)
            
            # Save to persistent storage
            if "storage" in entry_data:
                await entry_data["storage"].async_save_groups(groups)
            
            # Fire event so other entities can update
            self.hass.bus.async_fire(
                f"{DOMAIN}_groups_updated",
                {"entry_id": self._entry.entry_id, "count": len(groups)},
            )
            
            _LOGGER.info("Found %d groups for instance %s", len(groups), self._instance_id)
        except EvolutionApiError as err:
            _LOGGER.error("Failed to refresh groups: %s", err)


class RefreshConnectionButton(EvolutionApiButtonBase):
    """Button to refresh connection status."""

    _attr_icon = "mdi:refresh"
    _attr_name = "Refresh Connection"
    _attr_device_class = ButtonDeviceClass.RESTART

    def __init__(
        self,
        hass: HomeAssistant,
        client: EvolutionApiClient,
        entry: ConfigEntry,
        instance_id: str,
        server_url: str,
    ) -> None:
        """Initialize the button."""
        super().__init__(hass, client, entry, instance_id, server_url)
        self._attr_unique_id = f"{entry.entry_id}_refresh_connection"

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            _LOGGER.info("Refreshing connection for instance %s", self._instance_id)
            info = await self._client.get_instance_info()
            
            # Store info in hass.data
            self.hass.data[DOMAIN][self._entry.entry_id]["instance_info"] = info
            
            # Fire event so sensor can update
            self.hass.bus.async_fire(
                f"{DOMAIN}_connection_updated",
                {"entry_id": self._entry.entry_id, "state": info.get("state")},
            )
            
            _LOGGER.info("Connection state: %s", info.get("state"))
        except EvolutionApiError as err:
            _LOGGER.error("Failed to refresh connection: %s", err)
