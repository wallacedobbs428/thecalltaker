# TCT Video Understanding MCP Server v2

Lets Claude **see and understand** any video — local files or URLs from YouTube, TikTok, Twitter/X, Instagram, etc.

Built for The Call Taker (AI Receptionist SaaS) to learn from video content across social media.

## Tools

| Tool | Description |
|------|-------------|
| `analyze-video` | Full pipeline: download + extract frames + transcribe + Claude vision analysis |
| `extract-frames` | Pull frames at intervals or timestamps (base64 images Claude can see) |
| `transcribe-audio` | Extract and transcribe audio via OpenAI Whisper |
| `get-video-info` | Duration, resolution, codec, fps, file size |
| `describe-scene` | Analyze a specific time range with Claude vision |
| `download-video` | Download from YouTube/TikTok/Twitter/Instagram/Vimeo |
| `get-knowledge-base` | View all learnings extracted from analyzed videos |

## Prerequisites

```bash
# ffmpeg (REQUIRED)
brew install ffmpeg          # macOS
sudo apt install ffmpeg      # Ubuntu

# yt-dlp (REQUIRED for URL downloads)
pip install yt-dlp

# Verify
ffmpeg -version && yt-dlp --version
```

## Environment Variables

```bash
# REQUIRED for AI vision analysis of frames
export ANTHROPIC_API_KEY="sk-ant-..."

# OPTIONAL for audio transcription (Whisper)
export TCT_OPENAI_API_KEY="sk-..."

# OPTIONAL custom work directory
export TCT_VIDEO_WORK_DIR="/tmp/tct-video-work"
```

## Install

```bash
cd mcp-video-understand
npm install
```

## Add to Claude Code

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "video-understand": {
      "command": "node",
      "args": ["/absolute/path/to/thecalltaker/mcp-video-understand/server.js"],
      "env": {
        "ANTHROPIC_API_KEY": "your-anthropic-key"
      }
    }
  }
}
```

## Usage Examples

```
# Analyze a YouTube video about Claude Code tips
analyze-video source="https://youtube.com/watch?v=..." context="Claude Code tips and tricks"

# Analyze a TikTok about sales techniques
analyze-video source="https://tiktok.com/@user/video/..." context="sales closing techniques"

# Analyze a local video
analyze-video source="/path/to/video.mp4"

# Just get the transcript
transcribe-audio source="https://youtube.com/watch?v=..."

# Look at a specific scene
describe-scene source="/path/to/video.mp4" startTime="00:01:30" endTime="00:02:00"

# Download for later
download-video url="https://tiktok.com/..."

# Review everything learned so far
get-knowledge-base
```

## Knowledge Base

Every analyzed video saves learnings to `/tmp/tct-video-work/knowledge/claude-tips.json`. Builds up over time — all tips, tools, configs, and code discovered from videos.

## How It Works

1. **URL?** Downloads via yt-dlp (720p max to keep files reasonable)
2. **ffmpeg** extracts frames at regular intervals (default: every 5s, max 15-20 frames)
3. **ffmpeg** extracts audio track → sends to OpenAI Whisper for transcription
4. **Anthropic Claude API** (vision) analyzes frames + transcript together
5. Returns frames as base64 images + transcript + AI analysis
6. Saves learnings to knowledge base

## Supported Platforms (via yt-dlp)

YouTube, TikTok, Twitter/X, Instagram, Vimeo, Facebook, Reddit, Twitch, and 1000+ more sites.

## Supported Video Formats

mp4, mov, avi, mkv, webm, flv, wmv, m4v, ts, mts, 3gp, ogv
