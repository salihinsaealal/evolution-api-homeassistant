"""The Evolution API integration."""
from __future__ import annotations

import logging
import os
import base64
import mimetypes
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

PLATFORMS = [Platform.SENSOR, Platform.BUTTON, Platform.MEDIA_PLAYER]

from .api import EvolutionApiClient, EvolutionApiError
from .storage import EvolutionApiStorage
from .const import (
    ATTR_AUDIO_URL,
    ATTR_CONTACT_EMAIL,
    ATTR_CONTACT_NAME,
    ATTR_CONTACT_ORG,
    ATTR_CONTACT_PHONE,
    ATTR_DELAY,
    ATTR_FILENAME,
    ATTR_GROUP_ID,
    ATTR_LATITUDE,
    ATTR_LINK_PREVIEW,
    ATTR_LOCATION_ADDRESS,
    ATTR_LOCATION_NAME,
    ATTR_LONGITUDE,
    ATTR_MEDIA_CAPTION,
    ATTR_MEDIA_TYPE,
    ATTR_MEDIA_URL,
    ATTR_MENTION_ALL,
    ATTR_MESSAGE,
    ATTR_MESSAGE_ID,
    ATTR_PHONE_NUMBER,
    ATTR_TARGET, # <--- NEW
    ATTR_INSTANCE_ID, # <--- NEW
    ATTR_POLL_MAX_SELECTIONS,
    ATTR_POLL_NAME,
    ATTR_POLL_OPTIONS,
    ATTR_REACTION,
    ATTR_STICKER_URL,
    CONF_API_KEY,
    CONF_INSTANCE_ID,
    CONF_SERVER_URL,
    CONF_VERIFY_SSL,
    DEFAULT_VERIFY_SSL,
    DOMAIN,
    SERVICE_CHECK_NUMBER,
    SERVICE_SEND_AUDIO,
    SERVICE_SEND_CONTACT,
    SERVICE_SEND_LOCATION,
    SERVICE_SEND_MEDIA,
    SERVICE_SEND_POLL,
    SERVICE_SEND_REACTION,
    SERVICE_SEND_STICKER,
    SERVICE_SEND_TEXT,
)

SERVICE_REFRESH_GROUPS = "refresh_groups"

_LOGGER = logging.getLogger(__name__)

# --- ADDED: Helper to read local files as Base64 ---
def encode_file(file_path):
    """Reads a local file and converts it to a Raw Base64 string."""
    try:
        if not os.path.exists(file_path):
            _LOGGER.error(f"File not found: {file_path}")
            return None
        with open(file_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        _LOGGER.error(f"Error reading file {file_path}: {e}")
        return None

# --- ADDED: Smart Media Resolver ---
async def get_media_content(hass: HomeAssistant, path_or_url: str):
    """
    Handles:
    1. http://... (Returns URL as-is)
    2. media-source://... (Resolves to internal URL -> Downloads -> Returns Base64)
    3. /config/..., /media/... (Reads local file -> Returns Base64)
    """
    if not path_or_url:
        return None

    # 1. Standard Web URL
    if path_or_url.startswith("http"):
        return path_or_url

    # 2. Home Assistant Media Source (media-source://)
    if path_or_url.startswith("media-source://"):
        try:
            # Import media_source only when needed
            from homeassistant.components import media_source
            
            # Resolve the virtual path to a play URL
            play_media = await media_source.async_resolve_media(hass, path_or_url, None)
            url = play_media.url
            
            # If it's a relative URL (e.g. /media/local/...), prepend HA's internal address
            if url.startswith("/"):
                url = f"http://127.0.0.1:{hass.http.server_port}{url}"

            # Download the data internally
            session = async_get_clientsession(hass)
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.read()
                    return base64.b64encode(data).decode('utf-8')
                else:
                    _LOGGER.error(f"Failed to fetch media-source: {response.status}")
                    return None
        except Exception as e:
            _LOGGER.error(f"Error resolving media-source: {e}")
            return None

    # 3. Local File System
    return await hass.async_add_executor_job(encode_file, path_or_url)


# Service schemas - Updated to use ATTR_TARGET
SERVICE_SEND_TEXT_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_TARGET): cv.string,
        vol.Optional(ATTR_INSTANCE_ID): cv.string,
        vol.Required(ATTR_MESSAGE): cv.string,
        vol.Optional(ATTR_DELAY, default=0): cv.positive_int,
        vol.Optional(ATTR_LINK_PREVIEW, default=True): cv.boolean,
        vol.Optional(ATTR_MENTION_ALL, default=False): cv.boolean,
    }
)

