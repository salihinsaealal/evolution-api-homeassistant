# Evolution API Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub Release](https://img.shields.io/github/v/release/salihinsaealal/evolution-api-homeassistant)](https://github.com/salihinsaealal/evolution-api-homeassistant/releases)

A robust Home Assistant integration for [Evolution API](https://evolution-api.com/) that enables WhatsApp messaging automation directly from your smart home.

## Features

- 🚀 **Easy Setup** - Configure through Home Assistant UI with connection validation
- 📱 **Multiple Message Types** - Text, images, videos, documents, audio, stickers, locations, contacts, and polls
- 👥 **Group Support** - Send messages to WhatsApp groups
- ⚡ **Automation Ready** - All services available for automations, scripts, and scenes
- 🔒 **Secure** - API credentials stored securely in Home Assistant
- 📊 **Entity Support** - Connection status sensor, groups sensor, and refresh buttons

---

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Entities](#entities)
- [Services](#services)
- [Sending to Groups](#sending-to-groups)
- [Automation Examples](#automation-examples)
- [Troubleshooting](#troubleshooting)

---

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots → "Custom repositories"
4. Add `https://github.com/salihinsaealal/evolution-api-homeassistant` as "Integration"
5. Search for "Evolution API" and install
6. Restart Home Assistant

### Manual Installation

1. Download `custom_components/evolution_api` from this repository
2. Copy to your Home Assistant's `custom_components` directory
3. Restart Home Assistant

---

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Evolution API"
4. Enter your details:

| Field | Description | Example |
|-------|-------------|---------|
| Server URL | Evolution API server URL | `https://your-server.com` |
| Instance ID | WhatsApp instance ID | `my-instance` |
| API Key | Your API key | `your-api-key` |
| Verify SSL | SSL certificate verification | `true` |

> ⚠️ Make sure your WhatsApp instance is connected (QR code scanned) before setup.

---

## Entities

### Sensors

| Entity | Description |
|--------|-------------|
| `sensor.evolution_api_*_connection_status` | WhatsApp connection state (`open`, `close`, `connecting`) |
| `sensor.evolution_api_*_groups` | Number of groups (group list in attributes) |

### Buttons

| Entity | Description |
|--------|-------------|
| `button.evolution_api_*_refresh_groups` | Fetch latest groups list |
| `button.evolution_api_*_refresh_connection` | Refresh connection status |

---

## Services

All messaging services support both **phone numbers** and **groups**.

### `evolution_api.send_text`

Send a text message.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `phone_number` | No* | Phone with country code (e.g., `+1234567890`) |
| `group_id` | No* | Group JID (e.g., `123456789@g.us`) |
| `message` | **Yes** | Text message to send |
| `link_preview` | No | Show URL preview (default: `true`) |
| `mention_all` | No | Mention everyone in group (default: `false`) |
| `delay` | No | Delay in ms before sending |

*Either `phone_number` or `group_id` required.

```yaml
# Send to phone
service: evolution_api.send_text
data:
  phone_number: "+1234567890"
  message: "Hello from Home Assistant! 👋"
  link_preview: true
```

```yaml
# Send to group
service: evolution_api.send_text
data:
  group_id: "120363418454200327@g.us"
  message: "Hello everyone!"
  mention_all: true
```

---

### `evolution_api.send_media`

Send image, video, or document.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `phone_number` | No* | Phone number |
| `group_id` | No* | Group JID |
| `media_url` | **Yes** | URL or base64 of media |
| `media_type` | **Yes** | `image`, `video`, or `document` |
| `caption` | No | Caption text |
| `filename` | No | Filename (for documents) |
| `delay` | No | Delay in ms |

```yaml
# Send image
service: evolution_api.send_media
data:
  phone_number: "+1234567890"
  media_url: "https://example.com/photo.jpg"
  media_type: "image"
  caption: "Beautiful sunset! 🌅"
```

```yaml
# Send video
service: evolution_api.send_media
data:
  phone_number: "+1234567890"
  media_url: "https://example.com/video.mp4"
  media_type: "video"
  caption: "Check this out!"
```

```yaml
# Send document
service: evolution_api.send_media
data:
  phone_number: "+1234567890"
  media_url: "https://example.com/report.pdf"
  media_type: "document"
  filename: "Monthly_Report.pdf"
```

```yaml
# Send to group
service: evolution_api.send_media
data:
  group_id: "120363418454200327@g.us"
  media_url: "https://example.com/image.jpg"
  media_type: "image"
  caption: "Sharing with the group!"
```

---

### `evolution_api.send_audio`

Send audio/voice message.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `phone_number` | No* | Phone number |
| `group_id` | No* | Group JID |
| `audio_url` | **Yes** | URL or base64 of audio |
| `delay` | No | Delay in ms |

```yaml
service: evolution_api.send_audio
data:
  phone_number: "+1234567890"
  audio_url: "https://example.com/voice.mp3"
```

---

### `evolution_api.send_sticker`

Send a sticker (WebP format).

| Parameter | Required | Description |
|-----------|----------|-------------|
| `phone_number` | No* | Phone number |
| `group_id` | No* | Group JID |
| `sticker_url` | **Yes** | URL or base64 of sticker |
| `delay` | No | Delay in ms |

```yaml
service: evolution_api.send_sticker
data:
  phone_number: "+1234567890"
  sticker_url: "https://example.com/sticker.webp"
```

---

### `evolution_api.send_location`

Send a location pin.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `phone_number` | No* | Phone number |
| `group_id` | No* | Group JID |
| `latitude` | **Yes** | Latitude (-90 to 90) |
| `longitude` | **Yes** | Longitude (-180 to 180) |
| `name` | No | Location name |
| `address` | No | Full address |
| `delay` | No | Delay in ms |

```yaml
service: evolution_api.send_location
data:
  phone_number: "+1234567890"
  latitude: 37.7749
  longitude: -122.4194
  name: "San Francisco"
  address: "San Francisco, CA, USA"
```

```yaml
# Send home location using template
service: evolution_api.send_location
data:
  phone_number: "+1234567890"
  latitude: "{{ state_attr('zone.home', 'latitude') }}"
  longitude: "{{ state_attr('zone.home', 'longitude') }}"
  name: "My Home"
```

---

### `evolution_api.send_contact`

Send a contact card (vCard).

| Parameter | Required | Description |
|-----------|----------|-------------|
| `phone_number` | No* | Phone number |
| `group_id` | No* | Group JID |
| `contact_name` | **Yes** | Contact's full name |
| `contact_phone` | **Yes** | Contact's phone number |
| `contact_email` | No | Contact's email |
| `contact_organization` | No | Contact's company |

```yaml
service: evolution_api.send_contact
data:
  phone_number: "+1234567890"
  contact_name: "John Doe"
  contact_phone: "+1987654321"
  contact_email: "john@example.com"
  contact_organization: "Acme Inc."
```

---

### `evolution_api.send_reaction`

React to a message with emoji.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `phone_number` | No* | Chat's phone number |
| `group_id` | No* | Group JID |
| `message_id` | **Yes** | Message ID to react to |
| `reaction` | **Yes** | Emoji (empty to remove) |

```yaml
# Add reaction
service: evolution_api.send_reaction
data:
  phone_number: "+1234567890"
  message_id: "BAE5F5A632EAE722"
  reaction: "👍"
```

```yaml
# Remove reaction
service: evolution_api.send_reaction
data:
  phone_number: "+1234567890"
  message_id: "BAE5F5A632EAE722"
  reaction: ""
```

---

### `evolution_api.send_poll`

Create and send a poll.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `phone_number` | No* | Phone number |
| `group_id` | No* | Group JID |
| `poll_name` | **Yes** | Poll question |
| `poll_options` | **Yes** | Comma-separated options |
| `max_selections` | No | Max selections (default: 1) |
| `delay` | No | Delay in ms |

```yaml
# Single choice poll
service: evolution_api.send_poll
data:
  phone_number: "+1234567890"
  poll_name: "What's your favorite color?"
  poll_options: "Red, Blue, Green, Yellow"
  max_selections: 1
```

```yaml
# Multiple choice poll to group
service: evolution_api.send_poll
data:
  group_id: "120363418454200327@g.us"
  poll_name: "Which toppings for pizza?"
  poll_options: "Pepperoni, Mushrooms, Olives, Onions, Cheese"
  max_selections: 3
```

---

### `evolution_api.check_number`

Check if number is on WhatsApp.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `phone_number` | **Yes** | Phone to check |

```yaml
service: evolution_api.check_number
data:
  phone_number: "+1234567890"
```

---

### `evolution_api.refresh_groups`

Fetch latest groups list.

```yaml
service: evolution_api.refresh_groups
data: {}
```

---

## Sending to Groups

### Step 1: Fetch Groups

Press **"Refresh Groups"** button or call:
```yaml
service: evolution_api.refresh_groups
```

### Step 2: Find Group ID

1. Go to **Developer Tools** → **States**
2. Find `sensor.evolution_api_*_groups`
3. Check **Attributes** → `groups` list
4. Copy the `id` (e.g., `120363418454200327@g.us`)

### Step 3: Use in Services

```yaml
service: evolution_api.send_text
data:
  group_id: "120363418454200327@g.us"
  message: "Hello group!"
```

### Template Examples

```yaml
# Send to first group
service: evolution_api.send_text
data:
  group_id: "{{ state_attr('sensor.evolution_api_myinstance_groups', 'groups')[0].id }}"
  message: "Hello!"
```

```yaml
# Find group by name
service: evolution_api.send_text
data:
  group_id: >
    {% set groups = state_attr('sensor.evolution_api_myinstance_groups', 'groups') %}
    {% set family = groups | selectattr('name', 'equalto', 'Family') | first %}
    {{ family.id if family else '' }}
  message: "Hello family!"
```

---

## Automation Examples

### 🚪 Door Alert

```yaml
automation:
  - alias: "Door Open Alert"
    trigger:
      - platform: state
        entity_id: binary_sensor.front_door
        to: "on"
    action:
      - service: evolution_api.send_text
        data:
          phone_number: "+1234567890"
          message: "🚪 Door opened at {{ now().strftime('%H:%M') }}"
```

### 📷 Motion Camera Snapshot

```yaml
automation:
  - alias: "Motion - Send Camera"
    trigger:
      - platform: state
        entity_id: binary_sensor.motion
        to: "on"
    action:
      - service: camera.snapshot
        target:
          entity_id: camera.front
        data:
          filename: "/config/www/motion.jpg"
      - delay: 2
      - service: evolution_api.send_media
        data:
          phone_number: "+1234567890"
          media_url: "http://your-ha:8123/local/motion.jpg"
          media_type: "image"
          caption: "🚨 Motion detected!"
```

### 🌤️ Daily Weather

```yaml
automation:
  - alias: "Daily Weather"
    trigger:
      - platform: time
        at: "07:00:00"
    action:
      - service: evolution_api.send_text
        data:
          phone_number: "+1234567890"
          message: >
            🌤️ Good morning!
            🌡️ Temp: {{ states('sensor.temperature') }}°C
            💧 Humidity: {{ states('sensor.humidity') }}%
```

### 📍 Location on Leave

```yaml
automation:
  - alias: "Send Location"
    trigger:
      - platform: state
        entity_id: person.john
        from: "home"
    action:
      - service: evolution_api.send_location
        data:
          phone_number: "+1234567890"
          latitude: "{{ state_attr('person.john', 'latitude') }}"
          longitude: "{{ state_attr('person.john', 'longitude') }}"
          name: "Current Location"
```

### 🍕 Dinner Poll

```yaml
automation:
  - alias: "Dinner Poll"
    trigger:
      - platform: time
        at: "16:00:00"
    action:
      - service: evolution_api.send_poll
        data:
          group_id: "120363418454200327@g.us"
          poll_name: "🍽️ What's for dinner?"
          poll_options: "🍕 Pizza, 🍣 Sushi, 🌮 Tacos, 🍝 Pasta"
```

### 🔔 Doorbell with Image

```yaml
automation:
  - alias: "Doorbell"
    trigger:
      - platform: state
        entity_id: binary_sensor.doorbell
        to: "on"
    action:
      - service: camera.snapshot
        target:
          entity_id: camera.doorbell
        data:
          filename: "/config/www/doorbell.jpg"
      - delay: 1
      - service: evolution_api.send_media
        data:
          group_id: "120363418454200327@g.us"
          media_url: "http://your-ha:8123/local/doorbell.jpg"
          media_type: "image"
          caption: "🔔 Someone at the door!"
```

### 🚨 Security Alert

```yaml
automation:
  - alias: "Security Alert"
    trigger:
      - platform: state
        entity_id: alarm_control_panel.home
        to: "triggered"
    action:
      - service: evolution_api.send_text
        data:
          phone_number: "+1234567890"
          message: "🚨 ALARM TRIGGERED at {{ now().strftime('%H:%M') }}!"
      - service: evolution_api.send_text
        data:
          group_id: "120363418454200327@g.us"
          message: "🚨 Home alarm triggered!"
```

---

## Format Reference

### Phone Numbers

| Format | Valid |
|--------|-------|
| `+1234567890` | ✅ |
| `1234567890` | ✅ |
| `+1 (234) 567-890` | ❌ |

### Group IDs

| Format | Valid |
|--------|-------|
| `120363418454200327@g.us` | ✅ |
| `120363418454200327` | ✅ (auto-suffixed) |

---

## Troubleshooting

### Connection Failed
- Check server URL includes `https://` or `http://`
- Verify API key is correct
- Ensure server is accessible

### Instance Not Connected
- Open Evolution API dashboard
- Scan QR code with WhatsApp
- Check Connection Status sensor

### Messages Not Sending
- Verify phone number format
- Check recipient has WhatsApp
- Review Home Assistant logs

### Groups Not Loading
- Press "Refresh Groups" button
- Ensure instance is connected
- Check logs for errors

---

## Contributing

Contributions welcome! Please submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE)

## Disclaimer

Not affiliated with WhatsApp or Meta. Use responsibly per WhatsApp's Terms of Service.
