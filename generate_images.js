#!/usr/bin/env node
/**
 * KDP Coloring Book Image Generator (Node.js)
 * Usage: node generate_images.js <prompts_file> [options]
 *
 * Options:
 *   --workers N       Number of parallel workers (default: 4)
 *   --start N         Start from prompt index N (for resuming)
 *   --count N         Generate only N images
 *   --aspect 1:1|3:4  Override aspect ratio (auto-detected by default)
 *   --out DIR         Override output directory
 */

require("dotenv").config();
const fs = require("fs");
const path = require("path");
const axios = require("axios");
const FormData = require("form-data");
const sharp = require("sharp");

// ── Config ────────────────────────────────────────────────────────────────────
const AI33_API_URL = "https://api.ai33.pro/v1i/task/generate-image";
const AI33_STATUS_URL = "https://api.ai33.pro/v1/task";
const AI33_MODEL_ID = "gemini-3.1-flash-image-preview";
const AI33_RESOLUTION = "2K";
const POLL_INTERVAL_MS = 5000;
const POLL_TIMEOUT_MS = 300000;
const MAX_RETRIES = 3;
const DPI = 300;
const MARGIN_PX = 75; // 0.25" * 300 DPI

const PAGE_DIMS = {
  "1:1": { width: 2550, height: 2550 },
  "3:4": { width: 2550, height: 3300 },
};

// ── CLI args ──────────────────────────────────────────────────────────────────
function parseArgs() {
  const args = process.argv.slice(2);
  if (args.length === 0 || args[0].startsWith("--")) {
    console.error("Usage: node generate_images.js <prompts_file> [--workers N] [--start N] [--count N] [--aspect 1:1|3:4] [--out DIR]");
    process.exit(1);
  }

  const opts = {
    promptsFile: args[0],
    workers: 4,
    start: 0,
    count: null,
    aspect: null,
    outDir: null,
    force: false,
  };

  for (let i = 1; i < args.length; i++) {
    switch (args[i]) {
      case "--workers": opts.workers = parseInt(args[++i]); break;
      case "--start":   opts.start   = parseInt(args[++i]); break;
      case "--count":   opts.count   = parseInt(args[++i]); break;
      case "--aspect":  opts.aspect  = args[++i]; break;
      case "--out":     opts.outDir  = args[++i]; break;
      case "--force":   opts.force   = true; break;
      default:
        console.error(`Unknown option: ${args[i]}`);
        process.exit(1);
    }
  }

  return opts;
}

// ── Detect aspect ratio from prompt content ───────────────────────────────────
function detectAspectRatio(prompts) {
  const sample = prompts.slice(0, 5).join(" ").toLowerCase();
  if (sample.includes("square") || sample.includes("1:1")) return "1:1";
  return "3:4";
}

// ── Sleep helper ──────────────────────────────────────────────────────────────
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// ── Generate one image via AI33 ───────────────────────────────────────────────
async function generateImage(prompt, aspect, apiKey) {
  for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
    try {
      // 1. Submit task
      const form = new FormData();
      form.append("prompt", prompt);
      form.append("model_id", AI33_MODEL_ID);
      form.append("generations_count", "1");
      form.append("model_parameters", JSON.stringify({ aspect_ratio: aspect, resolution: AI33_RESOLUTION }));

      const submitRes = await axios.post(AI33_API_URL, form, {
        headers: { ...form.getHeaders(), "xi-api-key": apiKey },
        timeout: 30000,
      });

      const { success, task_id, ec_remain_credits } = submitRes.data;
      if (!success || !task_id) {
        console.log(`  [attempt ${attempt}] Submit failed:`, submitRes.data);
        continue;
      }
      console.log(`  Task ${task_id} submitted (credits: ${ec_remain_credits ?? "?"})`);

      // 2. Poll for completion
      const deadline = Date.now() + POLL_TIMEOUT_MS;
      while (Date.now() < deadline) {
        await sleep(POLL_INTERVAL_MS);

        const statusRes = await axios.get(`${AI33_STATUS_URL}/${task_id}`, {
          headers: { "Content-Type": "application/json", "xi-api-key": apiKey },
          timeout: 15000,
        });

        const { status, metadata, progress } = statusRes.data;

        if (status === "done") {
          const images = metadata?.result_images ?? [];
          const imageUrl = images[0]?.imageUrl;
          if (!imageUrl) throw new Error("Task done but no imageUrl returned");

          // 3. Download image
          const imgRes = await axios.get(imageUrl, { responseType: "arraybuffer", timeout: 60000 });
          return Buffer.from(imgRes.data);
        }

        if (status === "error") {
          throw new Error(`AI33 error: ${statusRes.data.error_message ?? "unknown"}`);
        }

        // Still processing — log occasionally
        if (progress !== undefined) process.stdout.write(`\r  Polling... ${progress}%   `);
      }

      throw new Error("Timeout waiting for AI33 task");
    } catch (err) {
      console.log(`\n  Error (attempt ${attempt}/${MAX_RETRIES}): ${err.message}`);
      if (attempt < MAX_RETRIES) await sleep(6000);
    }
  }

  return null;
}

