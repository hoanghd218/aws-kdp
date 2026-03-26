# HƯỚNG DẪN XÂY DỰNG BACKEND NODEJS — KDP COLORING BOOK GENERATOR

## 1. TỔNG QUAN DỰ ÁN

Xây dựng **REST API backend bằng Node.js** để tự động tạo coloring book bán trên Amazon KDP. Pipeline gồm 4 bước:

1. **Plan Book** — Gọi Gemini API (text-only) tạo metadata SEO + prompts cho từng trang
2. **Generate Images** — Gọi AI33 API tạo ảnh line art từ prompts, post-process thành grayscale
3. **Build PDF** — Ghép ảnh thành PDF chuẩn KDP (title page, copyright, coloring pages, thank you)
4. **Generate Cover** — Tạo full cover (front + spine + back) chuẩn KDP

---

## 2. TECH STACK

```
Runtime:       Node.js 20+
Framework:     Express.js (hoặc Fastify)
Database:      PostgreSQL (lưu books, jobs, status) + Prisma ORM
Queue:         BullMQ + Redis (xử lý image generation async)
Image:         Sharp (post-process images)
PDF:           PDFKit (tạo PDF)
AI APIs:       AI33 API (image generation), Google Gemini API (text planning + cover art)
Storage:       AWS S3 (lưu images, PDFs, covers)
Auth:          JWT
Deploy:        Docker → AWS ECS hoặc Railway
```

---

## 3. CẤU TRÚC THƯ MỤC

```
kdp-backend/
├── src/
│   ├── config/
│   │   ├── index.ts              # App config, env vars
│   │   ├── kdp.ts                # KDP specifications (page sizes, DPI, margins)
│   │   └── prompts.ts            # Base prompt templates (kids, adults)
│   ├── routes/
│   │   ├── books.routes.ts       # CRUD books + trigger pipeline
│   │   ├── images.routes.ts      # Image generation + review
│   │   ├── pdf.routes.ts         # Build PDF
│   │   └── covers.routes.ts      # Generate cover
│   ├── controllers/
│   │   ├── books.controller.ts
│   │   ├── images.controller.ts
│   │   ├── pdf.controller.ts
│   │   └── covers.controller.ts
│   ├── services/
│   │   ├── planner.service.ts    # Gemini API text planning
│   │   ├── ai33.service.ts       # AI33 image generation
│   │   ├── image-processor.service.ts  # Sharp post-processing
│   │   ├── pdf-builder.service.ts      # PDFKit assembly
│   │   └── cover-builder.service.ts    # Cover generation + composition
│   ├── jobs/
│   │   ├── image-generation.job.ts     # BullMQ worker
│   │   └── cover-generation.job.ts
│   ├── models/
│   │   └── schema.prisma         # Database schema
│   ├── middleware/
│   │   ├── auth.ts
│   │   └── error-handler.ts
│   └── app.ts                    # Express app setup
├── prisma/
│   └── schema.prisma
├── .env.example
├── package.json
├── tsconfig.json
└── Dockerfile
```

---

## 4. DATABASE SCHEMA (Prisma)

