"""Media Player platform for Evolution API."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerDeviceClass,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

# Import the helper from your existing __init__.py
from . import get_media_content
from .api import EvolutionApiClient, EvolutionApiError
from .const import CONF_INSTANCE_ID, CONF_SERVER_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Evolution API media player."""
    client: EvolutionApiClient = hass.data[DOMAIN][entry.entry_id]["client"]
    instance_id = entry.data[CONF_INSTANCE_ID]
    server_url = entry.data[CONF_SERVER_URL]

    async_add_entities(
        [EvolutionApiMediaPlayer(hass, client, entry, instance_id, server_url)]
    )


class EvolutionApiMediaPlayer(MediaPlayerEntity):
    """Representation of the Evolution API Instance as a Media Player."""

    _attr_has_entity_name = True
    _attr_name = "Voice Speaker"
    _attr_icon = "mdi:whatsapp"
    _attr_device_class = MediaPlayerDeviceClass.SPEAKER
    _attr_supported_features = MediaPlayerEntityFeature.PLAY_MEDIA

    def __init__(
        self,
        hass: HomeAssistant,
        client: EvolutionApiClient,
        entry: ConfigEntry,
        instance_id: str,
        server_url: str,
    ) -> None:
        """Initialize the media player."""
        self.hass = hass
        self._client = client
        self._entry = entry
        self._default_instance_id = instance_id
        self._server_url = server_url
        self._attr_unique_id = f"{entry.entry_id}_mediaplayer"
        self._attr_state = MediaPlayerState.IDLE

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=f"Evolution API ({self._default_instance_id})",
            manufacturer="Evolution API",
            model="WhatsApp Instance",
            configuration_url=self._server_url,
        )

    @property
    def state(self) -> MediaPlayerState:
        """Return the state of the device."""
        return self._attr_state

    # Supported media types for audio sending
    SUPPORTED_MEDIA_TYPES = {"music", "audio", "voice", "sound"}

    async def async_play_media(
        self, media_type: str, media_id: str, **kwargs: Any
    ) -> None:
        """Play media (Send Audio to WhatsApp).
        
        Note: This media player only supports audio content. The media_type
        parameter is validated but the actual content is always sent as audio.
        
        Required in 'extra':
            - target: WhatsApp phone number or Group JID
        Optional in 'extra':
            - instance_id: Override the default Evolution API instance
        """
        # Validate media_type (warn but proceed for flexibility)
        if media_type and media_type.lower() not in self.SUPPORTED_MEDIA_TYPES:
            _LOGGER.warning(
                "Media type '%s' is not in supported types %s. "
                "This media player only sends audio to WhatsApp. Proceeding anyway.",
                media_type, self.SUPPORTED_MEDIA_TYPES
            )
        
        # 1. Extract Target & Instance from 'extra' data
        extra = kwargs.get("extra", {})
        target = extra.get("target")
        instance_override = extra.get("instance_id")

        if not target:
            _LOGGER.error(
                "Missing 'target'. Please provide 'extra: target: <phone_or_group>' in your service call. "
                "Example: extra: { target: '1234567890' }"
            )
            return

        _LOGGER.debug(
            "Sending audio to %s via instance %s (media_type: %s)", 
            target, instance_override or self._default_instance_id, media_type
        )
        self._attr_state = MediaPlayerState.PLAYING
        self.async_write_ha_state()

        try:
            # 2. Resolve the media (handle local files, TTS URLs, media-source://)
            processed_audio = await get_media_content(self.hass, media_id)
            
            if not processed_audio:
                _LOGGER.error("Failed to process audio URL: %s", media_id)
                self._attr_state = MediaPlayerState.IDLE
                self.async_write_ha_state()
                return

            # 3. Send via API (passing target, audio, and optional instance override)
            await self._client.send_audio(
                number=target,
                audio_url=processed_audio,
                instance_id=instance_override
            )
        except EvolutionApiError as err:
            _LOGGER.error("Failed to send audio via media player: %s", err)
            self._attr_state = MediaPlayerState.IDLE
            self.async_write_ha_state()
            return
        except Exception as err:
            _LOGGER.error("Unexpected error in media player: %s", err)
            self._attr_state = MediaPlayerState.IDLE
            self.async_write_ha_state()
            return

        # Return to idle immediately as it's a push operation
        self._attr_state = MediaPlayerState.IDLE
        self.async_write_ha_state()