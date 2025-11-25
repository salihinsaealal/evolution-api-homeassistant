"""Evolution API client for Home Assistant."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
import async_timeout

from .const import (
    API_ENDPOINT_CONNECTION_STATE,
    API_ENDPOINT_FETCH_ALL_GROUPS,
    API_ENDPOINT_FETCH_PROFILE,
    API_ENDPOINT_SEND_TEXT,
    API_ENDPOINT_SEND_MEDIA,
    API_ENDPOINT_SEND_AUDIO,
    API_ENDPOINT_SEND_STICKER,
    API_ENDPOINT_SEND_LOCATION,
    API_ENDPOINT_SEND_CONTACT,
    API_ENDPOINT_SEND_REACTION,
    API_ENDPOINT_SEND_POLL,
    API_ENDPOINT_SEND_LIST,
    API_ENDPOINT_SEND_BUTTONS,
    API_ENDPOINT_SEND_STATUS,
    API_ENDPOINT_CHECK_IS_WHATSAPP,
    API_ENDPOINT_MARK_MESSAGE_READ,
    API_ENDPOINT_SEND_PRESENCE,
    API_ENDPOINT_FETCH_PROFILE_PICTURE,
    DEFAULT_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)


class EvolutionApiError(Exception):
    """Base exception for Evolution API errors."""


class EvolutionApiConnectionError(EvolutionApiError):
    """Exception for connection errors."""


class EvolutionApiAuthError(EvolutionApiError):
    """Exception for authentication errors."""


class EvolutionApiClient:
    """Evolution API client."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        server_url: str,
        instance_id: str,
        api_key: str,
        verify_ssl: bool = True,
    ) -> None:
        """Initialize the API client."""
        self._session = session
        self._server_url = server_url.rstrip("/")
        self._instance_id = instance_id
        self._api_key = api_key
        self._verify_ssl = verify_ssl

    @property
    def headers(self) -> dict[str, str]:
        """Return the headers for API requests."""
        return {
            "apikey": self._api_key,
            "Content-Type": "application/json",
        }

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: dict[str, Any] | None = None,
        include_instance: bool = True,
    ) -> dict[str, Any]:
        """Make a request to the Evolution API."""
        if include_instance:
            url = f"{self._server_url}{endpoint}/{self._instance_id}"
        else:
            url = f"{self._server_url}{endpoint}"

        try:
            async with async_timeout.timeout(DEFAULT_TIMEOUT):
                if method.upper() == "GET":
                    async with self._session.get(
                        url, headers=self.headers, ssl=self._verify_ssl
                    ) as response:
                        return await self._handle_response(response)
                elif method.upper() == "POST":
                    async with self._session.post(
                        url, headers=self.headers, json=data, ssl=self._verify_ssl
                    ) as response:
                        return await self._handle_response(response)
                elif method.upper() == "PUT":
                    async with self._session.put(
                        url, headers=self.headers, json=data, ssl=self._verify_ssl
                    ) as response:
                        return await self._handle_response(response)
                elif method.upper() == "DELETE":
                    async with self._session.delete(
                        url, headers=self.headers, ssl=self._verify_ssl
                    ) as response:
                        return await self._handle_response(response)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
        except asyncio.TimeoutError as err:
            _LOGGER.error("Timeout connecting to Evolution API: %s", err)
            raise EvolutionApiConnectionError("Timeout connecting to API") from err
        except aiohttp.ClientError as err:
            _LOGGER.error("Error connecting to Evolution API: %s", err)
            raise EvolutionApiConnectionError(f"Connection error: {err}") from err

    async def _handle_response(
        self, response: aiohttp.ClientResponse
    ) -> dict[str, Any]:
        """Handle the API response."""
        if response.status == 401:
            raise EvolutionApiAuthError("Invalid API key")
        if response.status == 404:
            raise EvolutionApiError("Instance not found")
        if response.status >= 400:
            text = await response.text()
            raise EvolutionApiError(f"API error {response.status}: {text}")

        try:
            return await response.json()
        except aiohttp.ContentTypeError:
            return {"status": response.status, "message": await response.text()}

    # ==================== Instance Methods ====================

    async def get_connection_state(self) -> dict[str, Any]:
        """Get the connection state of the instance."""
        return await self._request("GET", API_ENDPOINT_CONNECTION_STATE)

    async def check_connection(self) -> bool:
        """Check if the instance is connected."""
        try:
            result = await self.get_connection_state()
            state = result.get("instance", {}).get("state", "")
            return state.upper() == "OPEN"
        except EvolutionApiError:
            return False

    # ==================== Message Methods ====================

    async def send_text(
        self,
        number: str,
        text: str,
        delay: int | None = None,
        link_preview: bool = True,
        mention_all: bool = False,
        mentioned: list[str] | None = None,
    ) -> dict[str, Any]:
        """Send a text message."""
        payload: dict[str, Any] = {
            "number": number,
            "text": text,
            "linkPreview": link_preview,
        }
        if delay:
            payload["delay"] = delay
        if mention_all:
            payload["mentionsEveryOne"] = True
        if mentioned:
            payload["mentioned"] = mentioned

        _LOGGER.debug("Sending text message to %s", number)
        return await self._request("POST", API_ENDPOINT_SEND_TEXT, payload)

    async def send_media(
        self,
        number: str,
        media_url: str,
        media_type: str,
        caption: str | None = None,
        filename: str | None = None,
        delay: int | None = None,
    ) -> dict[str, Any]:
        """Send a media message (image, video, document)."""
        payload: dict[str, Any] = {
            "number": number,
            "mediatype": media_type,
            "media": media_url,
        }
        if caption:
            payload["caption"] = caption
        if filename:
            payload["fileName"] = filename
        if delay:
            payload["delay"] = delay

        # Set mimetype based on media type
        mimetype_map = {
            "image": "image/png",
            "video": "video/mp4",
            "document": "application/pdf",
        }
        payload["mimetype"] = mimetype_map.get(media_type, "application/octet-stream")

        _LOGGER.debug("Sending %s to %s", media_type, number)
        return await self._request("POST", API_ENDPOINT_SEND_MEDIA, payload)

    async def send_audio(
        self,
        number: str,
        audio_url: str,
        delay: int | None = None,
    ) -> dict[str, Any]:
        """Send an audio message (voice note)."""
        payload: dict[str, Any] = {
            "number": number,
            "audio": audio_url,
        }
        if delay:
            payload["delay"] = delay

        _LOGGER.debug("Sending audio to %s", number)
        return await self._request("POST", API_ENDPOINT_SEND_AUDIO, payload)

    async def send_sticker(
        self,
        number: str,
        sticker_url: str,
        delay: int | None = None,
    ) -> dict[str, Any]:
        """Send a sticker message."""
        payload: dict[str, Any] = {
            "number": number,
            "sticker": sticker_url,
        }
        if delay:
            payload["delay"] = delay

        _LOGGER.debug("Sending sticker to %s", number)
        return await self._request("POST", API_ENDPOINT_SEND_STICKER, payload)

    async def send_location(
        self,
        number: str,
        latitude: float,
        longitude: float,
        name: str | None = None,
        address: str | None = None,
        delay: int | None = None,
    ) -> dict[str, Any]:
        """Send a location message."""
        payload: dict[str, Any] = {
            "number": number,
            "latitude": latitude,
            "longitude": longitude,
        }
        if name:
            payload["name"] = name
        if address:
            payload["address"] = address
        if delay:
            payload["delay"] = delay

        _LOGGER.debug("Sending location to %s", number)
        return await self._request("POST", API_ENDPOINT_SEND_LOCATION, payload)

    async def send_contact(
        self,
        number: str,
        contact_name: str,
        contact_phone: str,
        contact_email: str | None = None,
        contact_organization: str | None = None,
    ) -> dict[str, Any]:
        """Send a contact message."""
        contact: dict[str, Any] = {
            "fullName": contact_name,
            "phoneNumber": contact_phone,
        }
        if contact_email:
            contact["email"] = contact_email
        if contact_organization:
            contact["organization"] = contact_organization

        payload = {
            "number": number,
            "contact": [contact],
        }

        _LOGGER.debug("Sending contact to %s", number)
        return await self._request("POST", API_ENDPOINT_SEND_CONTACT, payload)

    async def send_reaction(
        self,
        number: str,
        message_id: str,
        reaction: str,
    ) -> dict[str, Any]:
        """Send a reaction to a message."""
        payload = {
            "key": {
                "remoteJid": f"{number}@s.whatsapp.net",
                "id": message_id,
            },
            "reaction": reaction,
        }

        _LOGGER.debug("Sending reaction to message %s", message_id)
        return await self._request("POST", API_ENDPOINT_SEND_REACTION, payload)

    async def send_poll(
        self,
        number: str,
        poll_name: str,
        options: list[str],
        max_selections: int = 1,
        delay: int | None = None,
    ) -> dict[str, Any]:
        """Send a poll message."""
        payload: dict[str, Any] = {
            "number": number,
            "name": poll_name,
            "selectableCount": max_selections,
            "values": options,
        }
        if delay:
            payload["delay"] = delay

        _LOGGER.debug("Sending poll to %s", number)
        return await self._request("POST", API_ENDPOINT_SEND_POLL, payload)

    async def send_list(
        self,
        number: str,
        title: str,
        description: str,
        button_text: str,
        sections: list[dict[str, Any]],
        footer: str | None = None,
        delay: int | None = None,
    ) -> dict[str, Any]:
        """Send a list message."""
        payload: dict[str, Any] = {
            "number": number,
            "title": title,
            "description": description,
            "buttonText": button_text,
            "sections": sections,
        }
        if footer:
            payload["footerText"] = footer
        if delay:
            payload["delay"] = delay

        _LOGGER.debug("Sending list to %s", number)
        return await self._request("POST", API_ENDPOINT_SEND_LIST, payload)

    async def send_buttons(
        self,
        number: str,
        title: str,
        description: str,
        buttons: list[dict[str, Any]],
        footer: str | None = None,
        delay: int | None = None,
    ) -> dict[str, Any]:
        """Send a button message."""
        payload: dict[str, Any] = {
            "number": number,
            "title": title,
            "description": description,
            "buttons": buttons,
        }
        if footer:
            payload["footerText"] = footer
        if delay:
            payload["delay"] = delay

        _LOGGER.debug("Sending buttons to %s", number)
        return await self._request("POST", API_ENDPOINT_SEND_BUTTONS, payload)

    # ==================== Chat Methods ====================

    async def check_is_whatsapp(self, numbers: list[str]) -> dict[str, Any]:
        """Check if phone numbers are registered on WhatsApp."""
        payload = {"numbers": numbers}
        _LOGGER.debug("Checking WhatsApp numbers: %s", numbers)
        return await self._request("POST", API_ENDPOINT_CHECK_IS_WHATSAPP, payload)

    async def mark_message_as_read(
        self, remote_jid: str, message_id: str
    ) -> dict[str, Any]:
        """Mark a message as read."""
        payload = {
            "readMessages": [
                {
                    "remoteJid": remote_jid,
                    "id": message_id,
                }
            ]
        }
        return await self._request("POST", API_ENDPOINT_MARK_MESSAGE_READ, payload)

    async def send_presence(
        self, number: str, presence: str, delay: int = 1000
    ) -> dict[str, Any]:
        """Send presence status (typing, recording, etc.)."""
        payload = {
            "number": number,
            "presence": presence,
            "delay": delay,
        }
        return await self._request("POST", API_ENDPOINT_SEND_PRESENCE, payload)

    async def fetch_profile_picture(self, number: str) -> dict[str, Any]:
        """Fetch the profile picture URL of a contact."""
        payload = {"number": number}
        return await self._request("POST", API_ENDPOINT_FETCH_PROFILE_PICTURE, payload)

    # ==================== Group Methods ====================

    async def fetch_all_groups(self, get_participants: bool = False) -> list[dict[str, Any]]:
        """Fetch all groups the instance is part of."""
        # API requires getParticipants query parameter to be present
        url = f"{self._server_url}{API_ENDPOINT_FETCH_ALL_GROUPS}/{self._instance_id}?getParticipants={'true' if get_participants else 'false'}"
        
        try:
            async with async_timeout.timeout(DEFAULT_TIMEOUT):
                async with self._session.get(
                    url, headers=self.headers, ssl=self._verify_ssl
                ) as response:
                    result = await self._handle_response(response)
                    # API returns a list directly
                    if isinstance(result, list):
                        return result
                    return []
        except (asyncio.TimeoutError, aiohttp.ClientError) as err:
            _LOGGER.error("Error fetching groups: %s", err)
            raise EvolutionApiConnectionError(f"Error fetching groups: {err}") from err

    # ==================== Profile Methods ====================

    async def fetch_profile(self, number: str) -> dict[str, Any]:
        """Fetch profile information for a number."""
        payload = {"number": number}
        return await self._request("POST", API_ENDPOINT_FETCH_PROFILE, payload)

    async def get_instance_info(self) -> dict[str, Any]:
        """Get comprehensive instance information."""
        try:
            connection_state = await self.get_connection_state()
            instance_data = connection_state.get("instance", {})
            
            return {
                "state": instance_data.get("state", "unknown"),
                "owner": instance_data.get("owner", ""),
                "profile_name": instance_data.get("profileName", ""),
                "profile_picture_url": instance_data.get("profilePictureUrl", ""),
                "phone_number": instance_data.get("owner", "").replace("@s.whatsapp.net", ""),
            }
        except EvolutionApiError as err:
            _LOGGER.error("Error getting instance info: %s", err)
            return {
                "state": "error",
                "error": str(err),
            }
