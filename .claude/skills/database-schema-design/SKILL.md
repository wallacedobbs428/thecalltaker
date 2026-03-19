---
name: database-schema-design
description: "Design data schemas, state file structures, and data models. Use when planning JSON state files, database tables, data relationships, migration strategies, or data validation rules. Covers schema design patterns, normalization, indexing, and JSON document design."
category: engineering
---

# Database & Schema Design

Design data structures that are reliable, queryable, and evolvable.

---

## JSON State File Design (Primary for Ops Scripts)

### Schema Template
```json
{
  "_meta": {
    "version": 2,
    "engine": "max-engine",
    "created": "2026-01-15T00:00:00Z",
    "last_modified": "2026-03-19T14:00:00Z"
  },
  "contacts": {
    "contact_id_123": {
      "first_seen": "2026-03-15T10:00:00Z",
      "last_touched": "2026-03-19T08:00:00Z",
      "score": 85,
      "touches": [
        {"type": "email", "date": "2026-03-15", "template": "welcome"},
        {"type": "sms", "date": "2026-03-17", "template": "followup-1"}
      ],
      "tags": ["hvac", "pilot-candidate"],
      "status": "active"
    }
  },
  "daily_counts": {
    "2026-03-19": {"emails": 12, "sms": 8, "calls": 3}
  },
  "config": {
    "max_daily_emails": 30,
    "max_daily_sms": 20
  }
}
```

### Design Rules for State Files

1. **Always include `_meta.version`** — enables migration when schema changes
2. **Use ISO 8601 dates** — `2026-03-19T14:00:00Z`, not timestamps or custom formats
3. **Use contact ID as key** — O(1) lookup, no scanning
4. **Store arrays for history** — touches, events, scores over time
5. **Separate config from data** — easy to change limits without touching contacts
6. **Daily counts by date string** — easy to query, easy to prune old dates

### Schema Migration Pattern
```python
def migrate_state(state):
    version = state.get("_meta", {}).get("version", 1)

    if version < 2:
        # v1 → v2: Add daily_counts section
        state.setdefault("daily_counts", {})
        state["_meta"]["version"] = 2

    if version < 3:
        # v2 → v3: Add status field to contacts
        for cid, contact in state.get("contacts", {}).items():
            contact.setdefault("status", "active")
        state["_meta"]["version"] = 3

    return state
```

---

## Atomic State File Operations

Always use atomic writes to prevent corruption:

```python
import json
import os
import tempfile

def save_state(filepath, state):
    """Atomic write — never corrupts state file."""
    state["_meta"]["last_modified"] = datetime.now().isoformat()
    dir_name = os.path.dirname(filepath)

    with tempfile.NamedTemporaryFile(
        mode='w', dir=dir_name, suffix='.tmp', delete=False
    ) as f:
        json.dump(state, f, indent=2, default=str)
        temp_path = f.name

    os.replace(temp_path, filepath)  # Atomic on POSIX

def load_state(filepath, default=None):
    """Load state with corruption recovery."""
    try:
        with open(filepath) as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        if default:
            return default
        # Try backup
        backup = filepath + ".bak"
        if os.path.exists(backup):
            with open(backup) as f:
                return json.load(f)
        raise
```

---

## Data Modeling Patterns

### One-to-Many (Contact → Touches)
```json
{
  "contacts": {
    "abc123": {
      "name": "John Smith",
      "touches": [
        {"date": "2026-03-15", "type": "email", "engine": "max"},
        {"date": "2026-03-17", "type": "sms", "engine": "donny"}
      ]
    }
  }
}
```

### Cross-Reference (Contact Registry)
```json
{
  "abc123": {
    "last_email": "2026-03-18T10:00:00Z",
    "last_sms": "2026-03-17T14:00:00Z",
    "engines": {
      "max": {"last_touch": "2026-03-18", "touch_count": 3},
      "donny": {"last_touch": "2026-03-17", "touch_count": 1}
    }
  }
}
```

### Time-Series (Daily Metrics)
```json
{
  "metrics": {
    "2026-03-19": {
      "emails_sent": 45,
      "sms_sent": 22,
      "calls_made": 8,
      "demos_booked": 2,
      "revenue": 0
    }
  }
}
```

---

## Validation Rules

```python
def validate_contact(contact):
    """Validate contact data before saving."""
    errors = []

    if not contact.get("id"):
        errors.append("Missing contact ID")

    phone = contact.get("phone", "")
    if phone and not phone.startswith("+1"):
        errors.append(f"Phone must be E.164 format: {phone}")

    email = contact.get("email", "")
    if email and "@" not in email:
        errors.append(f"Invalid email: {email}")

    score = contact.get("score", 0)
    if not (0 <= score <= 100):
        errors.append(f"Score out of range: {score}")

    return errors
```

---

## Data Cleanup / Pruning

```python
def prune_old_data(state, max_age_days=90):
    """Remove data older than max_age_days."""
    cutoff = datetime.now() - timedelta(days=max_age_days)
    cutoff_str = cutoff.strftime("%Y-%m-%d")

    # Prune daily counts
    state["daily_counts"] = {
        date: counts
        for date, counts in state.get("daily_counts", {}).items()
        if date >= cutoff_str
    }

    # Prune completed contacts
    for cid in list(state.get("contacts", {}).keys()):
        contact = state["contacts"][cid]
        if contact.get("status") == "closed":
            last_touch = contact.get("last_touched", "")
            if last_touch < cutoff_str:
                del state["contacts"][cid]

    return state
```
