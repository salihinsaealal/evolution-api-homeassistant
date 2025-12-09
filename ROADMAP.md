# Evolution API Home Assistant Integration - Roadmap

## Current Version: 1.0.0
- Basic config flow
- 9 messaging services
- Connection status sensor

---

## Phase 1: Entity Enrichment (v1.1.0)

### Goals
- Add more entities without excessive API calls
- Use "fetch on demand" pattern via button entities
- Enrich device information

### Tasks

#### 1.1 Profile Sensor
- [ ] Fetch profile info (name, phone, picture URL)
- [ ] Store as sensor attributes
- [ ] Only refresh on button press or service call

#### 1.2 Groups Sensor  
- [ ] Create sensor with group count as state
- [ ] Store group list as attribute (id, name, participants count)
- [ ] Button entity to refresh groups list

#### 1.3 Button Entities
- [ ] "Refresh Profile" button
- [ ] "Refresh Groups" button
- [ ] "Refresh Connection" button

#### 1.4 Device Info Enhancement
- [ ] Add profile picture as device image (if supported)
- [ ] Add phone number to device info
- [ ] Add WhatsApp version info

### API Endpoints Needed
- `GET /chat/fetchProfilePictureUrl/{instance}` - Profile picture
- `GET /group/fetchAllGroups/{instance}` - Groups list
- `GET /instance/connectionState/{instance}` - Already implemented

---

## Phase 2: Service UI Polish (v1.2.x)

### Goals
- Make all services usable via UI without YAML knowledge
- Support multiple instances properly
- Return useful response data

### Tasks

#### 2.1 Improve Service Selectors
- [ ] Add `device` selector to target specific instance
- [ ] Use `entity` selector where applicable
- [ ] Add `area` selector for location services
- [ ] Improve number selectors with proper min/max/step

#### 2.2 Multi-Instance Support
- [ ] Allow selecting which instance to use per service call
- [ ] Default to first instance if not specified
- [ ] Show instance name in service UI

#### 2.3 Service Response Data
- [ ] Return message ID after sending
- [ ] Return delivery status
- [ ] Enable use in scripts with response variables

#### 2.4 New Convenience Services
- [ ] `send_template` - For business API templates
- [ ] `send_buttons` - Interactive buttons
- [ ] `send_list` - List messages
- [ ] `get_profile_picture` - Fetch contact's profile pic

---

## Phase 3: Advanced Features (v2.0.0)

### Goals
- Real-time message handling
- Full automation support
- Enterprise features

### Tasks

#### 3.1 Webhook Support (Incoming Messages)
- [ ] Register webhook with Evolution API
- [ ] Create event entity for incoming messages
- [ ] Fire Home Assistant events on message received
- [ ] Support message filtering (by sender, content, etc.)

#### 3.2 Device Triggers
- [ ] "Message received" trigger
- [ ] "Connection state changed" trigger
- [ ] "Group joined/left" trigger

#### 3.3 Diagnostics
- [ ] Add diagnostics.py for troubleshooting
- [ ] Include sanitized config
- [ ] Include API connection test results
- [ ] Include recent error logs

#### 3.4 Message History (Optional)
- [ ] Store recent messages locally
- [ ] Create sensor with last message info
- [ ] Attribute with message history

---

## Implementation Notes

### API Call Strategy
To minimize API calls:
1. **Connection Status**: Poll every 60 seconds (current)
2. **Profile/Groups**: Fetch ONLY when button pressed or service called
3. **Webhooks**: Real-time, no polling needed

### Data Storage
- Use `hass.data[DOMAIN]` for runtime data
- Consider `Store` helper for persistent data (message history)

### Error Handling
- Graceful degradation if API unavailable
- Clear error messages in UI
- Retry logic for transient failures

---

## Breaking Changes Policy
- Major version (2.x): May include breaking changes
- Minor version (1.x): Backward compatible additions
- Patch version (1.0.x): Bug fixes only

---

## Contributing
See CONTRIBUTING.md for guidelines on submitting changes.
