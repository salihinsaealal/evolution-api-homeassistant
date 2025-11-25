"""Constants for the Evolution API integration."""
from typing import Final

# Integration domain - used as the key for storing data in hass.data
DOMAIN: Final = "evolution_api"

# Configuration keys
CONF_INSTANCE_ID: Final = "instance_id"
CONF_API_KEY: Final = "api_key"
CONF_SERVER_URL: Final = "server_url"
CONF_VERIFY_SSL: Final = "verify_ssl"

# Default configuration
DEFAULT_NAME: Final = "Evolution API"
DEFAULT_PORT: Final = 3000
DEFAULT_VERIFY_SSL: Final = True
DEFAULT_TIMEOUT: Final = 30

# API endpoints - Instance Management
API_ENDPOINT_GET_INFO: Final = "/"
API_ENDPOINT_CREATE_INSTANCE: Final = "/instance/create"
API_ENDPOINT_FETCH_INSTANCES: Final = "/instance/fetchInstances"
API_ENDPOINT_INSTANCE_CONNECT: Final = "/instance/connect"
API_ENDPOINT_RESTART_INSTANCE: Final = "/instance/restart"
API_ENDPOINT_CONNECTION_STATE: Final = "/instance/connectionState"
API_ENDPOINT_LOGOUT_INSTANCE: Final = "/instance/logout"
API_ENDPOINT_DELETE_INSTANCE: Final = "/instance/delete"

# API endpoints - Message Controller
API_ENDPOINT_SEND_TEXT: Final = "/message/sendText"
API_ENDPOINT_SEND_MEDIA: Final = "/message/sendMedia"
API_ENDPOINT_SEND_AUDIO: Final = "/message/sendWhatsAppAudio"
API_ENDPOINT_SEND_STICKER: Final = "/message/sendSticker"
API_ENDPOINT_SEND_LOCATION: Final = "/message/sendLocation"
API_ENDPOINT_SEND_CONTACT: Final = "/message/sendContact"
API_ENDPOINT_SEND_REACTION: Final = "/message/sendReaction"
API_ENDPOINT_SEND_POLL: Final = "/message/sendPoll"
API_ENDPOINT_SEND_LIST: Final = "/message/sendList"
API_ENDPOINT_SEND_BUTTONS: Final = "/message/sendButtons"
API_ENDPOINT_SEND_STATUS: Final = "/message/sendStatus"

# API endpoints - Chat Controller
API_ENDPOINT_CHECK_IS_WHATSAPP: Final = "/chat/whatsappNumbers"
API_ENDPOINT_MARK_MESSAGE_READ: Final = "/chat/markMessageAsRead"
API_ENDPOINT_MARK_MESSAGE_UNREAD: Final = "/chat/markMessageAsUnread"
API_ENDPOINT_ARCHIVE_CHAT: Final = "/chat/archiveChat"
API_ENDPOINT_DELETE_MESSAGE: Final = "/chat/deleteMessageForEveryone"
API_ENDPOINT_SEND_PRESENCE: Final = "/chat/sendPresence"
API_ENDPOINT_FETCH_PROFILE_PICTURE: Final = "/chat/fetchProfilePictureUrl"

# API endpoints - Group Controller
API_ENDPOINT_FETCH_ALL_GROUPS: Final = "/group/fetchAllGroups"
API_ENDPOINT_FIND_GROUP: Final = "/group/findGroupInfos"
API_ENDPOINT_GROUP_PARTICIPANTS: Final = "/group/participants"

# API endpoints - Profile
API_ENDPOINT_FETCH_PROFILE: Final = "/chat/fetchProfile"

# Service names
SERVICE_SEND_TEXT: Final = "send_text"
SERVICE_SEND_MEDIA: Final = "send_media"
SERVICE_SEND_AUDIO: Final = "send_audio"
SERVICE_SEND_STICKER: Final = "send_sticker"
SERVICE_SEND_LOCATION: Final = "send_location"
SERVICE_SEND_CONTACT: Final = "send_contact"
SERVICE_SEND_REACTION: Final = "send_reaction"
SERVICE_SEND_POLL: Final = "send_poll"
SERVICE_CHECK_NUMBER: Final = "check_number"

# Service attributes
ATTR_PHONE_NUMBER: Final = "phone_number"
ATTR_MESSAGE: Final = "message"
ATTR_MEDIA_URL: Final = "media_url"
ATTR_MEDIA_TYPE: Final = "media_type"
ATTR_MEDIA_CAPTION: Final = "caption"
ATTR_FILENAME: Final = "filename"
ATTR_AUDIO_URL: Final = "audio_url"
ATTR_STICKER_URL: Final = "sticker_url"
ATTR_LATITUDE: Final = "latitude"
ATTR_LONGITUDE: Final = "longitude"
ATTR_LOCATION_NAME: Final = "name"
ATTR_LOCATION_ADDRESS: Final = "address"
ATTR_CONTACT_NAME: Final = "contact_name"
ATTR_CONTACT_PHONE: Final = "contact_phone"
ATTR_CONTACT_EMAIL: Final = "contact_email"
ATTR_CONTACT_ORG: Final = "contact_organization"
ATTR_MESSAGE_ID: Final = "message_id"
ATTR_REACTION: Final = "reaction"
ATTR_POLL_NAME: Final = "poll_name"
ATTR_POLL_OPTIONS: Final = "poll_options"
ATTR_POLL_MAX_SELECTIONS: Final = "max_selections"
ATTR_DELAY: Final = "delay"
ATTR_LINK_PREVIEW: Final = "link_preview"
ATTR_MENTION_ALL: Final = "mention_all"
ATTR_MENTIONED: Final = "mentioned"

# Media types
MEDIA_TYPE_IMAGE: Final = "image"
MEDIA_TYPE_VIDEO: Final = "video"
MEDIA_TYPE_DOCUMENT: Final = "document"

# Presence types
PRESENCE_AVAILABLE: Final = "available"
PRESENCE_COMPOSING: Final = "composing"
PRESENCE_RECORDING: Final = "recording"
PRESENCE_PAUSED: Final = "paused"