SERVICE_SEND_MEDIA_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_TARGET): cv.string,
        vol.Optional(ATTR_INSTANCE_ID): cv.string,
        vol.Required(ATTR_MEDIA_URL): cv.string,
        vol.Required(ATTR_MEDIA_TYPE): vol.In(["image", "video", "document"]),
        vol.Optional(ATTR_MEDIA_CAPTION): cv.string,
        vol.Optional(ATTR_FILENAME): cv.string,
        vol.Optional(ATTR_DELAY, default=0): cv.positive_int,
    }
)

SERVICE_SEND_AUDIO_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_TARGET): cv.string,
        vol.Optional(ATTR_INSTANCE_ID): cv.string,
        vol.Required(ATTR_AUDIO_URL): cv.string,
        vol.Optional(ATTR_DELAY, default=0): cv.positive_int,
    }
)

SERVICE_SEND_STICKER_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_TARGET): cv.string,
        vol.Optional(ATTR_INSTANCE_ID): cv.string,
        vol.Required(ATTR_STICKER_URL): cv.string,
        vol.Optional(ATTR_DELAY, default=0): cv.positive_int,
    }
)

SERVICE_SEND_LOCATION_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_TARGET): cv.string,
        vol.Optional(ATTR_INSTANCE_ID): cv.string,
        vol.Required(ATTR_LATITUDE): vol.Coerce(float),
        vol.Required(ATTR_LONGITUDE): vol.Coerce(float),
        vol.Optional(ATTR_LOCATION_NAME): cv.string,
        vol.Optional(ATTR_LOCATION_ADDRESS): cv.string,
        vol.Optional(ATTR_DELAY, default=0): cv.positive_int,
    }
)

SERVICE_SEND_CONTACT_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_TARGET): cv.string,
        vol.Optional(ATTR_INSTANCE_ID): cv.string,
        vol.Required(ATTR_CONTACT_NAME): cv.string,
        vol.Required(ATTR_CONTACT_PHONE): cv.string,
        vol.Optional(ATTR_CONTACT_EMAIL): cv.string,
        vol.Optional(ATTR_CONTACT_ORG): cv.string,
    }
)

SERVICE_SEND_REACTION_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_TARGET): cv.string,
        vol.Optional(ATTR_INSTANCE_ID): cv.string,
        vol.Required(ATTR_MESSAGE_ID): cv.string,
        vol.Required(ATTR_REACTION): cv.string,
    }
)

SERVICE_SEND_POLL_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_TARGET): cv.string,
        vol.Optional(ATTR_INSTANCE_ID): cv.string,
        vol.Required(ATTR_POLL_NAME): cv.string,
        vol.Required(ATTR_POLL_OPTIONS): cv.string,
        vol.Optional(ATTR_POLL_MAX_SELECTIONS, default=1): cv.positive_int,
        vol.Optional(ATTR_DELAY, default=0): cv.positive_int,
    }
)

SERVICE_CHECK_NUMBER_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_PHONE_NUMBER): cv.string,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Evolution API from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Create API client
    session = async_get_clientsession(hass)
    client = EvolutionApiClient(
        session=session,
        server_url=entry.data[CONF_SERVER_URL],
        instance_id=entry.data[CONF_INSTANCE_ID],
        api_key=entry.data[CONF_API_KEY],
        verify_ssl=entry.data.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL),
    )

    # Initialize persistent storage
    storage = EvolutionApiStorage(hass, entry.entry_id)
    await storage.async_load()

    # Store the client and storage
    hass.data[DOMAIN][entry.entry_id] = {
        "client": client,
        "config": entry.data,
        "storage": storage,
    }

    # Register services
    await _async_register_services(hass)

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Update listener for config changes
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

        # If no more entries, unregister services
        if not hass.data[DOMAIN]:
            _async_unregister_services(hass)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


def _get_client(hass: HomeAssistant) -> EvolutionApiClient:
    """Get the first available API client."""
    for entry_data in hass.data[DOMAIN].values():
        if "client" in entry_data:
            return entry_data["client"]
    raise ValueError("No Evolution API client configured")


