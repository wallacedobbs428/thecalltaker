---
name: code-refactoring
description: "Refactor code for better readability, maintainability, and performance. Use when cleaning up messy code, reducing duplication, extracting functions, simplifying conditionals, or restructuring modules. Covers refactoring patterns, code smells, and safe refactoring techniques."
category: engineering
---

# Code Refactoring

Improve code structure without changing behavior. Always have tests before refactoring.

---

## Refactoring Decision Framework

### When to Refactor
- Before adding a new feature to messy code
- When you've touched the same code 3+ times
- When a function exceeds ~50 lines
- When you can't understand code you wrote last month
- When copy-pasting instead of reusing

### When NOT to Refactor
- Code that works and won't be touched again
- During a production emergency
- Without tests to verify behavior is preserved
- Just to match a style preference (not a real improvement)

---

## Top Code Smells & Fixes

### 1. Long Function → Extract Functions
```python
# BEFORE — 80-line function doing 5 things
def process_lead(lead):
    # validate...20 lines
    # score...15 lines
    # tag...10 lines
    # notify...15 lines
    # save...20 lines

# AFTER — clear, testable pieces
def process_lead(lead):
    if not validate_lead(lead):
        return None
    score = calculate_score(lead)
    tags = generate_tags(lead, score)
    notify_if_hot(lead, score)
    save_lead(lead, score, tags)
```

### 2. Duplicated Code → Shared Function
```python
# BEFORE — same pattern in 4 engines
def max_send_email(contact, subject, body):
    html = f"<html><body>{body}<br><br>- The Call Taker Team</body></html>"
    ghl_post(f"/conversations/messages", {
        "type": "Email", "contactId": contact["id"],
        "subject": subject, "html": html
    })

# AFTER — one shared function
# In tct_common.py:
def send_email(contact_id, subject, body, sender="The Call Taker Team"):
    html = f"<html><body>{body}<br><br>- {sender}</body></html>"
    return ghl_post("/conversations/messages", {
        "type": "Email", "contactId": contact_id,
        "subject": subject, "html": html
    })
```

### 3. Deep Nesting → Early Returns
```python
# BEFORE — pyramid of doom
def handle_reply(msg):
    if msg:
        if msg.get("type") == "Email":
            if msg.get("direction") == "inbound":
                body = msg.get("body", "")
                if body:
                    if not is_auto_reply(body):
                        process_reply(msg)

# AFTER — flat and readable
def handle_reply(msg):
    if not msg:
        return
    if msg.get("type") != "Email":
        return
    if msg.get("direction") != "inbound":
        return
    body = msg.get("body", "")
    if not body or is_auto_reply(body):
        return
    process_reply(msg)
```

### 4. Magic Numbers → Named Constants
```python
# BEFORE
if score >= 70:
    send_urgent()
elif score >= 45:
    queue_outreach()

# AFTER
SCORE_URGENT = 70
SCORE_MEDIUM = 45

if score >= SCORE_URGENT:
    send_urgent()
elif score >= SCORE_MEDIUM:
    queue_outreach()
```

### 5. Boolean Parameters → Separate Functions
```python
# BEFORE — what does True mean?
send_message(contact, "Hello", True, False)

# AFTER — self-documenting
send_sms(contact, "Hello")
send_email(contact, "Hello")
```

### 6. Dictionary Soup → Data Classes
```python
# BEFORE — no structure, typos cause silent bugs
lead = {"name": "John", "scroe": 85}  # typo goes unnoticed

# AFTER — structured, IDE-friendly
from dataclasses import dataclass

@dataclass
class Lead:
    name: str
    score: int
    industry: str
    phone: str = ""
    email: str = ""
```

---

## Safe Refactoring Steps

1. **Verify tests exist** (or write them first)
2. **Make one small change** at a time
3. **Run tests** after each change
4. **Commit** after each successful refactor
5. **Never mix** refactoring with feature work in the same commit

---

## Quick Refactoring Recipes

### Replace Conditional with Dictionary
```python
# BEFORE
if industry == "hvac":
    job_word = "service call"
elif industry == "dental":
    job_word = "appointment"
elif industry == "legal":
    job_word = "case"
else:
    job_word = "job"

# AFTER
JOB_WORDS = {
    "hvac": "service call",
    "dental": "appointment",
    "legal": "case",
}
job_word = JOB_WORDS.get(industry, "job")
```

### Simplify Boolean Expressions
```python
# BEFORE
if is_active == True:
    if has_email == True or has_phone == True:
        return True
    else:
        return False
else:
    return False

# AFTER
return is_active and (has_email or has_phone)
```

### Extract Configuration
```python
# BEFORE — hardcoded everywhere
ghl_get(url, headers={"Authorization": "Bearer pit-771d...", "Version": "2021-07-28"})

# AFTER — single config source
from config import GHL_API_KEY, GHL_API_VERSION
# Used in tct_common.py wrapper, never repeated
```
