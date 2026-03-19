---
name: python-performance-optimization
description: "Optimize Python script performance. Use when scripts are slow, consuming too much memory, making too many API calls, or need to handle more data. Covers profiling, caching, async I/O, batch processing, memory optimization, and algorithmic improvements."
category: python
---

# Python Performance Optimization

Profile, identify bottlenecks, and optimize Python scripts for speed and memory efficiency.

---

## Step 1: Profile Before Optimizing

NEVER guess where the bottleneck is. Always measure first.

### Time Profiling
```python
import cProfile
import pstats

# Profile a function
cProfile.run('main()', 'output.prof')
stats = pstats.Stats('output.prof')
stats.sort_stats('cumulative').print_stats(20)

# Quick timing
import time
start = time.perf_counter()
result = expensive_function()
print(f"Took {time.perf_counter() - start:.3f}s")
```

### Memory Profiling
```python
# pip install memory-profiler
from memory_profiler import profile

@profile
def process_leads():
    data = load_all_leads()  # Shows memory per line
    ...
```

### Line-by-Line Profiling
```python
# pip install line-profiler
# kernprof -l -v script.py
@profile
def slow_function():
    ...
```

---

## Common Bottleneck Patterns & Fixes

### 1. Repeated API Calls (Most Common in Ops Scripts)

**Problem:** Calling GHL API in a loop for each contact
```python
# SLOW — N API calls
for contact in contacts:
    data = ghl_get(f"/contacts/{contact['id']}")
```

**Fix:** Batch requests, cache results
```python
# FAST — Use list endpoint with pagination
all_contacts = []
page = 1
while True:
    resp = ghl_get(f"/contacts?limit=100&page={page}")
    all_contacts.extend(resp.get('contacts', []))
    if len(resp.get('contacts', [])) < 100:
        break
    page += 1

# Cache with TTL
from functools import lru_cache
import time

_cache = {}
def cached_get(url, ttl=300):
    now = time.time()
    if url in _cache and now - _cache[url][1] < ttl:
        return _cache[url][0]
    result = ghl_get(url)
    _cache[url] = (result, now)
    return result
```

### 2. File I/O in Loops

**Problem:** Reading/writing files inside loops
```python
# SLOW
for lead in leads:
    with open('state.json') as f:
        state = json.load(f)
    state[lead['id']] = 'processed'
    with open('state.json', 'w') as f:
        json.dump(state, f)
```

**Fix:** Load once, write once
```python
# FAST
with open('state.json') as f:
    state = json.load(f)

for lead in leads:
    state[lead['id']] = 'processed'

with open('state.json', 'w') as f:
    json.dump(state, f)
```

### 3. String Concatenation

**Problem:** Building strings with `+=`
```python
# SLOW — O(n^2) for large strings
body = ""
for line in lines:
    body += line + "\n"
```

**Fix:** Use join
```python
# FAST — O(n)
body = "\n".join(lines)
```

### 4. Searching in Lists

**Problem:** Checking membership in large lists
```python
# SLOW — O(n) per lookup
processed = []
if contact_id in processed:  # Linear scan
    ...
```

**Fix:** Use sets for lookups
```python
# FAST — O(1) per lookup
processed = set()
if contact_id in processed:  # Hash lookup
    ...
```

### 5. Unnecessary Data Loading

**Problem:** Loading entire datasets when you need a subset
```python
# SLOW — loads 10K leads into memory
with open('master-all-industries.json') as f:
    all_leads = json.load(f)
hvac_leads = [l for l in all_leads if l['industry'] == 'hvac']
```

**Fix:** Stream or filter early
```python
# BETTER — generator for large files
import ijson  # pip install ijson
def get_hvac_leads(filepath):
    with open(filepath, 'rb') as f:
        for lead in ijson.items(f, 'item'):
            if lead.get('industry') == 'hvac':
                yield lead
```

---

## Async I/O for Network-Bound Scripts

When making many HTTP requests:

```python
import asyncio
import aiohttp

async def fetch_contact(session, contact_id):
    url = f"https://services.leadconnectorhq.com/contacts/{contact_id}"
    async with session.get(url, headers=HEADERS) as resp:
        return await resp.json()

async def fetch_all(contact_ids):
    async with aiohttp.ClientSession() as session:
        # Process in batches of 10 to respect rate limits
        results = []
        for i in range(0, len(contact_ids), 10):
            batch = contact_ids[i:i+10]
            tasks = [fetch_contact(session, cid) for cid in batch]
            results.extend(await asyncio.gather(*tasks))
            await asyncio.sleep(1)  # Rate limit pause
        return results

# Run
contacts = asyncio.run(fetch_all(contact_ids))
```

---

## Memory Optimization

### Use Generators Instead of Lists
```python
# BAD — stores all in memory
def get_all_emails(contacts):
    return [c['email'] for c in contacts if c.get('email')]

# GOOD — yields one at a time
def get_all_emails(contacts):
    for c in contacts:
        if c.get('email'):
            yield c['email']
```

### Process Files in Chunks
```python
def process_large_csv(filepath, chunk_size=1000):
    import csv
    with open(filepath) as f:
        reader = csv.DictReader(f)
        chunk = []
        for row in reader:
            chunk.append(row)
            if len(chunk) >= chunk_size:
                process_chunk(chunk)
                chunk = []
        if chunk:
            process_chunk(chunk)
```

### Release Memory Explicitly
```python
import gc

big_data = load_massive_dataset()
results = process(big_data)
del big_data  # Free memory
gc.collect()  # Force garbage collection
```

---

## Rate Limiting Pattern

For API-heavy scripts (GHL, Bland.ai):

```python
import time
from collections import deque

class RateLimiter:
    def __init__(self, max_calls, period):
        self.max_calls = max_calls
        self.period = period
        self.calls = deque()

    def wait(self):
        now = time.time()
        while self.calls and self.calls[0] < now - self.period:
            self.calls.popleft()
        if len(self.calls) >= self.max_calls:
            sleep_time = self.calls[0] + self.period - now
            time.sleep(sleep_time)
        self.calls.append(time.time())

# Usage: 100 calls per minute
limiter = RateLimiter(100, 60)
for contact in contacts:
    limiter.wait()
    ghl_get(f"/contacts/{contact['id']}")
```

---

## Quick Wins

1. **Cache API responses** with TTL (biggest impact for ops scripts)
2. **Batch API calls** instead of one-by-one
3. **Use sets** for membership checks on large collections
4. **Load state files once**, write once (not in loops)
5. **Add sleep/rate-limiting** to prevent 429s (which cause retries = slower)
6. **Use `json.dumps` with `default=str`** to avoid serialization errors that cause retries
7. **Profile before optimizing** — the bottleneck is rarely where you think