async def _async_register_services(hass: HomeAssistant) -> None:
    """Register Evolution API services."""

    # Check if services are already registered
    if hass.services.has_service(DOMAIN, SERVICE_SEND_TEXT):
        return

    async def async_send_text(call: ServiceCall) -> None:
        """Handle send text service call."""
        client = _get_client(hass)
        instance = call.data.get(ATTR_INSTANCE_ID)
        try:
            # Get target directly from call data
            recipient = call.data[ATTR_TARGET]
            
            await client.send_text(
                number=recipient,
                text=call.data[ATTR_MESSAGE],
                delay=call.data.get(ATTR_DELAY),
                link_preview=call.data.get(ATTR_LINK_PREVIEW, True),
                mention_all=call.data.get(ATTR_MENTION_ALL, False),
                instance_id=instance,
            )
        except EvolutionApiError as err:
            _LOGGER.error("Failed to send text message: %s", err)
            raise

    async def async_send_media(call: ServiceCall) -> None:
        """Handle send media service call."""
        client = _get_client(hass)
        instance = call.data.get(ATTR_INSTANCE_ID)
        try:
            recipient = call.data[ATTR_TARGET]
            
            # Use smart resolver for media
            media_input = call.data[ATTR_MEDIA_URL]
            processed_media = await get_media_content(hass, media_input)
            if not processed_media:
                 raise ValueError(f"Could not resolve media: {media_input}")

            await client.send_media(
                number=recipient,
                media_url=processed_media,
                media_type=call.data[ATTR_MEDIA_TYPE],
                caption=call.data.get(ATTR_MEDIA_CAPTION),
                filename=call.data.get(ATTR_FILENAME),
                delay=call.data.get(ATTR_DELAY),
                instance_id=instance,
            )
        except EvolutionApiError as err:
            _LOGGER.error("Failed to send media: %s", err)
            raise

    async def async_send_audio(call: ServiceCall) -> None:
        """Handle send audio service call."""
        client = _get_client(hass)
        instance = call.data.get(ATTR_INSTANCE_ID)
        try:
            recipient = call.data[ATTR_TARGET]
            
            # Use smart resolver for audio
            audio_input = call.data[ATTR_AUDIO_URL]
            processed_audio = await get_media_content(hass, audio_input)
            if not processed_audio:
                raise ValueError(f"Could not resolve audio: {audio_input}")

            await client.send_audio(
                number=recipient,
                audio_url=processed_audio,
                delay=call.data.get(ATTR_DELAY),
                instance_id=instance,
            )
        except EvolutionApiError as err:
            _LOGGER.error("Failed to send audio: %s", err)
            raise

    async def async_send_sticker(call: ServiceCall) -> None:
        """Handle send sticker service call."""
        client = _get_client(hass)
        instance = call.data.get(ATTR_INSTANCE_ID)
        try:
            recipient = call.data[ATTR_TARGET]
            
            # Use smart resolver for sticker
            sticker_input = call.data[ATTR_STICKER_URL]
            processed_sticker = await get_media_content(hass, sticker_input)
            if not processed_sticker:
                raise ValueError(f"Could not resolve sticker: {sticker_input}")

            await client.send_sticker(
                number=recipient,
                sticker_url=processed_sticker,
                delay=call.data.get(ATTR_DELAY),
                instance_id=instance,
            )
        except EvolutionApiError as err:
            _LOGGER.error("Failed to send sticker: %s", err)
            raise

    async def async_send_location(call: ServiceCall) -> None:
        """Handle send location service call."""
        client = _get_client(hass)
        instance = call.data.get(ATTR_INSTANCE_ID)
        try:
            recipient = call.data[ATTR_TARGET]
            await client.send_location(
                number=recipient,
                latitude=call.data[ATTR_LATITUDE],
                longitude=call.data[ATTR_LONGITUDE],
                name=call.data.get(ATTR_LOCATION_NAME),
                address=call.data.get(ATTR_LOCATION_ADDRESS),
                delay=call.data.get(ATTR_DELAY),
                instance_id=instance,
            )
        except EvolutionApiError as err:
            _LOGGER.error("Failed to send location: %s", err)
            raise

    async def async_send_contact(call: ServiceCall) -> None:
        """Handle send contact service call."""
        client = _get_client(hass)
        instance = call.data.get(ATTR_INSTANCE_ID)
        try:
            recipient = call.data[ATTR_TARGET]
            await client.send_contact(
                number=recipient,
                contact_name=call.data[ATTR_CONTACT_NAME],
                contact_phone=call.data[ATTR_CONTACT_PHONE],
                contact_email=call.data.get(ATTR_CONTACT_EMAIL),
                contact_organization=call.data.get(ATTR_CONTACT_ORG),
                instance_id=instance,
            )
        except EvolutionApiError as err:
            _LOGGER.error("Failed to send contact: %s", err)
            raise

    async def async_send_reaction(call: ServiceCall) -> None:
        """Handle send reaction service call."""
        client = _get_client(hass)
        instance = call.data.get(ATTR_INSTANCE_ID)
        try:
            recipient = call.data[ATTR_TARGET]
            await client.send_reaction(
                number=recipient,
                message_id=call.data[ATTR_MESSAGE_ID],
                reaction=call.data[ATTR_REACTION],
                instance_id=instance,
            )
        except EvolutionApiError as err:
            _LOGGER.error("Failed to send reaction: %s", err)
            raise

    async def async_send_poll(call: ServiceCall) -> None:
        """Handle send poll service call."""
        client = _get_client(hass)
        instance = call.data.get(ATTR_INSTANCE_ID)
        # Parse poll options from comma-separated string
        options_str = call.data[ATTR_POLL_OPTIONS]
        options = [opt.strip() for opt in options_str.split(",") if opt.strip()]
        try:
            recipient = call.data[ATTR_TARGET]
            await client.send_poll(
                number=recipient,
                poll_name=call.data[ATTR_POLL_NAME],
                options=options,
                max_selections=call.data.get(ATTR_POLL_MAX_SELECTIONS, 1),
                delay=call.data.get(ATTR_DELAY),
                instance_id=instance,
            )
        except EvolutionApiError as err:
            _LOGGER.error("Failed to send poll: %s", err)
            raise

    async def async_check_number(call: ServiceCall) -> dict[str, Any]:
        """Handle check number service call."""
        client = _get_client(hass)
        try:
            result = await client.check_is_whatsapp([call.data[ATTR_PHONE_NUMBER]])
            return result
        except EvolutionApiError as err:
            _LOGGER.error("Failed to check number: %s", err)
            raise

    async def async_refresh_groups(call: ServiceCall) -> None:
        """Handle refresh groups service call."""
        client = _get_client(hass)
        try:
            _LOGGER.info("Refreshing groups list")
            groups = await client.fetch_all_groups(get_participants=False)
            
            # Store groups in hass.data and persistent storage for all entries
            for entry_id, entry_data in hass.data[DOMAIN].items():
                if "client" in entry_data:
                    entry_data["groups"] = groups
                    entry_data["groups_count"] = len(groups)
                    
                    # Save to persistent storage
                    if "storage" in entry_data:
                        await entry_data["storage"].async_save_groups(groups)
                    
                    # Fire event so sensors can update
                    hass.bus.async_fire(
                        f"{DOMAIN}_groups_updated",
                        {"entry_id": entry_id, "count": len(groups)},
                    )
            
            _LOGGER.info("Found %d groups", len(groups))
        except EvolutionApiError as err:
            _LOGGER.error("Failed to refresh groups: %s", err)
            raise

    # Register all services
    hass.services.async_register(
        DOMAIN, SERVICE_SEND_TEXT, async_send_text, schema=SERVICE_SEND_TEXT_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SEND_MEDIA, async_send_media, schema=SERVICE_SEND_MEDIA_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SEND_AUDIO, async_send_audio, schema=SERVICE_SEND_AUDIO_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SEND_STICKER, async_send_sticker, schema=SERVICE_SEND_STICKER_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SEND_LOCATION, async_send_location, schema=SERVICE_SEND_LOCATION_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SEND_CONTACT, async_send_contact, schema=SERVICE_SEND_CONTACT_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SEND_REACTION, async_send_reaction, schema=SERVICE_SEND_REACTION_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SEND_POLL, async_send_poll, schema=SERVICE_SEND_POLL_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_CHECK_NUMBER, async_check_number, schema=SERVICE_CHECK_NUMBER_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_REFRESH_GROUPS, async_refresh_groups
    )

    _LOGGER.info("Evolution API services registered")


@callback
def _async_unregister_services(hass: HomeAssistant) -> None:
    """Unregister Evolution API services."""
    services = [
        SERVICE_SEND_TEXT,
        SERVICE_SEND_MEDIA,
        SERVICE_SEND_AUDIO,
        SERVICE_SEND_STICKER,
        SERVICE_SEND_LOCATION,
        SERVICE_SEND_CONTACT,
        SERVICE_SEND_REACTION,
        SERVICE_SEND_POLL,
        SERVICE_CHECK_NUMBER,
        SERVICE_REFRESH_GROUPS,
    ]
    for service in services:
        hass.services.async_remove(DOMAIN, service)

    _LOGGER.info("Evolution API services unregistered")