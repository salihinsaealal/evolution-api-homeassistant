# Evolution API Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

A robust Home Assistant integration for [Evolution API](https://evolution-api.com/) that enables WhatsApp messaging automation directly from your smart home.

## Features

- **Easy Setup**: Configure through Home Assistant UI with connection validation
- **Multiple Message Types**: Send text, images, videos, documents, audio, stickers, locations, contacts, and polls
- **Automation Ready**: All services available for use in automations, scripts, and scenes
- **Secure**: API credentials stored securely in Home Assistant
- **Real-time Validation**: Connection status checked during setup

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL and select "Integration" as the category
6. Click "Add"
7. Search for "Evolution API" and install it
8. Restart Home Assistant

### Manual Installation

1. Download the `custom_components/evolution_api` folder from this repository
2. Copy it to your Home Assistant's `custom_components` directory
3. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Evolution API"
4. Enter your Evolution API details:
   - **Server URL**: Your Evolution API server URL (e.g., `https://your-server.com`)
   - **Instance ID**: Your WhatsApp instance ID
   - **API Key**: Your Evolution API key
   - **Verify SSL**: Enable/disable SSL certificate verification

> **Note**: Make sure your WhatsApp instance is connected (QR code scanned) before configuring the integration.

## Available Services

### `evolution_api.send_text`
Send a text message via WhatsApp.

```yaml
service: evolution_api.send_text
data:
  phone_number: "+1234567890"
  message: "Hello from Home Assistant!"
  link_preview: true
  delay: 1000
```

### `evolution_api.send_media`
Send an image, video, or document.

```yaml
service: evolution_api.send_media
data:
  phone_number: "+1234567890"
  media_url: "https://example.com/image.jpg"
  media_type: "image"  # image, video, or document
  caption: "Check out this image!"
  filename: "photo.jpg"
```

### `evolution_api.send_audio`
Send an audio message (voice note).

```yaml
service: evolution_api.send_audio
data:
  phone_number: "+1234567890"
  audio_url: "https://example.com/audio.mp3"
```

### `evolution_api.send_sticker`
Send a sticker.

```yaml
service: evolution_api.send_sticker
data:
  phone_number: "+1234567890"
  sticker_url: "https://example.com/sticker.webp"
```

### `evolution_api.send_location`
Send a location.

```yaml
service: evolution_api.send_location
data:
  phone_number: "+1234567890"
  latitude: 37.7749
  longitude: -122.4194
  name: "San Francisco"
  address: "San Francisco, CA, USA"
```

### `evolution_api.send_contact`
Send a contact card.

```yaml
service: evolution_api.send_contact
data:
  phone_number: "+1234567890"
  contact_name: "John Doe"
  contact_phone: "+1987654321"
  contact_email: "john@example.com"
  contact_organization: "Acme Inc."
```

### `evolution_api.send_reaction`
Send a reaction to a message.

```yaml
service: evolution_api.send_reaction
data:
  phone_number: "+1234567890"
  message_id: "BAE5F5A632EAE722"
  reaction: "👍"
```

### `evolution_api.send_poll`
Send a poll.

```yaml
service: evolution_api.send_poll
data:
  phone_number: "+1234567890"
  poll_name: "What's your favorite color?"
  poll_options: "Red, Blue, Green, Yellow"
  max_selections: 1
```

### `evolution_api.check_number`
Check if a phone number is registered on WhatsApp.

```yaml
service: evolution_api.check_number
data:
  phone_number: "+1234567890"
```

## Automation Examples

### Send Alert When Door Opens

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
          message: "🚪 Front door was opened at {{ now().strftime('%H:%M') }}"
```

### Send Camera Snapshot on Motion

```yaml
automation:
  - alias: "Motion Detected - Send Camera Image"
    trigger:
      - platform: state
        entity_id: binary_sensor.motion_sensor
        to: "on"
    action:
      - service: camera.snapshot
        target:
          entity_id: camera.front_door
        data:
          filename: "/config/www/snapshot.jpg"
      - delay: "00:00:02"
      - service: evolution_api.send_media
        data:
          phone_number: "+1234567890"
          media_url: "{{ states('input_text.ha_external_url') }}/local/snapshot.jpg"
          media_type: "image"
          caption: "Motion detected at front door!"
```

### Daily Weather Report

```yaml
automation:
  - alias: "Daily Weather Report"
    trigger:
      - platform: time
        at: "07:00:00"
    action:
      - service: evolution_api.send_text
        data:
          phone_number: "+1234567890"
          message: >
            🌤️ Good morning! Today's weather:
            Temperature: {{ states('sensor.temperature') }}°C
            Humidity: {{ states('sensor.humidity') }}%
            Condition: {{ states('weather.home') }}
```

### Send Location When Leaving Home

```yaml
automation:
  - alias: "Send Location When Leaving"
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
          address: "I just left home"
```

### Poll for Dinner Choice

```yaml
script:
  dinner_poll:
    alias: "Send Dinner Poll"
    sequence:
      - service: evolution_api.send_poll
        data:
          phone_number: "+1234567890"
          poll_name: "What should we have for dinner tonight?"
          poll_options: "Pizza, Sushi, Tacos, Pasta, Salad"
          max_selections: 1
```

## Phone Number Format

Phone numbers should include the country code without any special characters:
- ✅ `+1234567890`
- ✅ `1234567890`
- ❌ `+1 (234) 567-890`
- ❌ `234-567-890`

## Troubleshooting

### Connection Failed
- Verify your Evolution API server is running and accessible
- Check that the server URL is correct (include `https://` or `http://`)
- Ensure your API key is valid

### Instance Not Connected
- Open your Evolution API dashboard
- Scan the QR code with WhatsApp on your phone
- Wait for the connection to be established

### Messages Not Sending
- Check that the phone number format is correct
- Verify the recipient has WhatsApp installed
- Check Home Assistant logs for error messages

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This integration is not affiliated with WhatsApp or Meta. Use responsibly and in accordance with WhatsApp's Terms of Service.
