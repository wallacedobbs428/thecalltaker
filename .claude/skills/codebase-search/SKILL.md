---
name: codebase-search
description: "Efficiently search and navigate large codebases. Use when finding specific functions, tracing data flows, locating configuration, understanding dependencies, or mapping code architecture. Covers search strategies, grep patterns, file discovery, and dependency tracing."
category: engineering
---

# Codebase Search

Find anything in any codebase quickly and systematically.

---

## Search Strategy Decision Tree

```
What are you looking for?
├── A specific file → Glob: **/*filename*
├── A function/class → Grep: "def function_name" or "class ClassName"
├── Where something is used → Grep: "function_name(" across all files
├── A config value → Grep: "CONFIG_KEY" or "setting_name"
├── An error message → Grep: "exact error text"
├── A URL/endpoint → Grep: "/api/endpoint"
├── How data flows → Trace: function calls, imports, state files
└── Overall architecture → Read: entry points, config, README
```

---

## Common Search Patterns

### Find Where a Function is Defined
```bash
# Python
grep -rn "def function_name" --include="*.py"

# JavaScript
grep -rn "function functionName\|const functionName\|functionName =" --include="*.js"
```

### Find Where a Function is Called
```bash
grep -rn "function_name(" --include="*.py" | grep -v "def function_name"
```

### Find All Files That Import a Module
```bash
grep -rn "from module_name import\|import module_name" --include="*.py"
```

### Find Configuration Values
```bash
# Environment variables
grep -rn "os.environ\|os.getenv\|ENV\[" --include="*.py"

# Config file references
grep -rn "config\.\|CONFIG\[" --include="*.py"
```

### Find API Endpoints
```bash
# GHL API calls
grep -rn "ghl_get\|ghl_post\|ghl_put" --include="*.py"

# URL patterns
grep -rn "https://\|http://" --include="*.py" | grep -v "#"
```

### Find TODOs and FIXMEs
```bash
grep -rn "TODO\|FIXME\|HACK\|XXX\|WORKAROUND" --include="*.py"
```

---

## Architecture Mapping

### Quick Architecture Scan
1. **Entry points:** `grep -rn "if __name__" --include="*.py"` — finds all runnable scripts
2. **Shared code:** `grep -rn "from .* import\|import .*common" --include="*.py"` — finds shared modules
3. **External APIs:** `grep -rn "requests\.\|aiohttp\|urllib" --include="*.py"` — finds API calls
4. **State files:** `grep -rn "\.json\|\.csv\|\.sqlite" --include="*.py"` — finds data files
5. **Scheduled tasks:** `ls *.plist` or `grep -rn "cron\|schedule\|launchd"` — finds automation

### Dependency Graph (Manual)
```
Start from entry point:
script.py
├── imports tct_common (shared utilities)
│   ├── ghl_get/ghl_post (GHL API)
│   ├── ntfy_standard (notifications)
│   └── contact_registry (shared state)
├── reads state-file.json
├── calls GHL API
├── writes state-file.json
└── sends ntfy notification
```

---

## File Discovery

### Find Files by Pattern
```bash
# All Python files
find . -name "*.py" -type f

# All state/config JSON files
find . -name "*state*.json" -o -name "*config*.json"

# Recently modified files
find . -name "*.py" -mtime -7 -type f  # Modified in last 7 days

# Large files
find . -name "*.py" -size +100k -type f
```

### Find Files by Content
```bash
# Files containing a specific string
grep -rl "GHL_API_KEY" --include="*.py"

# Files NOT containing something
grep -rL "import logging" --include="*.py"  # Python files without logging
```

---

## Tracing Data Flow

### Follow the Data
1. **Find where data enters:** `grep -rn "input\|request\|read\|load\|fetch"`
2. **Find where data transforms:** `grep -rn "process\|transform\|convert\|parse"`
3. **Find where data exits:** `grep -rn "save\|write\|send\|post\|return"`

### Follow an ID/Key Through the System
```bash
# Trace a contact ID
grep -rn "contact_id\|contactId" --include="*.py"

# Trace a tag
grep -rn "pilot-candidate" --include="*.py"

# Trace a state key
grep -rn "daily_sends\|daily_counts" --include="*.py"
```

---

## Quick Reference Commands

| Goal | Command |
|------|---------|
| Find file by name | `find . -name "*pattern*"` |
| Find text in files | `grep -rn "text" --include="*.py"` |
| Count matches | `grep -rc "pattern" --include="*.py"` |
| List file types | `find . -type f \| sed 's/.*\.//' \| sort \| uniq -c \| sort -rn` |
| Find duplicates | `find . -name "*.py" -exec md5sum {} + \| sort \| uniq -d -w32` |
| Recent changes | `git log --oneline -20` |
| Who changed a file | `git log --oneline path/to/file` |
| Blame a line | `git blame path/to/file` |
