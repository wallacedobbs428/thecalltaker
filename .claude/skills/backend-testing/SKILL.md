---
name: backend-testing
description: "Write and run tests for backend code. Use when creating unit tests, integration tests, API tests, or end-to-end tests for Python scripts, APIs, or backend services. Covers pytest, mocking, fixtures, test organization, CI integration, and test-driven development patterns."
category: testing
---

# Backend Testing — Python Testing Playbook

Write reliable tests for backend scripts, APIs, and automation engines.

---

## Test Organization

```
tests/
├── conftest.py          # Shared fixtures
├── test_engine.py       # Unit tests for engine functions
├── test_api.py          # API integration tests
├── test_state.py        # State file read/write tests
├── test_notifications.py # Notification routing tests
└── mocks/
    ├── ghl_responses.py # Mock GHL API responses
    └── state_fixtures.py # Sample state data
```

---

## pytest Basics

### Test File Structure
```python
import pytest
from unittest.mock import patch, MagicMock

class TestLeadScoring:
    """Tests for lead scoring logic."""

    def test_high_value_industry_scores_higher(self):
        lead = {"industry": "hvac", "reviews": 45, "rating": 3.2}
        score = calculate_score(lead)
        assert score >= 60

    def test_missing_fields_dont_crash(self):
        lead = {"industry": "hvac"}  # Missing reviews, rating
        score = calculate_score(lead)
        assert isinstance(score, (int, float))
        assert 0 <= score <= 100

    def test_empty_lead_returns_zero(self):
        assert calculate_score({}) == 0

    @pytest.mark.parametrize("industry,min_score", [
        ("hvac", 30),
        ("dental", 30),
        ("locksmith", 25),
        ("other", 10),
    ])
    def test_industry_base_scores(self, industry, min_score):
        lead = {"industry": industry}
        assert calculate_score(lead) >= min_score
```

### Fixtures
```python
# conftest.py
import pytest
import json
import tempfile
import os

@pytest.fixture
def sample_contact():
    return {
        "id": "test123",
        "firstName": "John",
        "lastName": "Smith",
        "email": "john@example.com",
        "phone": "+16155551234",
        "tags": ["pilot-candidate", "hvac"],
    }

@pytest.fixture
def temp_state_file():
    """Provides a temporary state file that auto-cleans up."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"version": 1, "contacts": {}}, f)
        path = f.name
    yield path
    os.unlink(path)

@pytest.fixture
def mock_ghl_api():
    """Mock GHL API calls."""
    with patch('tct_common.ghl_get') as mock_get, \
         patch('tct_common.ghl_post') as mock_post:
        mock_get.return_value = {"contacts": [], "meta": {"total": 0}}
        mock_post.return_value = {"succeeded": True}
        yield {"get": mock_get, "post": mock_post}
```

---

## Mocking External Services

### Mock GHL API
```python
def test_followup_sends_email(mock_ghl_api, sample_contact):
    mock_ghl_api["get"].return_value = {
        "contacts": [sample_contact],
        "meta": {"total": 1}
    }

    result = run_followup(sample_contact["id"])

    mock_ghl_api["post"].assert_called_once()
    call_args = mock_ghl_api["post"].call_args
    assert "html" in call_args[1]  # Email uses html field
    assert sample_contact["firstName"] in call_args[1]["html"]
```

### Mock ntfy Notifications
```python
def test_critical_alert_sends_to_urgent(self):
    with patch('tct_common.ntfy_standard') as mock_ntfy:
        notify_demo_call(
            name="John Smith",
            phone="+16155551234",
            company="Smith HVAC",
            industry="hvac",
            duration=180,
            source="demo-line"
        )
        mock_ntfy.assert_called_once()
        args = mock_ntfy.call_args
        assert "urgent" in str(args).lower() or "CRITICAL" in str(args)
```

### Mock File I/O
```python
def test_state_save_atomic(temp_state_file):
    state = {"version": 1, "contacts": {"abc": {"score": 85}}}
    save_state(temp_state_file, state)

    with open(temp_state_file) as f:
        loaded = json.load(f)
    assert loaded["contacts"]["abc"]["score"] == 85
```

---

## Testing Patterns for Ops Scripts

### Pattern 1: Test Command Routing
```python
def test_engine_commands():
    """Verify all documented commands are handled."""
    commands = ["monitor", "followup", "pipeline", "report", "status"]
    for cmd in commands:
        # Should not raise
        result = engine_dispatch(cmd, dry_run=True)
        assert result is not None, f"Command '{cmd}' returned None"
```

### Pattern 2: Test Rate Limiting
```python
def test_respects_daily_send_limit():
    state = {"daily_sends": {"2026-03-19": 29}, "max_daily": 30}
    # Should send (29 < 30)
    assert can_send(state) is True
    state["daily_sends"]["2026-03-19"] = 30
    # Should NOT send (30 >= 30)
    assert can_send(state) is False
```

### Pattern 3: Test Deduplication
```python
def test_no_duplicate_sends(temp_state_file):
    contact_id = "test123"
    # First send should succeed
    assert check_and_record(contact_id, "email", temp_state_file) is True
    # Immediate second send should be blocked
    assert check_and_record(contact_id, "email", temp_state_file) is False
```

### Pattern 4: Test Error Handling
```python
def test_api_failure_doesnt_crash():
    with patch('tct_common.ghl_get', side_effect=Exception("API timeout")):
        # Should handle gracefully, not crash
        result = run_monitor()
        assert result is not None  # Returns error info, not exception
```

---

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_engine.py -v

# Run tests matching pattern
pytest -k "test_scoring" -v

# Run with coverage
pytest --cov=. --cov-report=html tests/

# Run and stop on first failure
pytest -x tests/

# Show print output
pytest -s tests/
```

---

## Test Checklist for New Features

Before shipping any new engine command or script:

- [ ] Happy path test (normal operation)
- [ ] Empty/missing data test (no contacts, empty state)
- [ ] API failure test (mock 429, 500, timeout)
- [ ] Rate limit test (daily/hourly limits respected)
- [ ] Dedup test (same contact not processed twice)
- [ ] State persistence test (state saves and loads correctly)
- [ ] Null safety test (missing fields don't crash)
- [ ] Tag handling test (correct GHL tags applied)
