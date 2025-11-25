"""Persistent storage for Evolution API integration."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STORAGE_VERSION = 1
STORAGE_KEY = f"{DOMAIN}_data"


class EvolutionApiStorage:
    """Handle persistent storage for Evolution API data."""

    def __init__(self, hass: HomeAssistant, entry_id: str) -> None:
        """Initialize storage."""
        self.hass = hass
        self.entry_id = entry_id
        self._store = Store(hass, STORAGE_VERSION, f"{STORAGE_KEY}_{entry_id}")
        self._data: dict[str, Any] = {}
        self._loaded = False

    async def async_load(self) -> dict[str, Any]:
        """Load data from storage."""
        if self._loaded:
            return self._data

        stored = await self._store.async_load()
        if stored:
            self._data = stored
            _LOGGER.debug("Loaded Evolution API data from storage: %s keys", len(self._data))
        else:
            self._data = self._get_default_data()
            _LOGGER.debug("No stored data found, using defaults")

        self._loaded = True
        return self._data

    def _get_default_data(self) -> dict[str, Any]:
        """Get default data structure."""
        return {
            "groups": [],
            "groups_count": 0,
            "groups_last_updated": None,
            "connection_state": "unknown",
            "connection_last_updated": None,
            "instance_info": {},
        }

    async def async_save(self) -> None:
        """Save data to storage."""
        await self._store.async_save(self._data)
        _LOGGER.debug("Saved Evolution API data to storage")

    async def async_save_groups(self, groups: list[dict[str, Any]]) -> None:
        """Save groups data."""
        self._data["groups"] = groups
        self._data["groups_count"] = len(groups)
        self._data["groups_last_updated"] = dt_util.now().isoformat()
        await self.async_save()
        _LOGGER.info("Saved %d groups to storage", len(groups))

    async def async_save_connection_state(self, state: str, instance_info: dict[str, Any] | None = None) -> None:
        """Save connection state."""
        self._data["connection_state"] = state
        self._data["connection_last_updated"] = dt_util.now().isoformat()
        if instance_info:
            self._data["instance_info"] = instance_info
        await self.async_save()

    def get_groups(self) -> list[dict[str, Any]]:
        """Get stored groups."""
        return self._data.get("groups", [])

    def get_groups_count(self) -> int:
        """Get stored groups count."""
        return self._data.get("groups_count", 0)

    def get_groups_last_updated(self) -> str | None:
        """Get last updated timestamp for groups."""
        return self._data.get("groups_last_updated")

    def get_connection_state(self) -> str:
        """Get stored connection state."""
        return self._data.get("connection_state", "unknown")

    def get_instance_info(self) -> dict[str, Any]:
        """Get stored instance info."""
        return self._data.get("instance_info", {})

    async def async_reset(self) -> None:
        """Reset storage to defaults."""
        self._data = self._get_default_data()
        await self.async_save()
        _LOGGER.info("Reset Evolution API storage to defaults")
