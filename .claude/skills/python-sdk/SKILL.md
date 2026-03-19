---
name: python-sdk
description: "Python SDK for inference.sh — build AI applications, create agents, and integrate with 150+ models programmatically. Covers app execution, file operations, sessions, agent development, tool builder, and streaming."
---

# Python SDK for inference.sh

Build AI applications, create agents, and integrate with 150+ models programmatically.

## Installation

```bash
pip install inferencesh
```

## Authentication

Set API key directly or via environment variables.

## Core Capabilities

### App Execution
Run AI applications with basic, fire-and-forget, or streaming modes. Supports infrastructure selection and session management for stateful operations.

### File Operations
Automatic file uploads when local paths are provided as inputs. Manual uploads via `UploadFileOptions` for custom naming, content types, and access control.

### Sessions
Maintain warm workers across multiple invocations using session IDs with configurable timeout periods (1-3600 seconds).

## Agent Development

### Template Agents
Leverage pre-built agents from your workspace for multi-turn conversations with message sending, history retrieval, and reset functionality.

### Ad-hoc Agents
Programmatic construction using the tool builder API with custom tools, system prompts, temperature settings, and token limits.

## Tool Builder System

- **Client Tools**: Execute logic in your code with optional approval workflows
- **App Tools**: Invoke inference.sh applications from agents
- **Agent Tools**: Delegate to sub-agents
- **Webhook Tools**: Call external APIs with secure secret handling
- **Internal Tools**: planning, memory, web search, code execution, image generation

## Advanced Features

- **Streaming**: Real-time progress updates and message streaming with callback handlers
- **File Attachments**: File paths and base64-encoded data within agent messages
- **Skills**: Reusable context blocks via inline content or external URLs
- **Async Support**: Full asynchronous API for parallel processing
- **Error Handling**: Custom exception types for missing requirements and runtime issues
- **Human Approval**: Integration into tool execution pipelines for sensitive operations

## References

- `references/agent-patterns.md` — Agent development patterns
- `references/async-patterns.md` — Async usage patterns
- `references/files.md` — File handling
- `references/sessions.md` — Session management
- `references/streaming.md` — Streaming patterns
- `references/tool-builder.md` — Tool builder API
