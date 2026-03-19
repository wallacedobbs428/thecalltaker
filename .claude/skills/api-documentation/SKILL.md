---
name: api-documentation
description: "Write clear, complete API documentation. Use when documenting REST endpoints, webhook payloads, SDK functions, configuration options, or integration guides. Covers OpenAPI/Swagger specs, endpoint docs, request/response examples, error codes, and authentication guides."
category: documentation
---

# API Documentation

Write documentation that developers can actually use without asking questions.

---

## Documentation Structure

Every API doc should include:

1. **Overview** — What the API does, who it's for, base URL
2. **Authentication** — How to get and use credentials
3. **Endpoints** — Each endpoint with method, URL, params, body, response
4. **Error Codes** — What can go wrong and how to fix it
5. **Rate Limits** — Requests per minute/hour, what happens when exceeded
6. **Examples** — Real curl/Python/JS examples that work when copied

---

## Endpoint Documentation Template

```markdown
## Create Contact

Creates a new contact in the CRM.

**Endpoint:** `POST /contacts`

**Headers:**
| Header | Required | Value |
|--------|----------|-------|
| Authorization | Yes | `Bearer {api_key}` |
| Content-Type | Yes | `application/json` |
| Version | Yes | `2021-07-28` |

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| firstName | string | Yes | Contact's first name |
| lastName | string | No | Contact's last name |
| email | string | No | Email address |
| phone | string | No | Phone in E.164 format (+1XXXXXXXXXX) |
| tags | string[] | No | Array of tag names |

**Example Request:**
```bash
curl -X POST "https://services.leadconnectorhq.com/contacts" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Version: 2021-07-28" \
  -d '{
    "firstName": "John",
    "lastName": "Smith",
    "email": "john@smithhvac.com",
    "phone": "+16155551234",
    "tags": ["pilot-candidate", "hvac"]
  }'
```

**Success Response (201):**
```json
{
  "contact": {
    "id": "abc123",
    "firstName": "John",
    "lastName": "Smith",
    "email": "john@smithhvac.com",
    "phone": "+16155551234",
    "tags": ["pilot-candidate", "hvac"],
    "dateAdded": "2026-03-19T14:00:00.000Z"
  }
}
```

**Error Responses:**
| Code | Reason | Fix |
|------|--------|-----|
| 400 | Missing required field | Include firstName |
| 401 | Invalid API key | Check Authorization header |
| 409 | Duplicate contact | Contact with this email/phone exists |
| 429 | Rate limited | Wait and retry after Retry-After header |
```

---

## Writing Style Rules

1. **Use second person** — "You can create a contact" not "Users can create contacts"
2. **Show, don't tell** — Every endpoint needs a working example
3. **Be specific about types** — "string" not "text", "integer" not "number"
4. **Document edge cases** — What happens with empty arrays? Null fields? Unicode?
5. **Include error examples** — Not just success cases
6. **Version your docs** — Note when endpoints were added/changed

---

## Python SDK Documentation Template

```markdown
## send_email(contact_id, subject, body, sender=None)

Sends an email to a contact via GHL conversations API.

**Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| contact_id | str | required | GHL contact ID |
| subject | str | required | Email subject line |
| body | str | required | HTML email body |
| sender | str | "The Call Taker Team" | Sender name in signature |

**Returns:** `dict` — GHL API response with message ID

**Raises:**
- `ValueError` — If contact_id is empty
- `APIError` — If GHL returns non-200 status

**Example:**
```python
from tct_common import send_email

response = send_email(
    contact_id="abc123",
    subject="Your Free Pilot is Ready",
    body="<p>Hey John, your AI receptionist is live...</p>"
)
print(response["messageId"])  # "msg_xyz789"
```

**Notes:**
- Body should be HTML (GHL uses `html` field, NOT `message`)
- Subject line max 200 chars
- Rate limited to 100 emails/hour per location
```

---

## Quick Checklist

Before publishing any API doc:
- [ ] Every endpoint has a working curl example
- [ ] All required vs optional params clearly marked
- [ ] Error responses documented with fix suggestions
- [ ] Authentication section complete with example
- [ ] Rate limits documented
- [ ] Request and response body examples are valid JSON
- [ ] No placeholder values that would confuse copy-pasters