```prisma
model Book {
  id          String   @id @default(uuid())
  userId      String
  themeKey    String   @unique  // snake_case, e.g. "kawaii_food_sweets"
  status      BookStatus @default(DRAFT)

  // From Gemini planning
  title       String
  subtitle    String?
  description String?   @db.Text
  keywords    String[]  // 7 SEO keywords
  coverPrompt String?   @db.Text
  audience    Audience  @default(KIDS)
  pageSize    PageSize  @default(SIZE_8_5x11)

  // Output files (S3 URLs)
  pdfUrl      String?
  coverPngUrl String?
  coverPdfUrl String?

  // Metadata
  totalPages  Int       @default(30)
  authorName  String?
  createdAt   DateTime  @default(now())
  updatedAt   DateTime  @updatedAt

  pages       Page[]
}

model Page {
  id          String    @id @default(uuid())
  bookId      String
  book        Book      @relation(fields: [bookId], references: [id])
  pageNumber  Int       // 1-based
  prompt      String    @db.Text
  status      PageStatus @default(PENDING)
  imageUrl    String?   // S3 URL after generation
  needsRegen  Boolean   @default(false)
  regenNote   String?
  createdAt   DateTime  @default(now())
  updatedAt   DateTime  @updatedAt

  @@unique([bookId, pageNumber])
}

enum BookStatus {
  DRAFT          // Plan created, no images yet
  GENERATING     // Images being generated
  IMAGES_DONE    // All images generated
  REVIEWING      // User reviewing images
  BUILDING_PDF   // PDF being assembled
  PDF_DONE       // PDF ready
  BUILDING_COVER // Cover being generated
  COMPLETE       // Everything done
  ERROR
}

enum PageStatus {
  PENDING
  GENERATING
  DONE
  FAILED
  NEEDS_REGEN
}

enum Audience {
  KIDS
  ADULTS
  BOTH
}

enum PageSize {
  SIZE_8_5x11   // 8.5" x 11" portrait
  SIZE_8_5x8_5  // 8.5" x 8.5" square
}
```

---

## 5. KDP SPECIFICATIONS (config/kdp.ts)

```typescript
export const KDP = {
  DPI: 300,
  MARGIN_INCHES: 0.25,

  PAGE_SIZES: {
    "8.5x11": {
      width: 8.5,
      height: 11.0,
      widthPx: 2550,   // 8.5 * 300
      heightPx: 3300,  // 11 * 300
      aspectRatio: "3:4",
      label: '8.5" x 11" (Portrait)',
    },
    "8.5x8.5": {
      width: 8.5,
      height: 8.5,
      widthPx: 2550,
      heightPx: 2550,
      aspectRatio: "1:1",
      label: '8.5" x 8.5" (Square)',
    },
  },

  MARGIN_PX: 75,  // 0.25 * 300

  // Cover
  BLEED_INCHES: 0.125,
  PAPER_THICKNESS: 0.002252,  // inches per page (white paper)
  SAFE_MARGIN: 0.375,
  MIN_PAGES_FOR_SPINE_TEXT: 79,

  // AI33 API
  AI33_API_URL: "https://api.ai33.pro/v1i/task/generate-image",
  AI33_STATUS_URL: "https://api.ai33.pro/v1/task",
  AI33_MODEL_ID: "gemini-3.1-flash-image-preview",
  AI33_RESOLUTION: "2K",
  AI33_POLL_INTERVAL_MS: 5000,
  AI33_POLL_TIMEOUT_MS: 300000,

  // Gemini
  GEMINI_MODEL: "gemini-3.1-flash-image-preview",

  // Limits
  MAX_PARALLEL_WORKERS: 5,
  MAX_RETRIES: 3,
  REQUEST_DELAY_MS: 3000,
};
```

---

## 6. API ENDPOINTS

### 6.1. Books

```
POST   /api/books/plan
  Body: { concept: string, audience: "kids"|"adults", pages: number, themeKey: string }
  → Gọi Gemini API tạo plan, lưu DB, trả về Book object

GET    /api/books
  → List all books của user

GET    /api/books/:id
  → Chi tiết book + pages

PUT    /api/books/:id
  → Update metadata (title, subtitle, keywords, authorName...)

DELETE /api/books/:id
  → Xóa book + images trên S3
```

### 6.2. Images

```
POST   /api/books/:id/generate
  Body: { startIndex?: number, count?: number }
  → Queue job generate images cho book, trả về jobId

GET    /api/books/:id/generate/status
  → Trạng thái generation (pending, progress %, done, errors)

POST   /api/books/:id/pages/:pageId/regenerate
  Body: { newPrompt?: string }
  → Regenerate 1 page cụ thể

GET    /api/books/:id/pages
  → List tất cả pages + status + image URLs

POST   /api/books/:id/pages/:pageId/review
  Body: { approved: boolean, note?: string }
  → Mark page as approved hoặc needs regen
```

### 6.3. PDF

```
POST   /api/books/:id/build-pdf
  → Queue job build PDF, trả về jobId

GET    /api/books/:id/pdf
  → Download PDF (redirect S3 signed URL)
```

