#!/usr/bin/env node
/**
 * The Call Taker — Video Ad Production MCP Server
 *
 * Tools:
 *   generate-video   — Submit a script to AI video generation (Runway/Kling/HeyGen)
 *   check-status     — Poll generation status
 *   list-videos      — List all generated videos
 *   add-captions     — Add word-by-word captions to a video
 *   export-formats   — Export video in multiple aspect ratios (9:16, 1:1, 16:9)
 *   generate-thumbnail — Generate a scroll-stopping thumbnail
 *
 * Config via env vars:
 *   TCT_RUNWAY_API_KEY    — Runway Gen-3/Gen-4 API key
 *   TCT_KLING_API_KEY     — Kling AI API key
 *   TCT_HEYGEN_API_KEY    — HeyGen API key (for spokesperson videos)
 *   TCT_ELEVENLABS_KEY    — ElevenLabs API key (for voiceover + captions)
 *   TCT_VIDEO_OUTPUT_DIR  — Output directory (default: ../videos from this package)
 *   TCT_VIDEO_SCRIPTS_DIR — Script directory (default: ../scripts from this package)
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { readFileSync, writeFileSync, readdirSync, mkdirSync, existsSync } from "fs";
import { dirname, join } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ADS_DIR = dirname(__dirname);

const OUTPUT_DIR =
  process.env.TCT_VIDEO_OUTPUT_DIR ||
  join(ADS_DIR, "videos");

// Ensure output dir exists
if (!existsSync(OUTPUT_DIR)) {
  mkdirSync(OUTPUT_DIR, { recursive: true });
}

// State file for tracking generations
const STATE_FILE = join(OUTPUT_DIR, ".generation-state.json");

function loadState() {
  if (existsSync(STATE_FILE)) {
    return JSON.parse(readFileSync(STATE_FILE, "utf-8"));
  }
  return { generations: [] };
}

function saveState(state) {
  writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
}

// ---------- Provider Adapters ----------

const providers = {
  runway: {
    name: "Runway",
    async generate(prompt, options) {
      const key = process.env.TCT_RUNWAY_API_KEY;
      if (!key) return { error: "TCT_RUNWAY_API_KEY not set" };

      const res = await fetch("https://api.dev.runwayml.com/v1/image_to_video", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${key}`,
          "Content-Type": "application/json",
          "X-Runway-Version": "2024-11-06",
        },
        body: JSON.stringify({
          model: "gen3a_turbo",
          promptText: prompt,
          duration: options.duration || 10,
          ratio: options.ratio || "9:16",
          watermark: false,
        }),
      });

      if (!res.ok) {
        const err = await res.text();
        return { error: `Runway API error ${res.status}: ${err}` };
      }

      const data = await res.json();
      return {
        id: data.id,
        provider: "runway",
        status: "pending",
        estimatedSeconds: 120,
      };
    },

    async checkStatus(id) {
      const key = process.env.TCT_RUNWAY_API_KEY;
      const res = await fetch(`https://api.dev.runwayml.com/v1/tasks/${id}`, {
        headers: {
          Authorization: `Bearer ${key}`,
          "X-Runway-Version": "2024-11-06",
        },
      });
      const data = await res.json();
      return {
        status: data.status, // PENDING, RUNNING, SUCCEEDED, FAILED
        output: data.output?.[0] || null,
        progress: data.progress || 0,
      };
    },
  },

  kling: {
    name: "Kling AI",
    async generate(prompt, options) {
      const key = process.env.TCT_KLING_API_KEY;
      if (!key) return { error: "TCT_KLING_API_KEY not set" };

      const res = await fetch(
        "https://api.klingai.com/v1/videos/text2video",
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${key}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            model_name: "kling-v2-master",
            prompt: prompt,
            negative_prompt: "blurry, distorted, low quality, watermark",
            duration: String(options.duration || 10),
            aspect_ratio: options.ratio || "9:16",
            mode: "high_quality",
          }),
        }
      );

      if (!res.ok) {
        const err = await res.text();
        return { error: `Kling API error ${res.status}: ${err}` };
      }

      const data = await res.json();
      return {
        id: data.data?.task_id,
        provider: "kling",
        status: "pending",
        estimatedSeconds: 180,
      };
    },

    async checkStatus(id) {
      const key = process.env.TCT_KLING_API_KEY;
      const res = await fetch(
        `https://api.klingai.com/v1/videos/text2video/${id}`,
        {
          headers: { Authorization: `Bearer ${key}` },
        }
      );
      const data = await res.json();
      const task = data.data;
      return {
        status: task?.task_status || "unknown",
        output: task?.task_result?.videos?.[0]?.url || null,
        progress: task?.task_status_msg || "",
      };
    },
  },

  heygen: {
    name: "HeyGen",
    async generate(prompt, options) {
      const key = process.env.TCT_HEYGEN_API_KEY;
      if (!key) return { error: "TCT_HEYGEN_API_KEY not set" };

      // HeyGen uses avatar-based video generation
      const res = await fetch("https://api.heygen.com/v2/video/generate", {
        method: "POST",
        headers: {
          "X-Api-Key": key,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          video_inputs: [
            {
              character: {
                type: "avatar",
                avatar_id: options.avatarId || "default",
                avatar_style: "normal",
              },
              voice: {
                type: "text",
                input_text: prompt,
                voice_id: options.voiceId || "en-US-JennyNeural",
              },
              background: {
                type: "color",
                value: "#0a0a0a",
              },
            },
          ],
          dimension: {
            width: options.ratio === "9:16" ? 1080 : 1080,
            height: options.ratio === "9:16" ? 1920 : 1080,
          },
        }),
      });

      if (!res.ok) {
        const err = await res.text();
        return { error: `HeyGen API error ${res.status}: ${err}` };
      }

      const data = await res.json();
      return {
        id: data.data?.video_id,
        provider: "heygen",
        status: "pending",
        estimatedSeconds: 300,
      };
    },

    async checkStatus(id) {
      const key = process.env.TCT_HEYGEN_API_KEY;
      const res = await fetch(
        `https://api.heygen.com/v1/video_status.get?video_id=${id}`,
        {
          headers: { "X-Api-Key": key },
        }
      );
      const data = await res.json();
      return {
        status: data.data?.status || "unknown",
        output: data.data?.video_url || null,
        progress: data.data?.status || "",
      };
    },
  },
};

// ---------- Script Loader ----------

const SCRIPTS_DIR =
  process.env.TCT_VIDEO_SCRIPTS_DIR || join(ADS_DIR, "scripts");

function loadScript(scriptNum) {
  const files = readdirSync(SCRIPTS_DIR).filter((f) =>
    f.startsWith(`script-0${scriptNum}`)
  );
  if (files.length === 0) return null;
  return readFileSync(join(SCRIPTS_DIR, files[0]), "utf-8");
}

function buildVideoPrompt(script, vertical, section) {
  // Extract the visual direction from a script for a specific section
  const sectionMap = {
    hook: "SECOND 0-3",
    pain: "SECOND 3-8",
    solution: "SECOND 8-15",
    proof: "SECOND 15-20",
    offer: "SECOND 20-2",
    cta: "SECOND 2[5-9]-30",
  };

  const pattern = sectionMap[section] || "SECOND 0-3";
  const regex = new RegExp(`### ${pattern}[\\s\\S]*?(?=###|---|\n## )`, "i");
  const match = script.match(regex);

  let visualDescription = match
    ? match[0]
        .replace(/###.*\n/, "")
        .replace(/- \*\*Text overlay.*?\n/g, "")
        .replace(/- \*\*Audio.*?\n/g, "")
        .replace(/- \*\*Music.*?\n/g, "")
        .replace(/- \*\*Visual:\*\*/g, "")
        .trim()
    : `Professional video ad for ${vertical} business, cinematic quality`;

  return visualDescription;
}

