---
name: api-design-principles
description: "Design clean, consistent, and maintainable APIs. Use when building REST APIs, designing webhook handlers, structuring API wrappers, or planning integrations between services. Covers REST conventions, error handling, versioning, rate limiting, and authentication patterns."
category: engineering
---

# API Design Principles

Build APIs that are predictable, well-documented, and easy to integrate with.

---

## REST Conventions

### URL Structure
```
GET    /contacts              # List all
GET    /contacts/{id}         # Get one
POST   /contacts              # Create
PUT    /contacts/{id}         # Full update
PATCH  /contacts/{id}         # Partial update
DELETE /contacts/{id}         # Delete

# Nested resources
GET    /contacts/{id}/messages
POST   /contacts/{id}/messages

# Actions (when CRUD doesn't fit)
POST   /contacts/{id}/actions/archive
POST   /leads/{id}/actions/score
```

### Naming
- Use **nouns** for resources (`/contacts`, not `/getContacts`)
- Use **plural** names (`/leads`, not `/lead`)
- Use **kebab-case** for multi-word (`/lead-scores`, not `/leadScores`)
- Use **query params** for filtering (`/contacts?industry=hvac&status=active`)

---

## Request/Response Patterns

### Successful Response
```json
{
  "data": { "id": "abc123", "name": "John Smith", "score": 85 },
  "meta": { "timestamp": "2026-03-19T14:00:00Z" }
}

// List response
{
  "data": [{ "id": "abc123" }, { "id": "def456" }],
  "meta": { "total": 47, "page": 1, "per_page": 20 }
}
```

### Error Response
```json
{
  "error": {
    "code": "CONTACT_NOT_FOUND",
    "message": "Contact with ID 'abc123' not found",
    "status": 404
  }
}
```

### Pagination
```
GET /contacts?page=2&limit=20

Response:
{
  "data": [...],
  "meta": {
    "total": 1765,
    "page": 2,
    "per_page": 20,
    "total_pages": 89
  }
}
```

---

## Error Handling

### HTTP Status Codes (Use Correctly)
| Code | Meaning | When to Use |
|------|---------|-------------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid input, missing required field |
| 401 | Unauthorized | No/invalid auth token |
| 403 | Forbidden | Valid auth, insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate, state conflict |
| 422 | Unprocessable | Valid JSON but business logic failure |
| 429 | Too Many Requests | Rate limited |
| 500 | Internal Error | Server bug |

### Retry Strategy for API Clients
```python
import time

def api_call_with_retry(method, url, max_retries=3, **kwargs):
    for attempt in range(max_retries + 1):
        try:
            response = method(url, **kwargs)
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 30))
                time.sleep(retry_after)
                continue
            if response.status_code >= 500:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            return response
        except ConnectionError:
            if attempt == max_retries:
                raise
            time.sleep(2 ** attempt)
    return response
```

---

## API Wrapper Pattern

When integrating with external APIs (GHL, Bland.ai):

```python
class APIClient:
    def __init__(self, base_url, api_key, version=None):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "TheCallTaker/1.0",
        })
        if version:
            self.session.headers["Version"] = version

    def get(self, path, params=None):
        return self._request("GET", path, params=params)

    def post(self, path, data=None):
        return self._request("POST", path, json=data)

    def _request(self, method, path, **kwargs):
        url = f"{self.base_url}{path}"
        response = self.session.request(method, url, timeout=30, **kwargs)

        if response.status_code == 429:
            raise RateLimitError(response)
        response.raise_for_status()
        return response.json()
```

---

## Webhook Design

### Receiving Webhooks
```python
def handle_webhook(request):
    # 1. Verify signature
    if not verify_signature(request):
        return {"error": "Invalid signature"}, 401

    # 2. Parse event
    event = request.json
    event_type = event.get("type")

    # 3. Acknowledge immediately (return 200)
    # 4. Process asynchronously if heavy

    # 5. Idempotency — check if already processed
    event_id = event.get("id")
    if already_processed(event_id):
        return {"status": "already_processed"}, 200

    # 6. Route to handler
    handlers = {
        "contact.created": handle_contact_created,
        "payment.received": handle_payment,
        "call.completed": handle_call_completed,
    }
    handler = handlers.get(event_type)
    if handler:
        handler(event)

    mark_processed(event_id)
    return {"status": "ok"}, 200
```

---

## Rate Limiting Your Own APIs

```python
from collections import defaultdict
import time

class SimpleRateLimiter:
    def __init__(self, max_requests=100, window_seconds=60):
        self.max = max_requests
        self.window = window_seconds
        self.requests = defaultdict(list)

    def allow(self, client_id):
        now = time.time()
        # Clean old entries
        self.requests[client_id] = [
            t for t in self.requests[client_id]
            if now - t < self.window
        ]
        if len(self.requests[client_id]) >= self.max:
            return False
        self.requests[client_id].append(now)
        return True
```