### 6.4. Cover

```
POST   /api/books/:id/build-cover
  Body: { authorName?: string, renderer?: "gemini"|"ai33", kdpWidth?: number, kdpHeight?: number }
  → Queue job generate cover

GET    /api/books/:id/cover
  → Download cover PDF (redirect S3 signed URL)
```

### 6.5. Full Pipeline

```
POST   /api/books/:id/build-all
  → Chạy toàn bộ pipeline: generate images → build PDF → build cover
  Trả về jobId để poll status

GET    /api/jobs/:jobId/status
  → Trạng thái job (queued, processing, step, progress, done, error)
```

---

## 7. SERVICE IMPLEMENTATIONS

### 7.1. Planner Service (planner.service.ts)

Gọi Gemini API (text-only) để tạo book plan:

```typescript
// Input: concept, audience, pages count
// Output: { title, subtitle, description, keywords[7], coverPrompt, pagePrompts[] }

// Prompt template cho adults:
const ADULT_PROMPT = (concept: string, pages: number) => `
Generate a complete adult-friendly coloring book package based on the concept below, but do not generate any images; output text only.
Concept: ${concept}
Number of coloring pages: ${pages}

All prompts must be written specifically for image generation and must later create final illustrations, but for now only text should be produced.
Every coloring page prompt must follow a refined "cute cozy medium-detail" adult aesthetic with complete, layered scenes that never feel empty, but all details must remain clean, bold, and easy to color.
Absolutely avoid dense clusters of small shapes; all vegetation, plants, flowers must be drawn using large, simple, stylized shapes with wide line spacing.
Characters must maintain consistent kawaii proportions and expressive poses.

Output format (respond ONLY with this JSON, no other text):
{
  "title": "catchy SEO-friendly title",
  "subtitle": "descriptive subtitle",
  "description": "3-5 sentence commercial description for Amazon KDP emphasizing cozy charm and relaxation",
  "keywords": ["keyword1", "keyword2", ... 7 keywords],
  "cover_prompt": "full-color cover illustration prompt that includes title/subtitle text, warm premium cozy aesthetic, states 'Coloring Book for Adults'",
  "page_prompts": ["prompt1", "prompt2", ... ${pages} prompts, each describing a finished black-and-white coloring page with medium detail, large clear decorative shapes, cozy fully developed scenes]
}`;

// Prompt template cho kids:
const KIDS_PROMPT = (concept: string, pages: number) => `
Generate a complete children's coloring book package based on the concept below, but do not generate any images; output text only.
Concept: ${concept}
Target age: 6-12
Number of coloring pages: ${pages}

All prompts must be written specifically for image generation. Each coloring page must be a black-and-white line art page with:
- Bold, thick, clean outlines suitable for children ages 6-12
- Simple enough for kids to color with crayons or markers
- Single subject centered on page, filling most of the space
- NO shading, NO gradients, NO gray tones
- White background, no borders or frames
- Cute, friendly, appealing style