// ---------- MCP Server ----------

const server = new Server(
  { name: "tct-video-ads", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "generate-video",
      description:
        "Generate a video ad clip from a script. Sends the visual prompt to an AI video provider.",
      inputSchema: {
        type: "object",
        properties: {
          script: {
            type: "number",
            description: "Script number (1-5)",
            enum: [1, 2, 3, 4, 5],
          },
          vertical: {
            type: "string",
            description:
              "Industry vertical (roofing, hvac, plumbing, dental, locksmith, towing, universal)",
          },
          section: {
            type: "string",
            description: "Which section to generate",
            enum: ["hook", "pain", "solution", "proof", "offer", "cta", "full"],
          },
          provider: {
            type: "string",
            description: "AI video provider",
            enum: ["runway", "kling", "heygen"],
            default: "kling",
          },
          ratio: {
            type: "string",
            description: "Aspect ratio",
            enum: ["9:16", "1:1", "16:9"],
            default: "9:16",
          },
          duration: {
            type: "number",
            description: "Duration in seconds (5 or 10)",
            enum: [5, 10],
            default: 10,
          },
        },
        required: ["script", "vertical"],
      },
    },
    {
      name: "check-status",
      description: "Check the status of a video generation job",
      inputSchema: {
        type: "object",
        properties: {
          generationId: {
            type: "string",
            description: "The generation ID returned by generate-video",
          },
        },
        required: ["generationId"],
      },
    },
    {
      name: "list-videos",
      description: "List all generated videos and their status",
      inputSchema: { type: "object", properties: {} },
    },
    {
      name: "add-captions",
      description:
        "Generate caption data (SRT/VTT) for a video using the script's voiceover text. Returns timed caption file.",
      inputSchema: {
        type: "object",
        properties: {
          script: { type: "number", description: "Script number (1-5)" },
          format: {
            type: "string",
            enum: ["srt", "vtt"],
            default: "vtt",
          },
        },
        required: ["script"],
      },
    },
    {
      name: "export-formats",
      description:
        "Create export manifest for a video: file names, specs, and ffmpeg commands for all aspect ratios.",
      inputSchema: {
        type: "object",
        properties: {
          script: { type: "number", description: "Script number (1-5)" },
          vertical: { type: "string", description: "Industry vertical" },
          version: { type: "number", default: 1 },
        },
        required: ["script", "vertical"],
      },
    },
    {
      name: "generate-thumbnail",
      description:
        "Return the thumbnail concept and specs for a given script, ready for Canva/Figma creation.",
      inputSchema: {
        type: "object",
        properties: {
          script: { type: "number", description: "Script number (1-5)" },
        },
        required: ["script"],
      },
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  switch (name) {
    case "generate-video": {
      const scriptContent = loadScript(args.script);
      if (!scriptContent) {
        return {
          content: [
            {
              type: "text",
              text: `Script ${args.script} not found in ${SCRIPTS_DIR}`,
            },
          ],
        };
      }

      const section = args.section || "hook";
      const provider = args.provider || "kling";
      const prompt = buildVideoPrompt(
        scriptContent,
        args.vertical,
        section
      );

      if (!providers[provider]) {
        return {
          content: [
            { type: "text", text: `Unknown provider: ${provider}` },
          ],
        };
      }

      const result = await providers[provider].generate(prompt, {
        ratio: args.ratio || "9:16",
        duration: args.duration || 10,
      });

      if (result.error) {
        return { content: [{ type: "text", text: `Error: ${result.error}` }] };
      }

      // Save to state
      const state = loadState();
      const gen = {
        ...result,
        script: args.script,
        vertical: args.vertical,
        section,
        prompt,
        createdAt: new Date().toISOString(),
        filename: `tct-${args.vertical}-script${args.script}-${section}-v1-${args.ratio.replace(":", "x")}-${new Date().toISOString().slice(0, 10)}.mp4`,
      };
      state.generations.push(gen);
      saveState(state);

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                message: `Video generation submitted to ${providers[provider].name}`,
                generationId: result.id,
                provider: provider,
                estimatedWait: `${result.estimatedSeconds}s`,
                filename: gen.filename,
                section: section,
                prompt: prompt.slice(0, 200) + "...",
              },
              null,
              2
            ),
          },
        ],
      };
    }

    case "check-status": {
      const state = loadState();
      const gen = state.generations.find(
        (g) => g.id === args.generationId
      );
      if (!gen) {
        return {
          content: [
            { type: "text", text: `Generation ${args.generationId} not found` },
          ],
        };
      }

      const provider = providers[gen.provider];
      const status = await provider.checkStatus(gen.id);

      // Update state
      gen.status = status.status;
      if (status.output) gen.outputUrl = status.output;
      saveState(state);

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                generationId: gen.id,
                provider: gen.provider,
                status: status.status,
                progress: status.progress,
                outputUrl: status.output,
                filename: gen.filename,
              },
              null,
              2
            ),
          },
        ],
      };
    }

    case "list-videos": {
      const state = loadState();

      // Also list any completed videos in the output dir
      const files = readdirSync(OUTPUT_DIR).filter((f) =>
        f.endsWith(".mp4")
      );

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                outputDir: OUTPUT_DIR,
                pendingGenerations: state.generations.filter(
                  (g) => g.status === "pending" || g.status === "RUNNING"
                ).length,
                completedGenerations: state.generations.filter(
                  (g) =>
                    g.status === "SUCCEEDED" || g.status === "succeed"
                ).length,
                localFiles: files,
                generations: state.generations.map((g) => ({
                  id: g.id,
                  script: g.script,
                  vertical: g.vertical,
                  section: g.section,
                  provider: g.provider,
                  status: g.status,
                  filename: g.filename,
                  createdAt: g.createdAt,
                })),
              },
              null,
              2
            ),
          },
        ],
      };
    }

    case "add-captions": {
      const scriptContent = loadScript(args.script);
      if (!scriptContent) {
        return {
          content: [
            { type: "text", text: `Script ${args.script} not found` },
          ],
        };
      }

      // Extract VO script section
      const voMatch = scriptContent.match(
        /## VOICEOVER SCRIPT[\s\S]*?```([\s\S]*?)```/
      );
      if (!voMatch) {
        return {
          content: [
            {
              type: "text",
              text: "Could not extract voiceover from script",
            },
          ],
        };
      }

      const voLines = voMatch[1]
        .split("\n")
        .filter((l) => l.trim() && !l.startsWith(">"));

      // Parse timing cues like [0-3], [3-8], etc.
      const cues = [];
      let currentStart = 0;
      let currentEnd = 0;

      for (const line of voLines) {
        const timeMatch = line.match(/\[(\d+)-(\d+)\]/);
        if (timeMatch) {
          currentStart = parseInt(timeMatch[1]);
          currentEnd = parseInt(timeMatch[2]);
          continue;
        }

        const text = line
          .replace(/^\s*"/, "")
          .replace(/"\s*$/, "")
          .trim();
        if (!text || text.startsWith("(")) continue;

        const duration = currentEnd - currentStart;
        const words = text.split(/\s+/);
        const msPerWord = (duration * 1000) / words.length;

        let wordStart = currentStart * 1000;
        for (const word of words) {
          const wordEnd = wordStart + msPerWord;
          cues.push({
            start: wordStart,
            end: wordEnd,
            text: word,
          });
          wordStart = wordEnd;
        }
      }

      // Generate VTT or SRT
      const format = args.format || "vtt";
      let output = "";

      if (format === "vtt") {
        output = "WEBVTT\n\n";
        cues.forEach((cue, i) => {
          const startTime = formatTime(cue.start, "vtt");
          const endTime = formatTime(cue.end, "vtt");
          output += `${i + 1}\n${startTime} --> ${endTime}\n${cue.text}\n\n`;
        });
      } else {
        cues.forEach((cue, i) => {
          const startTime = formatTime(cue.start, "srt");
          const endTime = formatTime(cue.end, "srt");
          output += `${i + 1}\n${startTime} --> ${endTime}\n${cue.text}\n\n`;
        });
      }

      const captionFile = join(
        OUTPUT_DIR,
        `script-${args.script}-captions.${format}`
      );
      writeFileSync(captionFile, output);

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                message: `Caption file generated`,
                file: captionFile,
                format: format,
                totalCues: cues.length,
                duration: `${Math.round(cues[cues.length - 1]?.end / 1000 || 0)}s`,
              },
              null,
              2
            ),
          },
        ],
      };
    }

    case "export-formats": {
      const date = new Date().toISOString().slice(0, 10);
      const v = args.version || 1;
      const base = `tct-${args.vertical}-script${args.script}`;

      const exports = [
        {
          format: "reels",
          ratio: "9:16",
          resolution: "1080x1920",
          filename: `${base}-v${v}-reels-${date}.mp4`,
          ffmpeg: `ffmpeg -i input.mp4 -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black" -c:v libx264 -b:v 12M -c:a aac -b:a 128k -r 30 "${base}-v${v}-reels-${date}.mp4"`,
        },
        {
          format: "feed",
          ratio: "1:1",
          resolution: "1080x1080",
          filename: `${base}-v${v}-feed-${date}.mp4`,
          ffmpeg: `ffmpeg -i input.mp4 -vf "scale=1080:1080:force_original_aspect_ratio=decrease,pad=1080:1080:(ow-iw)/2:(oh-ih)/2:black" -c:v libx264 -b:v 10M -c:a aac -b:a 128k -r 30 "${base}-v${v}-feed-${date}.mp4"`,
        },
        {
          format: "landscape",
          ratio: "16:9",
          resolution: "1920x1080",
          filename: `${base}-v${v}-landscape-${date}.mp4`,
          ffmpeg: `ffmpeg -i input.mp4 -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black" -c:v libx264 -b:v 15M -c:a aac -b:a 128k -r 30 "${base}-v${v}-landscape-${date}.mp4"`,
        },
      ];

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                outputDir: OUTPUT_DIR,
                exports: exports,
                captionOverlay: `ffmpeg -i input.mp4 -vf "subtitles=script-${args.script}-captions.vtt:force_style='FontName=Inter,FontSize=22,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,Bold=1'" output.mp4`,
                note: "Run ffmpeg commands in the output directory. Add -vf subtitles filter for burned-in captions.",
              },
              null,
              2
            ),
          },
        ],
      };
    }

    case "generate-thumbnail": {
      const scriptContent = loadScript(args.script);
      if (!scriptContent) {
        return {
          content: [
            { type: "text", text: `Script ${args.script} not found` },
          ],
        };
      }

      // Extract thumbnail section
      const thumbMatch = scriptContent.match(
        /## THUMBNAIL CONCEPT[\s\S]*?(?=---|\n## )/
      );
      const concept = thumbMatch
        ? thumbMatch[0].replace("## THUMBNAIL CONCEPT\n", "").trim()
        : "No thumbnail concept found in script";

      const specs = {
        dimensions: { reels: "1080x1920", feed: "1080x1080" },
        textStyle: {
          hookFont: "Inter Black",
          hookSize: "80-96px",
          hookColor: "#ffffff",
          statFont: "Inter ExtraBold",
          statSize: "72px",
          painColor: "#ef4444",
          gainColor: "#00dc82",
          shadow: "2px 2px 8px rgba(0,0,0,0.8)",
        },
        rules: [
          "Max 5 words of text",
          "High contrast: dark bg, bright text",
          "Human faces increase CTR 30%",
          "No logo on thumbnail",
          "Red for pain, green for gain",
        ],
      };

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              { script: args.script, concept, specs },
              null,
              2
            ),
          },
        ],
      };
    }

    default:
      return {
        content: [{ type: "text", text: `Unknown tool: ${name}` }],
      };
  }
});

// Helpers
function formatTime(ms, format) {
  const hours = Math.floor(ms / 3600000);
  const minutes = Math.floor((ms % 3600000) / 60000);
  const seconds = Math.floor((ms % 60000) / 1000);
  const millis = Math.floor(ms % 1000);

  if (format === "vtt") {
    return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}.${String(millis).padStart(3, "0")}`;
  }
  // SRT uses comma
  return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")},${String(millis).padStart(3, "0")}`;
}

// Start
const transport = new StdioServerTransport();
await server.connect(transport);