// ── Post-process: grayscale + fit + contrast + white background ───────────────
async function postProcess(imageBuffer, aspect) {
  const dims = PAGE_DIMS[aspect];
  const safeW = dims.width - 2 * MARGIN_PX;
  const safeH = dims.height - 2 * MARGIN_PX;

  // Resize to fit within safe area (contain, preserving aspect ratio)
  const resized = await sharp(imageBuffer)
    .grayscale()
    .resize(safeW, safeH, { fit: "inside", kernel: sharp.kernel.lanczos3 })
    .linear(2.0, -(128 * 2.0) + 128 + 30) // contrast boost + brightness lift
    .toBuffer();

  const meta = await sharp(resized).metadata();

  // Center on full white page
  const left = Math.floor((dims.width  - meta.width)  / 2);
  const top  = Math.floor((dims.height - meta.height) / 2);

  return sharp({
    create: { width: dims.width, height: dims.height, channels: 3, background: { r: 255, g: 255, b: 255 } },
  })
    .composite([{ input: resized, left, top }])
    .grayscale()
    .png({ dpi: DPI })
    .toBuffer();
}

// ── Worker pool ───────────────────────────────────────────────────────────────
async function runPool(items, concurrency, fn) {
  let idx = 0;
  async function worker() {
    while (idx < items.length) {
      const i = idx++;
      await fn(items[i], i);
    }
  }
  await Promise.all(Array.from({ length: Math.min(concurrency, items.length) }, worker));
}

// ── Main ──────────────────────────────────────────────────────────────────────
async function main() {
  const opts = parseArgs();

  const apiKey = process.env.AI33_KEY;
  if (!apiKey) {
    console.error("Error: AI33_KEY not found in .env");
    process.exit(1);
  }

  // Read prompts file
  if (!fs.existsSync(opts.promptsFile)) {
    console.error(`Error: File not found: ${opts.promptsFile}`);
    process.exit(1);
  }

  const allPrompts = fs
    .readFileSync(opts.promptsFile, "utf-8")
    .split("\n")
    .map((l) => l.trim())
    .filter(Boolean);

  if (allPrompts.length === 0) {
    console.error("Error: No prompts found in file");
    process.exit(1);
  }

  // Determine aspect ratio
  const aspect = opts.aspect ?? detectAspectRatio(allPrompts);
  if (!PAGE_DIMS[aspect]) {
    console.error(`Error: Unknown aspect ratio "${aspect}". Use "1:1" or "3:4"`);
    process.exit(1);
  }

  // Determine theme key from filename
  const themeKey = path.basename(opts.promptsFile, path.extname(opts.promptsFile));

  // Output directory
  const outDir = opts.outDir ?? path.join(path.dirname(opts.promptsFile), "..", "output", "images", themeKey);
  fs.mkdirSync(outDir, { recursive: true });

  // Slice prompts
  const start = opts.start;
  const end = opts.count ? Math.min(start + opts.count, allPrompts.length) : allPrompts.length;
  const prompts = allPrompts.slice(start, end);

  console.log(`\nKDP Image Generator`);
  console.log(`Theme    : ${themeKey}`);
  console.log(`Prompts  : ${opts.promptsFile}`);
  console.log(`Pages    : ${prompts.length} (index ${start}–${end - 1})`);
  console.log(`Aspect   : ${aspect} (${PAGE_DIMS[aspect].width}×${PAGE_DIMS[aspect].height}px)`);
  console.log(`Workers  : ${opts.workers} parallel`);
  console.log(`Output   : ${outDir}`);
  console.log("─".repeat(60));

  let success = 0;
  let skipped = 0;
  let failed = 0;

  await runPool(prompts, opts.workers, async (prompt, localIdx) => {
    const pageNum = start + localIdx + 1;
    const filename = `page_${String(pageNum).padStart(2, "0")}.png`;
    const filepath = path.join(outDir, filename);

    if (fs.existsSync(filepath) && !opts.force) {
      console.log(`[${pageNum}/${end}] Skip (exists): ${filename}`);
      skipped++;
      return;
    }

    const preview = prompt.length > 80 ? prompt.slice(0, 80) + "…" : prompt;
    console.log(`\n[${pageNum}/${end}] Generating: ${preview}`);

    const rawBuffer = await generateImage(prompt, aspect, apiKey);
    if (!rawBuffer) {
      console.log(`  FAILED: ${filename}`);
      failed++;
      return;
    }

    const processed = await postProcess(rawBuffer, aspect);
    fs.writeFileSync(filepath, processed);
    console.log(`\n  Saved: ${filename}`);
    success++;
  });

  console.log("\n" + "─".repeat(60));
  console.log(`Done! Success: ${success}  Skipped: ${skipped}  Failed: ${failed}`);
  console.log(`Output: ${outDir}`);
}

main().catch((err) => {
  console.error("Fatal error:", err);
  process.exit(1);
});