Output format (respond ONLY with this JSON, no other text):
{
  "title": "catchy SEO-friendly title with 'for Kids Ages 6-12'",
  "subtitle": "descriptive subtitle",
  "description": "3-5 sentence commercial description for Amazon KDP emphasizing fun and creativity for children",
  "keywords": ["keyword1", "keyword2", ... 7 keywords],
  "cover_prompt": "full-color vibrant cover illustration prompt, cartoon style, eye-catching, NO text in image, states 'Coloring Book for Kids Ages 6-12'",
  "page_prompts": ["prompt1", "prompt2", ... ${pages} prompts, each describing a single cute subject for a children's coloring page]
}`;

// Parse response: strip markdown fences (```json ... ```), JSON.parse()
function parseJsonResponse(text: string): object {
  let cleaned = text.trim();
  const match = cleaned.match(/```(?:json)?\s*\n?(.*?)\n?\s*```/s);
  if (match) cleaned = match[1].trim();
  return JSON.parse(cleaned);
}
```

**Gemini API call:**
```typescript
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({ apiKey: process.env.GOOGLE_API_KEY });

async function planBook(concept: string, audience: string, pages: number) {
  const prompt = audience === "adults"
    ? ADULT_PROMPT(concept, pages)
    : KIDS_PROMPT(concept, pages);

  const response = await ai.models.generateContent({
    model: "gemini-3.1-flash-image-preview",
    contents: prompt,
    config: { responseModalities: ["TEXT"] },
  });

  const text = response.candidates[0].content.parts
    .filter(p => p.text)
    .map(p => p.text)
    .join("");

  return parseJsonResponse(text);
}
```

### 7.2. AI33 Service (ai33.service.ts)

Generate images qua AI33 API (submit → poll → download):

```typescript
import axios from "axios";
import { KDP } from "../config/kdp";

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function generateImage(prompt: string, aspectRatio: string = "3:4"): Promise<Buffer> {
  const apiKey = process.env.AI33_KEY;
  if (!apiKey) throw new Error("AI33_KEY not configured");

  for (let attempt = 0; attempt < KDP.MAX_RETRIES; attempt++) {
    try {
      // Step 1: Submit task
      const submitResponse = await axios.post(KDP.AI33_API_URL, {
        prompt,
        model_id: KDP.AI33_MODEL_ID,
        generations_count: "1",
        model_parameters: JSON.stringify({
          aspect_ratio: aspectRatio,
          resolution: KDP.AI33_RESOLUTION,
        }),
      }, {
        headers: { "xi-api-key": apiKey },
      });

      if (!submitResponse.data.success) {
        console.error(`AI33 submit failed (attempt ${attempt + 1}):`, submitResponse.data);
        continue;
      }

      const taskId = submitResponse.data.task_id;
      console.log(`Task submitted: ${taskId} (credits: ${submitResponse.data.ec_remain_credits})`);

      // Step 2: Poll until done (max 300s, check every 5s)
      let elapsed = 0;
      while (elapsed < KDP.AI33_POLL_TIMEOUT_MS) {
        await sleep(KDP.AI33_POLL_INTERVAL_MS);
        elapsed += KDP.AI33_POLL_INTERVAL_MS;

        const statusResp = await axios.get(`${KDP.AI33_STATUS_URL}/${taskId}`, {
          headers: {
            "Content-Type": "application/json",
            "xi-api-key": apiKey,
          },
        });

        const status = statusResp.data;

        if (status.status === "done") {
          const images = status.metadata?.result_images || [];
          if (!images.length || !images[0].imageUrl) {
            throw new Error("Task done but no image returned");
          }

          // Step 3: Download image
          const imageResp = await axios.get(images[0].imageUrl, {
            responseType: "arraybuffer",
          });
          return Buffer.from(imageResp.data);
        }

        if (status.status === "error") {
          throw new Error(status.error_message || "AI33 generation error");
        }

        // Log progress every 15s
        if (elapsed % 15000 === 0) {
          console.log(`Polling... status=${status.status} progress=${status.progress || 0}%`);
        }
      }

      throw new Error(`Timeout waiting for AI33 task ${taskId}`);
    } catch (error) {
      console.error(`Error (attempt ${attempt + 1}/${KDP.MAX_RETRIES}):`, error.message);
      if (attempt < KDP.MAX_RETRIES - 1) {
        await sleep(KDP.REQUEST_DELAY_MS * 2);
      }
    }
  }

  throw new Error("All retry attempts failed");
}

export { generateImage };
```

### 7.3. Image Processor (image-processor.service.ts)

Post-process ảnh bằng Sharp:

```typescript
import sharp from "sharp";
import { KDP } from "../config/kdp";

type PageSizeKey = "8.5x11" | "8.5x8.5";

async function postProcess(imageBuffer: Buffer, pageSize: PageSizeKey = "8.5x11"): Promise<Buffer> {
  const dims = KDP.PAGE_SIZES[pageSize];
  const marginPx = KDP.MARGIN_PX;
  const safeW = dims.widthPx - 2 * marginPx;
  const safeH = dims.heightPx - 2 * marginPx;

  // 1. Convert to grayscale + resize to fit safe area (preserve aspect ratio)
  const resized = await sharp(imageBuffer)
    .grayscale()
    .resize(safeW, safeH, {
      fit: "inside",
      withoutEnlargement: false,
    })
    .toBuffer();

  // 2. Get resized dimensions for centering
  const metadata = await sharp(resized).metadata();
  const imgW = metadata.width!;
  const imgH = metadata.height!;

  // 3. Increase contrast to make lines crisp black on white
  const contrasted = await sharp(resized)
    .linear(2.0, -(255 * 0.3))  // contrast boost + brightness
    .toBuffer();

  // 4. Center on full page with white background (margins included)
  const offsetX = Math.floor((dims.widthPx - imgW) / 2);
  const offsetY = Math.floor((dims.heightPx - imgH) / 2);

  return sharp({
    create: {
      width: dims.widthPx,
      height: dims.heightPx,
      channels: 1,
      background: 255,  // white
    },
  })
    .composite([{ input: contrasted, left: offsetX, top: offsetY }])
    .png({ quality: 100 })
    .toBuffer();
}

export { postProcess };
```

### 7.4. PDF Builder (pdf-builder.service.ts)

Dùng PDFKit ghép PDF:

```typescript
import PDFDocument from "pdfkit";
import { KDP } from "../config/kdp";

interface BookData {
  title: string;
  subtitle: string;
  audience: "kids" | "adults" | "both";
  pageSize: "8.5x11" | "8.5x8.5";
  pageImages: Buffer[];  // sorted coloring page images
}

async function buildPDF(book: BookData): Promise<Buffer> {
  const dims = KDP.PAGE_SIZES[book.pageSize];
  const pageW = dims.width * 72;  // PDFKit uses points (72 per inch)
  const pageH = dims.height * 72;

  return new Promise((resolve, reject) => {
    const doc = new PDFDocument({ size: [pageW, pageH], margin: 0, autoFirstPage: false });
    const buffers: Buffer[] = [];
    doc.on("data", (chunk) => buffers.push(chunk));
    doc.on("end", () => resolve(Buffer.concat(buffers)));
    doc.on("error", reject);

    // --- Page 1: Title Page ---
    doc.addPage();
    doc.fontSize(36).font("Helvetica-Bold");
    const titleLines = wrapText(book.title, 25);
    let yStart = pageH * 0.55;
    for (const line of titleLines) {
      doc.text(line, 0, yStart, { align: "center", width: pageW });
      yStart += 45;
    }

    doc.fontSize(16).font("Helvetica");
    const subtitleLines = wrapText(book.subtitle, 45);
    let ySub = pageH * 0.35;
    for (const line of subtitleLines) {
      doc.text(line, 0, ySub, { align: "center", width: pageW });
      ySub += 22;
    }

    doc.fontSize(14).font("Helvetica-Oblique");
    const tagline = book.audience === "adults"
      ? "Cozy & Relaxing Designs"
      : "Bold & Easy Designs";
    doc.text(tagline, 0, pageH * 0.25, { align: "center", width: pageW });

    // --- Page 2: Copyright ---
    doc.addPage();
    doc.fontSize(11).font("Helvetica");
    const copyrightLines = [
      "Copyright (c) 2026. All rights reserved.",
      "",
      "No part of this book may be reproduced or used in any manner",
      "without written permission of the copyright owner.",
      "",
      book.audience === "adults"
        ? "This coloring book is designed for adults who enjoy relaxing,"
        : "This coloring book is designed for children ages 6-12.",
      book.audience === "adults" ? "creative coloring sessions." : "",
      "",
      "For personal use only. Not for resale.",
      "",
      book.audience === "adults"
        ? "We hope you enjoy every page!"
        : "Made with love for creative kids everywhere!",
    ];
    let yCopy = pageH * 0.6;
    for (const line of copyrightLines) {
      doc.text(line, 0, yCopy, { align: "center", width: pageW });
      yCopy -= 18;
    }

    // --- Coloring Pages (odd) + Blank Backs (even) ---
    for (const imageBuffer of book.pageImages) {
      // Coloring page
      doc.addPage();
      doc.image(imageBuffer, 0, 0, {
        width: pageW,
        height: pageH,
        fit: [pageW, pageH],
        align: "center",
        valign: "center",
      });

      // Blank back page (prevents bleed-through when coloring)
      doc.addPage();
    }

    // --- Last Page: Thank You ---
    doc.addPage();
    doc.fontSize(28).font("Helvetica-Bold");
    doc.text("Thank You!", 0, pageH * 0.55, { align: "center", width: pageW });
    doc.fontSize(16).font("Helvetica");
    doc.text("We hope you enjoyed coloring!", 0, pageH * 0.45, { align: "center", width: pageW });
    doc.fontSize(14);
    doc.text("If you liked this book, please leave a review.", 0, pageH * 0.38, {
      align: "center", width: pageW,
    });

    // Ensure even total page count (KDP requirement)
    // title(1) + copyright(1) + coloringPages*2 + thankYou(1)
    const totalPages = 2 + book.pageImages.length * 2 + 1;
    if (totalPages % 2 !== 0) {
      doc.addPage(); // Add blank page to make even
    }

    doc.end();
  });
}

function wrapText(text: string, maxChars: number = 25): string[] {
  const words = text.split(" ");
  const lines: string[] = [];
  let current = "";
  for (const word of words) {
    if (current.length + word.length + 1 > maxChars && current) {
      lines.push(current.trim());
      current = word;
    } else {
      current += " " + word;
    }
  }
  if (current.trim()) lines.push(current.trim());
  return lines;
}

export { buildPDF };
```

### 7.5. Cover Builder (cover-builder.service.ts)

Tạo cover KDP (front + spine + back):

```typescript
import sharp from "sharp";
import { KDP } from "../config/kdp";

interface CoverDimensions {
  totalPages: number;
  spineWidthInches: number;
  fullWidthPx: number;
  fullHeightPx: number;
  bleedPx: number;
  trimWPx: number;
  spineWPx: number;
  safePx: number;
  backStartX: number;
  spineStartX: number;
  frontStartX: number;
  canHaveSpineText: boolean;
}

// Cover dimensions calculation
function calculateCoverDimensions(
  totalPages: number,
  trimW: number,
  trimH: number
): CoverDimensions {
  const spineWidth = totalPages * KDP.PAPER_THICKNESS;
  const fullWidth = (2 * trimW) + spineWidth + (2 * KDP.BLEED_INCHES);
  const fullHeight = trimH + (2 * KDP.BLEED_INCHES);

  const fullWidthPx = Math.round(fullWidth * KDP.DPI);
  const fullHeightPx = Math.round(fullHeight * KDP.DPI);
  const bleedPx = Math.round(KDP.BLEED_INCHES * KDP.DPI);
  const trimWPx = Math.round(trimW * KDP.DPI);
  const spineWPx = Math.round(spineWidth * KDP.DPI);
  const safePx = Math.round(KDP.SAFE_MARGIN * KDP.DPI);

  return {
    totalPages,
    spineWidthInches: spineWidth,
    fullWidthPx,
    fullHeightPx,
    bleedPx,
    trimWPx,
    spineWPx,
    safePx,
    backStartX: bleedPx,
    spineStartX: bleedPx + trimWPx,
    frontStartX: bleedPx + trimWPx + spineWPx,
    canHaveSpineText: totalPages >= KDP.MIN_PAGES_FOR_SPINE_TEXT,
  };
}

// Cover layout: | BLEED | BACK COVER | SPINE | FRONT COVER | BLEED |
//
// Front cover: AI-generated full-color artwork (from coverPrompt in plan)
//   - Generate via AI33 API (aspect_ratio "3:4" for portrait, "1:1" for square)
//   - Resize to fit front cover area (trimWPx x fullHeightPx)
//   - Title text is included in the AI prompt (baked into artwork)
//   - Author name overlaid at bottom with text outline for readability
//   - Bottom gradient overlay (transparent→dark) for subtitle/author readability
//
// Spine: solid color slightly darker than back
//   - Text only if totalPages >= 79 (vertical text: book title + author)
//
// Back cover: light solid background color
//   - Book name (centered, top)
//   - Description bullet points (centered, below title)
//   - 6 sample pages in 2x3 grid (evenly spaced from generated pages)
//   - Barcode placeholder (white rectangle, bottom-right, KDP auto-generates barcode)
//
// Final output: PNG + PDF at 300 DPI, upload to S3

// Count total pages for spine calculation
function countTotalPages(numColoringPages: number): number {
  // title(1) + copyright(1) + coloringPages * 2 (page + blank back) + thankYou(1)
  let total = 2 + numColoringPages * 2 + 1;
  if (total % 2 !== 0) total += 1; // KDP requires even
  return total;
}

export { calculateCoverDimensions, countTotalPages };
```

---

## 8. QUEUE JOBS (BullMQ)

```typescript
import { Queue, Worker } from "bullmq";
import { generateImage } from "../services/ai33.service";
import { postProcess } from "../services/image-processor.service";
import { uploadToS3 } from "../services/s3.service";
import { prisma } from "../config/db";

// Create queue
const imageQueue = new Queue("image-generation", {
  connection: { url: process.env.REDIS_URL },
});

// Worker - processes pages with parallel batches (max 5 concurrent)
const imageWorker = new Worker("image-generation", async (job) => {
  const { bookId, startIndex = 0, count } = job.data;

  const book = await prisma.book.findUnique({
    where: { id: bookId },
    include: { pages: { orderBy: { pageNumber: "asc" } } },
  });

  if (!book) throw new Error(`Book ${bookId} not found`);

  await prisma.book.update({
    where: { id: bookId },
    data: { status: "GENERATING" },
  });

  const pagesToGenerate = book.pages
    .filter(p => p.status === "PENDING" || p.status === "NEEDS_REGEN")
    .slice(startIndex, count ? startIndex + count : undefined);

  const pageSize = book.pageSize === "SIZE_8_5x8_5" ? "8.5x8.5" : "8.5x11";
  const aspectRatio = pageSize === "8.5x8.5" ? "1:1" : "3:4";
  let completedCount = 0;

  // Process in batches of MAX_PARALLEL_WORKERS (5)
  const batchSize = 5;
  for (let i = 0; i < pagesToGenerate.length; i += batchSize) {
    const batch = pagesToGenerate.slice(i, i + batchSize);

    await Promise.all(batch.map(async (page) => {
      try {
        await prisma.page.update({
          where: { id: page.id },
          data: { status: "GENERATING" },
        });

        const imageBuffer = await generateImage(page.prompt, aspectRatio);
        const processed = await postProcess(imageBuffer, pageSize);
        const s3Key = `books/${bookId}/page_${String(page.pageNumber).padStart(2, "0")}.png`;
        const s3Url = await uploadToS3(processed, s3Key);

        await prisma.page.update({
          where: { id: page.id },
          data: { status: "DONE", imageUrl: s3Url, needsRegen: false },
        });

        completedCount++;
        await job.updateProgress(Math.round((completedCount / pagesToGenerate.length) * 100));
      } catch (error) {
        console.error(`Failed page ${page.pageNumber}:`, error.message);
        await prisma.page.update({
          where: { id: page.id },
          data: { status: "FAILED" },
        });
      }
    }));
  }

  // Check if all pages done
  const allPages = await prisma.page.findMany({ where: { bookId } });
  const allDone = allPages.every(p => p.status === "DONE");
  const anyFailed = allPages.some(p => p.status === "FAILED");

  await prisma.book.update({
    where: { id: bookId },
    data: { status: allDone ? "IMAGES_DONE" : anyFailed ? "ERROR" : "IMAGES_DONE" },
  });

  return { completedCount, total: pagesToGenerate.length };
}, {
  connection: { url: process.env.REDIS_URL },
  concurrency: 1,  // 1 book at a time, parallelism is within the job
});

export { imageQueue, imageWorker };
```

---

## 9. ENV VARIABLES

```env
# Server
PORT=3000
NODE_ENV=development
DATABASE_URL=postgresql://user:pass@localhost:5432/kdp
REDIS_URL=redis://localhost:6379

# AI APIs
GOOGLE_API_KEY=your_gemini_api_key
AI33_KEY=your_ai33_api_key

# AWS S3
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
S3_BUCKET=kdp-coloring-books

# Auth
JWT_SECRET=your_jwt_secret
```

---

## 10. BUSINESS RULES QUAN TRỌNG

1. **Page count phải CHẴN** — KDP yêu cầu tổng số trang phải chẵn. Nếu lẻ, thêm 1 trang trắng cuối
2. **Single-sided printing** — Mỗi trang tô màu phải có 1 trang trắng phía sau (tránh thấm mực)
3. **Layout PDF:** Title → Copyright → [Coloring Page + Blank Back] × N → Thank You → (blank if odd)
4. **Image post-process:** PHẢI convert grayscale, tăng contrast, center trên trang trắng với margins
5. **Spine text:** Chỉ được thêm text trên gáy sách khi >= 79 trang
6. **Cover bleed:** 0.125" mỗi bên, safe margin 0.375"
7. **Spine width:** = totalPages × 0.002252 inches (white paper)
8. **Aspect ratio:** 3:4 cho 8.5x11, 1:1 cho 8.5x8.5
9. **AI33 API flow:** POST submit → GET poll status every 5s → download imageUrl when done
10. **Resume support:** Skip pages đã generate (check imageUrl != null)

---

## 11. PROMPT GUIDELINES

### Kids (6-12):
- Bold thick clean outlines
- Single subject centered, fills page
- NO shading/gradients/borders/frames
- Simple enough for crayons/markers
- Cute, friendly, appealing style

### Adults (cozy/cute):
- "Cute cozy medium-detail" aesthetic
- Layered scenes: foreground + midground + background
- Large stylized shapes, NO dense small clusters
- Kawaii proportions, cozy environments
- Clean, bold, easy to color

---

## 12. SAMPLE PLAN JSON STRUCTURE

```json
{
  "theme_key": "kawaii_food_sweets",
  "audience": "both",
  "page_size": "8.5x8.5",
  "title": "Kawaii Food & Sweets Coloring Book: Cute Kawaii Food with Adorable Faces — Bold and Easy Designs for Kids, Teens & Adults",
  "subtitle": "50 Adorable Kawaii Food Characters with Smiling Faces — Donuts, Sushi, Cupcakes, Bubble Tea & More",
  "description": "Discover the cutest food coloring book ever! This kawaii food and sweets coloring book features 50 adorable food characters...",
  "keywords": [
    "kawaii food coloring book",
    "cute food coloring pages",
    "kawaii coloring book for kids and adults",
    "bold and easy coloring book",
    "kawaii sweets coloring",
    "cute food faces coloring book",
    "kawaii dessert coloring pages"
  ],
  "cover_prompt": "Full-color vibrant kawaii food illustration for a coloring book cover, professional quality...",
  "page_prompts": [
    "A children's coloring book page in SQUARE format (1:1 aspect ratio). Black and white line art ONLY. A cute kawaii donut with a happy smiling face...",
    "A children's coloring book page in SQUARE format (1:1 aspect ratio). Black and white line art ONLY. A cute kawaii sushi roll..."
  ]
}
```

---

## 13. RECOMMENDED IMPLEMENTATION ORDER

1. **Setup project** — Express + TypeScript + Prisma + Docker Compose (Postgres + Redis)
2. **Config + KDP specs** — Tất cả constants, page sizes, dimensions
3. **Planner Service** — Gemini API text planning
4. **Books CRUD** — POST /plan, GET list, GET detail
5. **AI33 Service** — Submit/poll/download
6. **Image Processor** — Sharp grayscale + contrast + center
7. **BullMQ Queue** — Image generation worker
8. **Image endpoints** — Generate, status, review, regenerate
9. **PDF Builder** — PDFKit assembly
10. **Cover Builder** — Dimensions calc + artwork + composition
11. **S3 integration** — Upload/download
12. **Full pipeline endpoint** — Build-all orchestration
13. **Auth + Error handling**
14. **Dockerize + Deploy**
