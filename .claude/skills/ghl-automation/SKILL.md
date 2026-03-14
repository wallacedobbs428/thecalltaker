---
name: ghl-automation
description: "Automate GoHighLevel (GHL) operations -- manage contacts, pipelines, opportunities, tags, custom fields, calendars, appointments, conversations, workflows, and voice AI -- using the GHL REST API v2. This skill should be used when performing CRM operations, lead management, appointment scheduling, or voice AI configuration in GoHighLevel."
category: crm
---

# GoHighLevel (GHL) Automation

Manage your GoHighLevel CRM -- create and update contacts, move opportunities through pipelines, schedule appointments, send messages via conversations, configure workflows, and manage voice AI agents -- all through the GHL REST API v2.

**API Base URL:** `https://services.leadconnectorhq.com`

**API Docs:** [highlevel.stoplight.io](https://highlevel.stoplight.io/)

---

## Setup

### Authentication

All requests require a Bearer token in the `Authorization` header and a `Version` header specifying the API version for each endpoint.

```bash
curl -X GET "https://services.leadconnectorhq.com/contacts/{contactId}" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Version: 2021-07-28" \
  -H "Accept: application/json"
```

### Required Headers

| Header | Value | Notes |
|--------|-------|-------|
| `Authorization` | `Bearer {api_key}` | Required on every request |
| `Version` | Endpoint-specific | See per-endpoint version below |
| `Content-Type` | `application/json` | Required for POST/PUT/PATCH/DELETE |
| `Accept` | `application/json` | Recommended |
| `User-Agent` | Any non-empty string | **MUST be set** to avoid Cloudflare 403 |

### Location ID

Most endpoints require a `locationId` parameter (query or body). This identifies the GHL sub-account.

---

## Core Workflows

### 1. Contacts

Create, update, search, and manage CRM contacts.

**API Version:** `2021-07-28`

#### Search Contacts

**Endpoint:** `GET /contacts/`

**Example:**
```bash
curl -X GET "https://services.leadconnectorhq.com/contacts/?locationId={locationId}&query=john@example.com&limit=20" \
  -H "Authorization: Bearer {api_key}" \
  -H "Version: 2021-07-28"
```

**Key parameters:**
- `locationId` (required) -- Sub-account ID
- `query` -- Search by name, email, phone, or company
- `limit` -- Results per page (default 20, max 100)
- `page` -- Page number for pagination (NOT `offset`)

#### Get Contact

**Endpoint:** `GET /contacts/{contactId}`

#### Create Contact

**Endpoint:** `POST /contacts/`

**Key parameters:**
- `locationId` (required)
- `firstName`, `lastName` -- Contact name
- `email` -- Email address
- `phone` -- Phone in `+1XXXXXXXXXX` format
- `companyName` -- Business name
- `tags` -- Array of tag strings
- `source` -- Lead source
- `customFields` -- Array of `{id, field_value}` objects

**Example body:**
```json
{
  "locationId": "your_location_id",
  "firstName": "John",
  "lastName": "Smith",
  "email": "john@acme.com",
  "phone": "+16155551234",
  "companyName": "Acme HVAC",
  "tags": ["pilot-candidate", "hvac"],
  "source": "cold-email"
}
```

#### Update Contact

**Endpoint:** `PUT /contacts/{contactId}`

Same body fields as create. Omitted fields are not changed.

#### Delete Contact

**Endpoint:** `DELETE /contacts/{contactId}`

#### Add/Remove Tags

**Endpoint:** `POST /contacts/{contactId}/tags`

```json
{
  "tags": ["hot-lead", "demo-caller"]
}
```

**Endpoint:** `DELETE /contacts/{contactId}/tags`

```json
{
  "tags": ["cold-lead"]
}
```

#### Add Contact Notes

**Endpoint:** `POST /contacts/{contactId}/notes`

```json
{
  "body": "Called 3/14, interested in pilot program."
}
```

---

### 2. Pipelines

Manage sales pipelines and their stages.

**API Version:** `2021-07-28`

#### List Pipelines

**Endpoint:** `GET /opportunities/pipelines?locationId={locationId}`

Returns all pipelines with their stages.

#### Get Pipeline

**Endpoint:** `GET /opportunities/pipelines/{pipelineId}?locationId={locationId}`

---

### 3. Opportunities

Track deals through pipeline stages.

**API Version:** `2021-07-28`

#### Search Opportunities

**Endpoint:** `GET /opportunities/search`

**Key parameters:**
- `locationId` (required)
- `pipelineId` -- Filter by pipeline
- `stageId` -- Filter by stage
- `status` -- `open`, `won`, `lost`, `abandoned`, `all`
- `q` -- Search query
- `limit` -- Results per page (max 100)
- `page` -- Page number

#### Create Opportunity

**Endpoint:** `POST /opportunities/`

**Key parameters:**
- `pipelineId` (required)
- `locationId` (required)
- `name` (required) -- Deal name
- `stageId` (required) -- Pipeline stage to place in
- `contactId` (required) -- Associated contact
- `status` -- `open` (default), `won`, `lost`, `abandoned`
- `monetaryValue` -- Deal value in dollars

**Example body:**
```json
{
  "pipelineId": "pipeline_id",
  "locationId": "location_id",
  "name": "Acme HVAC - Pro Plan",
  "stageId": "stage_id",
  "contactId": "contact_id",
  "status": "open",
  "monetaryValue": 297
}
```

#### Update Opportunity

**Endpoint:** `PUT /opportunities/{opportunityId}`

Update stage, status, monetary value, or other fields.

#### Delete Opportunity

**Endpoint:** `DELETE /opportunities/{opportunityId}`

#### Update Opportunity Status

**Endpoint:** `PUT /opportunities/{opportunityId}/status`

```json
{
  "status": "won"
}
```

---

### 4. Tags

Manage tags at the location level.

**API Version:** `2021-07-28`

#### List Tags

**Endpoint:** `GET /locations/{locationId}/tags`

Returns all tags for the sub-account.

#### Create Tag

**Endpoint:** `POST /locations/{locationId}/tags`

```json
{
  "name": "pilot-active"
}
```

#### Get Tag

**Endpoint:** `GET /locations/{locationId}/tags/{tagId}`

#### Update Tag

**Endpoint:** `PUT /locations/{locationId}/tags/{tagId}`

```json
{
  "name": "pilot-converted"
}
```

#### Delete Tag

**Endpoint:** `DELETE /locations/{locationId}/tags/{tagId}`

---

### 5. Custom Fields

Manage custom data fields on contacts.

**API Version:** `2021-07-28`

#### List Custom Fields

**Endpoint:** `GET /locations/{locationId}/customFields`

Returns all custom field definitions with their IDs, names, field types, and accepted values.

#### Create Custom Field

**Endpoint:** `POST /locations/{locationId}/customFields`

```json
{
  "name": "Lead Score",
  "dataType": "NUMBER",
  "placeholder": "0-100"
}
```

**Supported data types:** `TEXT`, `LARGE_TEXT`, `NUMBER`, `MONETARY`, `PHONE`, `EMAIL`, `DATE`, `CHECKBOX`, `SINGLE_OPTIONS`, `MULTIPLE_OPTIONS`, `FILE_UPLOAD`, `SIGNATURE`

#### Update Custom Field

**Endpoint:** `PUT /locations/{locationId}/customFields/{customFieldId}`

#### Delete Custom Field

**Endpoint:** `DELETE /locations/{locationId}/customFields/{customFieldId}`

#### Set Custom Field Value on Contact

Use the contact update endpoint with `customFields` array:

```json
{
  "customFields": [
    {
      "id": "custom_field_id",
      "field_value": "85"
    }
  ]
}
```

---

### 6. Calendars

Manage booking calendars and availability.

**API Version:** `2021-04-15`

#### List Calendars

**Endpoint:** `GET /calendars/?locationId={locationId}`

Returns all calendars with their IDs, names, and settings.

#### Get Calendar

**Endpoint:** `GET /calendars/{calendarId}`

#### Create Calendar

**Endpoint:** `POST /calendars/`

**Key parameters:**
- `locationId` (required)
- `name` (required)
- `description`
- `slug` -- URL-friendly identifier
- `widgetType` -- `default`, `classic`, `neo`
- `calendarType` -- `RoundRobin`, `event`, `class_booking`, `collective`, `service_booking`
- `slotDuration` -- Duration in minutes
- `availabilities` -- Array of day/time availability windows

#### Update Calendar

**Endpoint:** `PUT /calendars/{calendarId}`

#### Delete Calendar

**Endpoint:** `DELETE /calendars/{calendarId}`

#### Get Free Slots

**Endpoint:** `GET /calendars/{calendarId}/free-slots?startDate={YYYY-MM-DD}&endDate={YYYY-MM-DD}`

Returns available time slots for a date range.

---

### 7. Appointments

Schedule and manage calendar appointments.

**API Version:** `2021-04-15`

#### List Appointments

**Endpoint:** `GET /calendars/events?locationId={locationId}&calendarId={calendarId}&startTime={epoch_ms}&endTime={epoch_ms}`

**Key parameters:**
- `locationId` (required)
- `calendarId` -- Filter by specific calendar
- `startTime` -- Start of range (epoch milliseconds)
- `endTime` -- End of range (epoch milliseconds)

#### Get Appointment

**Endpoint:** `GET /calendars/events/appointments/{eventId}`

#### Create Appointment

**Endpoint:** `POST /calendars/events/appointments`

**Key parameters:**
- `calendarId` (required)
- `locationId` (required)
- `contactId` (required)
- `startTime` (required) -- ISO 8601 datetime
- `endTime` (required) -- ISO 8601 datetime
- `title` -- Appointment title
- `appointmentStatus` -- `confirmed`, `new`, `cancelled`, `showed`, `noshow`, `invalid`
- `notes` -- Additional notes

**Example body:**
```json
{
  "calendarId": "calendar_id",
  "locationId": "location_id",
  "contactId": "contact_id",
  "startTime": "2026-03-15T10:00:00-05:00",
  "endTime": "2026-03-15T10:30:00-05:00",
  "title": "Demo Call - Acme HVAC",
  "appointmentStatus": "confirmed"
}
```

#### Update Appointment

**Endpoint:** `PUT /calendars/events/appointments/{eventId}`

#### Delete Appointment

**Endpoint:** `DELETE /calendars/events/appointments/{eventId}`

---

### 8. Conversations & Messages

Send and receive messages (SMS, email) through the conversations API.

**API Version:** `2021-04-15`

#### List Conversations

**Endpoint:** `GET /conversations/search?locationId={locationId}`

**Key parameters:**
- `locationId` (required)
- `contactId` -- Filter by contact
- `limit` -- Max results (default 20)

#### Get Conversation

**Endpoint:** `GET /conversations/{conversationId}`

#### Create Conversation

**Endpoint:** `POST /conversations/`

```json
{
  "locationId": "location_id",
  "contactId": "contact_id"
}
```

#### Send SMS

**Endpoint:** `POST /conversations/messages`

```json
{
  "type": "SMS",
  "contactId": "contact_id",
  "message": "Hey! Just following up on the demo you heard."
}
```

**Key fields:**
- `type` -- `SMS`, `Email`, `WhatsApp`, `GMB`, `IG`, `FB`, `Custom`, `Live_Chat`
- `contactId` (required)
- `message` -- SMS/chat body text

#### Send Email

**Endpoint:** `POST /conversations/messages`

```json
{
  "type": "Email",
  "contactId": "contact_id",
  "subject": "Your AI Receptionist Demo Results",
  "html": "<h1>Here are your results</h1><p>Your demo call lasted 2 minutes...</p>",
  "emailFrom": "The Call Taker <notifications@mail.thecalltaker.com>"
}
```

**Key fields for email:**
- `type` -- `Email`
- `contactId` (required)
- `subject` -- Email subject line
- `html` -- Email body (**NOT** `message` -- use `html` for email body content)
- `emailFrom` -- Sender name and address

#### Get Messages

**Endpoint:** `GET /conversations/{conversationId}/messages`

---

### 9. Workflows

Manage automation workflows.

**API Version:** `2021-07-28`

#### List Workflows

**Endpoint:** `GET /workflows/?locationId={locationId}`

Returns all workflows with their IDs, names, and statuses.

#### Get Workflow

**Endpoint:** `GET /workflows/{workflowId}?locationId={locationId}`

---

### 10. Voice AI

Configure and manage Voice AI agents for phone handling.

**API Version:** `2021-04-15`

#### List Voice AI Agents

**Endpoint:** `GET /voice-ai/agents?locationId={locationId}`

Returns all voice agents with their IDs, names, and configurations.

#### Get Voice AI Agent

**Endpoint:** `GET /voice-ai/agents/{agentId}?locationId={locationId}`

#### Update Voice AI Agent

**Endpoint:** `PATCH /voice-ai/agents/{agentId}?locationId={locationId}`

**Key parameters (in body):**
- `name` -- Agent display name
- `prompt` -- System prompt / instructions
- `welcomeMessage` -- Greeting when call connects
- `voiceId` -- Text-to-speech voice ID
- `responsiveness` -- Float 0-1 (1.0 = fastest response)

**Example:**
```json
{
  "name": "After-Hours AI",
  "prompt": "You are an AI receptionist for {business}...",
  "welcomeMessage": "Thanks for calling! How can I help?",
  "responsiveness": 1.0
}
```

**Important:** The `locationId` goes in the **query string**, NOT the request body.

---

## Tool Sequences

### Sequence: Enroll a New Lead

1. **Create contact** → `POST /contacts/` with name, email, phone, tags
2. **Add to pipeline** → `POST /opportunities/` with contactId, pipelineId, stageId
3. **Send welcome SMS** → `POST /conversations/messages` with type `SMS`
4. **Book appointment** → `POST /calendars/events/appointments` with contactId, calendarId

### Sequence: Move Deal Through Pipeline

1. **Search opportunity** → `GET /opportunities/search?q={name}`
2. **Update stage** → `PUT /opportunities/{id}` with new `stageId`
3. **Notify via SMS** → `POST /conversations/messages` to associated contact

### Sequence: Handle Demo Caller

1. **Search contact by phone** → `GET /contacts/?query={phone}`
2. **Create if not found** → `POST /contacts/` with demo-caller tags
3. **Tag contact** → `POST /contacts/{id}/tags` with `["demo-caller", "hot-demo"]`
4. **Add note** → `POST /contacts/{id}/notes` with call details
5. **Create opportunity** → `POST /opportunities/` in demo pipeline

### Sequence: Configure Voice AI for Client

1. **List agents** → `GET /voice-ai/agents?locationId={id}`
2. **Update prompt** → `PATCH /voice-ai/agents/{agentId}?locationId={id}` with industry-specific prompt
3. **Set voice** → Same PATCH with `voiceId`
4. **Set responsiveness** → Same PATCH with `responsiveness: 1.0`

---

## Known Pitfalls

- **Email body is `html`, NOT `message`**: When sending email via conversations, the body content goes in the `html` field. The `message` field is for SMS/chat only. Using `message` for email results in blank emails.
- **SMS body is `message`**: For SMS, use the `message` field. Do NOT use `html`.
- **Phone format must be `+1XXXXXXXXXX`**: Always include country code. Omitting it causes delivery failures.
- **Pagination uses `page`, NOT `offset`**: GHL uses page-based pagination. Do not use `offset` or `skip` parameters.
- **User-Agent header is mandatory**: Requests without a `User-Agent` header receive Cloudflare 403 errors.
- **API versions vary by endpoint**: Contacts and opportunities use `2021-07-28`. Conversations, calendars, and voice AI use `2021-04-15`. Always set the correct `Version` header.
- **Voice AI `locationId` is a query param**: When PATCHing voice AI agents, `locationId` goes in the URL query string, not the request body. Putting it in the body causes 400 errors.
- **Message objects can be strings**: When reading conversation messages, individual message objects may be plain strings instead of dicts. Always check `isinstance(msg, dict)` before accessing keys.
- **Rate limiting**: GHL enforces rate limits. On 429 responses, back off with delays: 30s → 60s → 120s.
- **API retry backoff**: On 5xx errors, retry with backoff: 5s → 15s → 30s.
- **Conversations API version**: Always use `2021-04-15` for conversations endpoints, not `2021-07-28`.
- **Tags are strings, not objects**: When creating/updating contacts, tags are a plain array of strings `["tag1", "tag2"]`, not objects.
- **Custom field values use `id` not `name`**: When setting custom field values on contacts, reference the field by its `id`, not its `name`. List custom fields first to get IDs.
- **Calendar free slots require date range**: The free-slots endpoint requires both `startDate` and `endDate` in `YYYY-MM-DD` format.
- **Appointment times in ISO 8601**: Use full ISO 8601 with timezone offset (e.g., `2026-03-15T10:00:00-05:00`), not epoch timestamps.
- **Event listing uses epoch milliseconds**: Unlike appointment creation, the events list endpoint uses `startTime`/`endTime` as epoch milliseconds, not ISO 8601.
- **Voice AI endpoint is plural**: The path is `/voice-ai/agents/{id}` (plural "agents"), not `/voice-ai/agent/{id}`.

---

## Quick Reference

| Action | Method | Endpoint | Version | Required Params |
|--------|--------|----------|---------|-----------------|
| Search contacts | `GET` | `/contacts/` | `2021-07-28` | `locationId` |
| Get contact | `GET` | `/contacts/{contactId}` | `2021-07-28` | `contactId` |
| Create contact | `POST` | `/contacts/` | `2021-07-28` | `locationId`, `firstName` or `email` or `phone` |
| Update contact | `PUT` | `/contacts/{contactId}` | `2021-07-28` | `contactId` |
| Delete contact | `DELETE` | `/contacts/{contactId}` | `2021-07-28` | `contactId` |
| Add tags | `POST` | `/contacts/{contactId}/tags` | `2021-07-28` | `contactId`, `tags[]` |
| Remove tags | `DELETE` | `/contacts/{contactId}/tags` | `2021-07-28` | `contactId`, `tags[]` |
| Add note | `POST` | `/contacts/{contactId}/notes` | `2021-07-28` | `contactId`, `body` |
| List pipelines | `GET` | `/opportunities/pipelines` | `2021-07-28` | `locationId` |
| Search opportunities | `GET` | `/opportunities/search` | `2021-07-28` | `locationId` |
| Create opportunity | `POST` | `/opportunities/` | `2021-07-28` | `pipelineId`, `locationId`, `name`, `stageId`, `contactId` |
| Update opportunity | `PUT` | `/opportunities/{id}` | `2021-07-28` | `opportunityId` |
| Delete opportunity | `DELETE` | `/opportunities/{id}` | `2021-07-28` | `opportunityId` |
| List tags | `GET` | `/locations/{locationId}/tags` | `2021-07-28` | `locationId` |
| Create tag | `POST` | `/locations/{locationId}/tags` | `2021-07-28` | `locationId`, `name` |
| List custom fields | `GET` | `/locations/{locationId}/customFields` | `2021-07-28` | `locationId` |
| Create custom field | `POST` | `/locations/{locationId}/customFields` | `2021-07-28` | `locationId`, `name`, `dataType` |
| List calendars | `GET` | `/calendars/` | `2021-04-15` | `locationId` |
| Get free slots | `GET` | `/calendars/{id}/free-slots` | `2021-04-15` | `calendarId`, `startDate`, `endDate` |
| List appointments | `GET` | `/calendars/events` | `2021-04-15` | `locationId` |
| Create appointment | `POST` | `/calendars/events/appointments` | `2021-04-15` | `calendarId`, `locationId`, `contactId`, `startTime`, `endTime` |
| Update appointment | `PUT` | `/calendars/events/appointments/{id}` | `2021-04-15` | `eventId` |
| Delete appointment | `DELETE` | `/calendars/events/appointments/{id}` | `2021-04-15` | `eventId` |
| Search conversations | `GET` | `/conversations/search` | `2021-04-15` | `locationId` |
| Send SMS | `POST` | `/conversations/messages` | `2021-04-15` | `contactId`, `type: SMS`, `message` |
| Send email | `POST` | `/conversations/messages` | `2021-04-15` | `contactId`, `type: Email`, `html`, `subject` |
| Get messages | `GET` | `/conversations/{id}/messages` | `2021-04-15` | `conversationId` |
| List workflows | `GET` | `/workflows/` | `2021-07-28` | `locationId` |
| List voice agents | `GET` | `/voice-ai/agents` | `2021-04-15` | `locationId` |
| Update voice agent | `PATCH` | `/voice-ai/agents/{id}` | `2021-04-15` | `agentId`, `locationId` (query) |

---

## API Version Reference

| Endpoint Group | Version Header |
|----------------|---------------|
| Contacts | `2021-07-28` |
| Opportunities | `2021-07-28` |
| Pipelines | `2021-07-28` |
| Tags | `2021-07-28` |
| Custom Fields | `2021-07-28` |
| Workflows | `2021-07-28` |
| Calendars | `2021-04-15` |
| Appointments | `2021-04-15` |
| Conversations | `2021-04-15` |
| Voice AI | `2021-04-15` |

---

## Response Handling

### Pagination Pattern

GHL uses page-based pagination. Always check if more pages exist:

```python
page = 1
all_contacts = []
while True:
    resp = requests.get(
        f"{BASE_URL}/contacts/",
        headers=headers,
        params={"locationId": location_id, "page": page, "limit": 100}
    )
    data = resp.json()
    contacts = data.get("contacts", [])
    all_contacts.extend(contacts)
    if len(contacts) < 100:
        break
    page += 1
```

### Error Handling Pattern

```python
resp = requests.post(url, headers=headers, json=body)
if resp.status_code == 429:
    # Rate limited — back off 30s, 60s, 120s
    time.sleep(30)
    resp = requests.post(url, headers=headers, json=body)
elif resp.status_code >= 500:
    # Server error — retry with backoff 5s, 15s, 30s
    time.sleep(5)
    resp = requests.post(url, headers=headers, json=body)
elif resp.status_code == 400:
    # Bad request — check field names, Version header, and locationId placement
    print(resp.json())
elif resp.status_code == 403:
    # Likely missing User-Agent header or invalid API key
    pass
```
