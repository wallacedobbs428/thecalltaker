#!/usr/bin/env node
/**
 * The Call Taker — Video Understanding MCP Server v2
 *
 * Lets Claude SEE and UNDERSTAND any video — local files or social media URLs.
 * Uses Anthropic Claude API for vision analysis + ffmpeg for frame/audio extraction.
 *
 * Tools:
 *   analyze-video      — Full analysis: frames + audio + scene descriptions
 *   extract-frames     — Pull frames at intervals or timestamps (base64 images)
 *   transcribe-audio   — Extract audio track, transcribe via Whisper or return path
 *   get-video-info     — Metadata: duration, resolution, codec, fps, size
 *   describe-scene     — Analyze a specific time range
 *   download-video     — Download video from URL (YouTube, TikTok, Twitter, etc.)
 *   get-knowledge-base — View all extracted learnings
 *
 * Config:
 *   ANTHROPIC_API_KEY       — For Claude vision analysis (REQUIRED for AI analysis)
 *   TCT_OPENAI_API_KEY      — For Whisper transcription (optional)
 *   TCT_VIDEO_WORK_DIR      — Temp dir (default: /tmp/tct-video-work)
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { execSync } from "child_process";
import {
  readFileSync,
  writeFileSync,
  mkdirSync,
  existsSync,
  readdirSync,
  unlinkSync,
} from "fs";
import { join, basename } from "path";
import { tmpdir } from "os";

// ---------- Config ----------

const WORK_DIR =
  process.env.TCT_VIDEO_WORK_DIR || join(tmpdir(), "tct-video-work");
const ANTHROPIC_KEY = process.env.ANTHROPIC_API_KEY;
const OPENAI_KEY = process.env.TCT_OPENAI_API_KEY;
const MAX_FRAMES = 20;
const FRAME_QUALITY = 85;

if (!existsSync(WORK_DIR)) mkdirSync(WORK_DIR, { recursive: true });

const KNOWLEDGE_DIR = join(WORK_DIR, "knowledge");
if (!existsSync(KNOWLEDGE_DIR)) mkdirSync(KNOWLEDGE_DIR, { recursive: true });

// ---------- Helpers ----------

function checkFfmpeg() {
  try {
    execSync("which ffmpeg", { stdio: "pipe" });
    execSync("which ffprobe", { stdio: "pipe" });
    return true;
  } catch {
    return false;
  }
}

function checkYtDlp() {
  try {
    execSync("which yt-dlp", { stdio: "pipe" });
    return true;
  } catch {
    return false;
  }
}

function getVideoInfo(filePath) {
  const cmd = `ffprobe -v quiet -print_format json -show_format -show_streams "${filePath}"`;
  const output = execSync(cmd, {
    encoding: "utf-8",
    maxBuffer: 10 * 1024 * 1024,
  });
  const data = JSON.parse(output);

  const videoStream = data.streams?.find((s) => s.codec_type === "video");
  const audioStream = data.streams?.find((s) => s.codec_type === "audio");
  const format = data.format || {};

  const fps = videoStream?.r_frame_rate
    ? (() => {
        const parts = videoStream.r_frame_rate.split("/");
        return parts.length === 2
          ? (parseInt(parts[0]) / parseInt(parts[1])).toFixed(2)
          : videoStream.r_frame_rate;
      })()
    : 0;

  return {
    duration: parseFloat(format.duration || 0),
    durationFormatted: fmtDur(parseFloat(format.duration || 0)),
    width: videoStream?.width || 0,
    height: videoStream?.height || 0,
    resolution: videoStream
      ? `${videoStream.width}x${videoStream.height}`
      : "unknown",
    codec: videoStream?.codec_name || "unknown",
    audioCodec: audioStream?.codec_name || "none",
    fps,
    bitrate: parseInt(format.bit_rate || 0),
    fileSize: parseInt(format.size || 0),
    fileSizeMB: (parseInt(format.size || 0) / 1048576).toFixed(2),
    format: format.format_name || "unknown",
    filePath,
  };
}

function fmtDur(s) {
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = Math.floor(s % 60);
  if (h > 0) return `${h}h ${m}m ${sec}s`;
  if (m > 0) return `${m}m ${sec}s`;
  return `${sec}s`;
}

function fmtTs(seconds) {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

function parseTime(t) {
  if (typeof t === "number") return t;
  if (!isNaN(t)) return parseFloat(t);
  const parts = String(t).split(":").map(Number);
  if (parts.length === 3) return parts[0] * 3600 + parts[1] * 60 + parts[2];
  if (parts.length === 2) return parts[0] * 60 + parts[1];
  return parseFloat(t) || 0;
}

function extractFrames(filePath, options = {}) {
  const {
    interval = 5,
    timestamps = null,
    maxFrames = MAX_FRAMES,
    quality = FRAME_QUALITY,
  } = options;

  const sessionDir = join(WORK_DIR, `frames-${Date.now()}`);
  mkdirSync(sessionDir, { recursive: true });

  const info = getVideoInfo(filePath);
  const frames = [];
  const q = Math.round((100 - quality) / 3.2);

  if (timestamps && timestamps.length > 0) {
    for (let i = 0; i < Math.min(timestamps.length, maxFrames); i++) {
      const ts = timestamps[i];
      const outFile = join(sessionDir, `frame-${i}.jpg`);
      try {
        execSync(
          `ffmpeg -y -ss ${ts} -i "${filePath}" -vframes 1 -q:v ${q} "${outFile}"`,
          { stdio: "pipe", timeout: 30000 }
        );
        if (existsSync(outFile)) {
          frames.push({
            timestamp: ts,
            index: i,
            base64: readFileSync(outFile).toString("base64"),
            mimeType: "image/jpeg",
          });
        }
      } catch {}
    }
  } else {
    const effectiveInterval = Math.max(interval, info.duration / maxFrames);
    let fc = 0;
    for (let t = 0; t < info.duration && fc < maxFrames; t += effectiveInterval) {
      const outFile = join(sessionDir, `frame-${fc}.jpg`);
      const ts = fmtTs(t);
      try {
        execSync(
          `ffmpeg -y -ss ${t} -i "${filePath}" -vframes 1 -q:v ${q} "${outFile}"`,
          { stdio: "pipe", timeout: 30000 }
        );
        if (existsSync(outFile)) {
          frames.push({
            timestamp: ts,
            secondsIn: Math.round(t),
            index: fc,
            base64: readFileSync(outFile).toString("base64"),
            mimeType: "image/jpeg",
          });
          fc++;
        }
      } catch {}
    }
  }

  // Cleanup
  try {
    readdirSync(sessionDir).forEach((f) => unlinkSync(join(sessionDir, f)));
  } catch {}

  return { frames, totalExtracted: frames.length, videoInfo: info };
}

function extractAudio(filePath) {
  const audioFile = join(WORK_DIR, `audio-${Date.now()}.wav`);
  try {
    execSync(
      `ffmpeg -y -i "${filePath}" -vn -acodec pcm_s16le -ar 16000 -ac 1 "${audioFile}"`,
      { stdio: "pipe", timeout: 120000 }
    );
    return audioFile;
  } catch {
    return null;
  }
}

async function transcribeWithWhisper(audioPath) {
  if (!OPENAI_KEY) return null;

  const audioData = readFileSync(audioPath);
  const blob = new Blob([audioData], { type: "audio/wav" });

  const formData = new FormData();
  formData.append("file", blob, "audio.wav");
  formData.append("model", "whisper-1");
  formData.append("response_format", "verbose_json");
  formData.append("timestamp_granularities[]", "segment");

  try {
    const res = await fetch("https://api.openai.com/v1/audio/transcriptions", {
      method: "POST",
      headers: { Authorization: `Bearer ${OPENAI_KEY}` },
      body: formData,
    });
    if (!res.ok) {
      return { error: `Whisper API ${res.status}: ${await res.text()}` };
    }
    const data = await res.json();
    return {
      text: data.text,
      segments: data.segments?.map((s) => ({
        start: s.start,
        end: s.end,
        text: s.text,
      })),
      language: data.language,
      duration: data.duration,
    };
  } catch (e) {
    return { error: e.message };
  }
}

async function analyzeFramesWithClaude(frames, context = "") {
  if (!ANTHROPIC_KEY) return null;

  const content = [];
  if (context) content.push({ type: "text", text: context });

  for (const frame of frames.slice(0, 10)) {
    content.push({
      type: "text",
      text: `\n--- Frame at ${frame.timestamp} (${frame.secondsIn || 0}s in) ---`,
    });
    content.push({
      type: "image",
      source: {
        type: "base64",
        media_type: "image/jpeg",
        data: frame.base64,
      },
    });
  }

  content.push({
    type: "text",
    text: "\nDescribe what you see in each frame. Note any: text on screen, UI elements, code, terminal commands, tools being demonstrated, key concepts being taught, and actionable tips. Be specific and detailed.",
  });

  try {
    const res = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "x-api-key": ANTHROPIC_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
      },
      body: JSON.stringify({
        model: "claude-sonnet-4-20250514",
        max_tokens: 4096,
        messages: [{ role: "user", content }],
      }),
    });

    if (!res.ok) {
      return { error: `Claude API ${res.status}: ${await res.text()}` };
    }

    const data = await res.json();
    return {
      analysis: data.content?.[0]?.text || "No analysis returned",
      model: data.model,
      inputTokens: data.usage?.input_tokens,
      outputTokens: data.usage?.output_tokens,
    };
  } catch (e) {
    return { error: e.message };
  }
}

function dlVideo(url) {
  if (!checkYtDlp()) {
    return { error: "yt-dlp not installed. Install: pip install yt-dlp" };
  }
  const outFile = join(WORK_DIR, `download-${Date.now()}.mp4`);
  try {
    execSync(
      `yt-dlp -f "bestvideo[height<=720]+bestaudio/best[height<=720]/best" --merge-output-format mp4 -o "${outFile}" "${url}"`,
      { stdio: "pipe", timeout: 300000, maxBuffer: 50 * 1024 * 1024 }
    );
    if (existsSync(outFile)) return { filePath: outFile, success: true };
  } catch {
    try {
      execSync(`yt-dlp -f "best" -o "${outFile}" "${url}"`, {
        stdio: "pipe",
        timeout: 300000,
        maxBuffer: 50 * 1024 * 1024,
      });
      if (existsSync(outFile)) return { filePath: outFile, success: true };
    } catch {}
  }
  return { error: "Download failed" };
}

async function resolveSource(source) {
  if (!source) return { error: "No source provided" };
  if (source.startsWith("http://") || source.startsWith("https://")) {
    const result = dlVideo(source);
    if (result.error) return result;
    return {
      filePath: result.filePath,
      wasDownloaded: true,
      originalUrl: source,
    };
  }
  if (!existsSync(source)) return { error: `File not found: ${source}` };
  return { filePath: source, wasDownloaded: false };
}

function saveKnowledge(title, source, learnings) {
  const knowledgeFile = join(KNOWLEDGE_DIR, "claude-tips.json");
  let existing = [];
  if (existsSync(knowledgeFile)) {
    try {
      existing = JSON.parse(readFileSync(knowledgeFile, "utf-8"));
    } catch {}
  }
  existing.push({
    title,
    source,
    learnings,
    extractedAt: new Date().toISOString(),
  });
  writeFileSync(knowledgeFile, JSON.stringify(existing, null, 2));
  return existing.length;
}

// ---------- MCP Server ----------

const server = new Server(
  { name: "tct-video-understand", version: "2.0.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "analyze-video",
      description:
        "Full video analysis: extracts key frames, transcribes audio, uses Claude vision to describe each scene. Accepts file paths or URLs (YouTube, TikTok, Twitter, Instagram, etc).",
      inputSchema: {
        type: "object",
        properties: {
          source: {
            type: "string",
            description:
              "File path OR URL (YouTube, TikTok, Twitter/X, Instagram, Vimeo, etc.)",
          },
          frameInterval: {
            type: "number",
            description:
              "Seconds between frame extractions (default: 5, lower = more detail)",
            default: 5,
          },
          maxFrames: {
            type: "number",
            description: "Max frames to extract (default: 15)",
            default: 15,
          },
          context: {
            type: "string",
            description:
              "What to focus on — e.g. 'Claude Code tips', 'MCP server setup', 'sales techniques'",
          },
          saveKnowledge: {
            type: "boolean",
            description: "Save extracted learnings to knowledge base (default: true)",
            default: true,
          },
        },
        required: ["source"],
      },
    },
    {
      name: "extract-frames",
      description:
        "Extract frames from a video at intervals or specific timestamps. Returns base64 images Claude can see.",
      inputSchema: {
        type: "object",
        properties: {
          source: { type: "string", description: "File path or URL" },
          interval: {
            type: "number",
            description: "Seconds between frames (default: 5)",
            default: 5,
          },
          timestamps: {
            type: "array",
            items: { type: "string" },
            description: "Specific timestamps like ['00:00:10', '00:01:30']",
          },
          maxFrames: {
            type: "number",
            description: "Max frames (default: 20)",
            default: 20,
          },
        },
        required: ["source"],
      },
    },
    {
      name: "transcribe-audio",
      description:
        "Extract and transcribe audio from a video. Uses OpenAI Whisper if TCT_OPENAI_API_KEY is set.",
      inputSchema: {
        type: "object",
        properties: {
          source: { type: "string", description: "File path or URL" },
        },
        required: ["source"],
      },
    },
    {
      name: "get-video-info",
      description: "Get video metadata: duration, resolution, codec, fps, file size.",
      inputSchema: {
        type: "object",
        properties: {
          source: { type: "string", description: "File path or URL" },
        },
        required: ["source"],
      },
    },
    {
      name: "describe-scene",
      description:
        "Analyze a specific time range in a video using Claude vision.",
      inputSchema: {
        type: "object",
        properties: {
          source: { type: "string", description: "File path or URL" },
          startTime: {
            type: "string",
            description: "Start timestamp (e.g. '00:01:30' or '90')",
          },
          endTime: {
            type: "string",
            description: "End timestamp (e.g. '00:02:00' or '120')",
          },
          context: {
            type: "string",
            description: "What to focus on in the scene",
          },
        },
        required: ["source", "startTime", "endTime"],
      },
    },
    {
      name: "download-video",
      description:
        "Download a video from any URL (YouTube, TikTok, Twitter/X, Instagram, Vimeo, etc). Returns local file path.",
      inputSchema: {
        type: "object",
        properties: {
          url: { type: "string", description: "Video URL" },
        },
        required: ["url"],
      },
    },
    {
      name: "get-knowledge-base",
      description:
        "View all learnings extracted from analyzed videos. Tips, tools, configs, and actionable insights.",
      inputSchema: { type: "object", properties: {} },
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (!checkFfmpeg() && name !== "get-knowledge-base") {
    return {
      content: [
        {
          type: "text",
          text: "ERROR: ffmpeg/ffprobe not found.\n  macOS: brew install ffmpeg\n  Ubuntu: sudo apt install ffmpeg",
        },
      ],
    };
  }

  switch (name) {
    // ============================================================
    // ANALYZE VIDEO — full pipeline
    // ============================================================
    case "analyze-video": {
      const resolved = await resolveSource(args.source);
      if (resolved.error)
        return { content: [{ type: "text", text: `Error: ${resolved.error}` }] };

      const filePath = resolved.filePath;
      const interval = args.frameInterval || 5;
      const maxFrames = args.maxFrames || 15;
      const context = args.context || "";

      let info;
      try {
        info = getVideoInfo(filePath);
      } catch (e) {
        return {
          content: [{ type: "text", text: `Error reading video: ${e.message}` }],
        };
      }

      // Extract frames
      const { frames } = extractFrames(filePath, { interval, maxFrames });

      // Transcribe
      let transcript = null;
      const audioPath = extractAudio(filePath);
      if (audioPath && OPENAI_KEY) {
        transcript = await transcribeWithWhisper(audioPath);
        try { unlinkSync(audioPath); } catch {}
      } else if (audioPath) {
        try { unlinkSync(audioPath); } catch {}
      }

      // Claude vision
      let visionAnalysis = null;
      if (ANTHROPIC_KEY && frames.length > 0) {
        const focusCtx = context
          ? `Analyzing video about: ${context}\nExtract actionable tips, tools, configs, code, and anything useful for "The Call Taker" (AI receptionist SaaS business).\n`
          : "Analyze this video. Note all text, code, UI, tools, and concepts shown.\n";
        const fullCtx =
          focusCtx +
          (transcript?.text ? `\nTranscript: "${transcript.text}"\n` : "") +
          `\nVideo: ${info.durationFormatted}, ${info.resolution}\n`;
        visionAnalysis = await analyzeFramesWithClaude(frames, fullCtx);
      }

      // Build response
      const rc = [];

      rc.push({
        type: "text",
        text: [
          `## Video Analysis Complete`,
          `**Source:** ${resolved.originalUrl || filePath}`,
          `**Duration:** ${info.durationFormatted}`,
          `**Resolution:** ${info.resolution}`,
          `**Frames:** ${frames.length}`,
          `**Transcript:** ${transcript?.text ? "Yes" : "No (set TCT_OPENAI_API_KEY)"}`,
          `**Vision AI:** ${visionAnalysis?.analysis ? "Yes" : "No (set ANTHROPIC_API_KEY)"}`,
        ].join("\n"),
      });

      // Frames as images
      for (const frame of frames) {
        rc.push({
          type: "text",
          text: `\n### Frame at ${frame.timestamp} (${frame.secondsIn || 0}s)`,
        });
        rc.push({
          type: "image",
          data: frame.base64,
          mimeType: "image/jpeg",
        });
      }

      if (transcript?.text) {
        rc.push({ type: "text", text: `\n## Transcript\n${transcript.text}` });
        if (transcript.segments) {
          rc.push({
            type: "text",
            text:
              `\n## Timestamped Segments\n` +
              transcript.segments
                .map((s) => `[${fmtTs(s.start)}] ${s.text}`)
                .join("\n"),
          });
        }
      }

      if (visionAnalysis?.analysis) {
        rc.push({
          type: "text",
          text: `\n## AI Analysis\n${visionAnalysis.analysis}`,
        });
      }

      if (args.saveKnowledge !== false) {
        const title = resolved.originalUrl || basename(filePath);
        const learnings =
          visionAnalysis?.analysis ||
          transcript?.text ||
          "Frames extracted — manual review needed";
        const total = saveKnowledge(title, args.source, learnings);
        rc.push({
          type: "text",
          text: `\n---\nSaved to knowledge base (${total} total entries).`,
        });
      }

      if (resolved.wasDownloaded) {
        try { unlinkSync(filePath); } catch {}
      }

      return { content: rc };
    }

    // ============================================================
    // EXTRACT FRAMES
    // ============================================================
    case "extract-frames": {
      const resolved = await resolveSource(args.source);
      if (resolved.error)
        return { content: [{ type: "text", text: `Error: ${resolved.error}` }] };

      const { frames, totalExtracted, videoInfo } = extractFrames(
        resolved.filePath,
        {
          interval: args.interval || 5,
          timestamps: args.timestamps,
          maxFrames: args.maxFrames || 20,
        }
      );

      const rc = [
        {
          type: "text",
          text: `Extracted ${totalExtracted} frames from ${videoInfo.durationFormatted} video (${videoInfo.resolution})`,
        },
      ];

      for (const frame of frames) {
        rc.push({ type: "text", text: `\n--- ${frame.timestamp} ---` });
        rc.push({ type: "image", data: frame.base64, mimeType: "image/jpeg" });
      }

      if (resolved.wasDownloaded) {
        try { unlinkSync(resolved.filePath); } catch {}
      }
      return { content: rc };
    }

    // ============================================================
    // TRANSCRIBE AUDIO
    // ============================================================
    case "transcribe-audio": {
      const resolved = await resolveSource(args.source);
      if (resolved.error)
        return { content: [{ type: "text", text: `Error: ${resolved.error}` }] };

      const audioPath = extractAudio(resolved.filePath);
      if (!audioPath)
        return {
          content: [{ type: "text", text: "Failed to extract audio" }],
        };

      if (OPENAI_KEY) {
        const transcript = await transcribeWithWhisper(audioPath);
        try { unlinkSync(audioPath); } catch {}
        if (resolved.wasDownloaded) {
          try { unlinkSync(resolved.filePath); } catch {}
        }
        if (transcript?.error)
          return {
            content: [
              { type: "text", text: `Transcription error: ${transcript.error}` },
            ],
          };

        const rc = [
          { type: "text", text: `## Transcript\n\n${transcript.text}` },
        ];
        if (transcript.segments) {
          rc.push({
            type: "text",
            text:
              `\n## Timestamped\n` +
              transcript.segments
                .map((s) => `[${fmtTs(s.start)}] ${s.text}`)
                .join("\n"),
          });
        }
        return { content: rc };
      }

      if (resolved.wasDownloaded) {
        try { unlinkSync(resolved.filePath); } catch {}
      }
      return {
        content: [
          {
            type: "text",
            text: `Audio extracted: ${audioPath}\n\nSet TCT_OPENAI_API_KEY for auto-transcription.`,
          },
        ],
      };
    }

    // ============================================================
    // GET VIDEO INFO
    // ============================================================
    case "get-video-info": {
      const resolved = await resolveSource(args.source);
      if (resolved.error)
        return { content: [{ type: "text", text: `Error: ${resolved.error}` }] };
      try {
        const info = getVideoInfo(resolved.filePath);
        if (resolved.wasDownloaded) {
          try { unlinkSync(resolved.filePath); } catch {}
        }
        return {
          content: [{ type: "text", text: JSON.stringify(info, null, 2) }],
        };
      } catch (e) {
        return { content: [{ type: "text", text: `Error: ${e.message}` }] };
      }
    }

    // ============================================================
    // DESCRIBE SCENE
    // ============================================================
    case "describe-scene": {
      const resolved = await resolveSource(args.source);
      if (resolved.error)
        return { content: [{ type: "text", text: `Error: ${resolved.error}` }] };

      const start = parseTime(args.startTime);
      const end = parseTime(args.endTime);
      const dur = end - start;

      const timestamps = [];
      const step = Math.max(1, dur / 8);
      for (let t = start; t <= end && timestamps.length < 10; t += step) {
        timestamps.push(fmtTs(t));
      }

      const { frames } = extractFrames(resolved.filePath, { timestamps });

      const rc = [
        {
          type: "text",
          text: `## Scene: ${args.startTime} → ${args.endTime} (${Math.round(dur)}s)`,
        },
      ];

      for (const frame of frames) {
        rc.push({ type: "text", text: `\n--- ${frame.timestamp} ---` });
        rc.push({ type: "image", data: frame.base64, mimeType: "image/jpeg" });
      }

      if (ANTHROPIC_KEY && frames.length > 0) {
        const ctx = args.context
          ? `Scene ${args.startTime}→${args.endTime}. Focus: ${args.context}`
          : `Scene ${args.startTime}→${args.endTime}. Describe in detail.`;
        const analysis = await analyzeFramesWithClaude(frames, ctx);
        if (analysis?.analysis) {
          rc.push({
            type: "text",
            text: `\n## Scene Analysis\n${analysis.analysis}`,
          });
        }
      }

      if (resolved.wasDownloaded) {
        try { unlinkSync(resolved.filePath); } catch {}
      }
      return { content: rc };
    }

    // ============================================================
    // DOWNLOAD VIDEO
    // ============================================================
    case "download-video": {
      const result = dlVideo(args.url);
      if (result.error)
        return {
          content: [{ type: "text", text: `Download error: ${result.error}` }],
        };
      const info = getVideoInfo(result.filePath);
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                success: true,
                filePath: result.filePath,
                duration: info.durationFormatted,
                resolution: info.resolution,
                fileSize: `${info.fileSizeMB} MB`,
                note: "Use analyze-video with this file path for full analysis.",
              },
              null,
              2
            ),
          },
        ],
      };
    }

    // ============================================================
    // KNOWLEDGE BASE
    // ============================================================
    case "get-knowledge-base": {
      const kf = join(KNOWLEDGE_DIR, "claude-tips.json");
      if (!existsSync(kf)) {
        return {
          content: [
            {
              type: "text",
              text: "Knowledge base empty. Analyze videos first with analyze-video.",
            },
          ],
        };
      }
      try {
        const entries = JSON.parse(readFileSync(kf, "utf-8"));
        const summary = entries
          .map(
            (e, i) =>
              `### ${i + 1}. ${e.title}\n**Source:** ${e.source}\n**Date:** ${e.extractedAt}\n\n${e.learnings.slice(0, 1000)}${e.learnings.length > 1000 ? "..." : ""}`
          )
          .join("\n\n---\n\n");
        return {
          content: [
            {
              type: "text",
              text: `## Knowledge Base — ${entries.length} entries\n\n${summary}`,
            },
          ],
        };
      } catch (e) {
        return { content: [{ type: "text", text: `Error: ${e.message}` }] };
      }
    }

    default:
      return { content: [{ type: "text", text: `Unknown tool: ${name}` }] };
  }
});

// ---------- Start ----------
const transport = new StdioServerTransport();
await server.connect(transport);
