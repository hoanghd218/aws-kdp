# Rule & Prompt Tạo Ảnh Coloring Book (từ ý tưởng → prompt)

> Tài liệu tổng hợp toàn bộ **rule viết prompt** và **prompt mẫu** dùng để tạo ảnh trang tô màu KDP,
> trích đúng theo cách skill `kdp-prompt-writer` + `kdp-image-generator` chạy trong pipeline.
> Claude là người viết TẤT CẢ prompt — KHÔNG dùng AI/Gemini để viết prompt, chỉ dùng AI để render ảnh.

---

## 0. Luồng tổng quát: từ ý tưởng → ảnh

```
ý tưởng (ideas/*.md)
   ↓  [kdp-prompt-writer]  Claude phân tích, viết SEO + cover prompt + 20-30 page prompt
plan.json  (output/{theme_key}/plan.json)
   ↓  [kdp-image-generator]  python generate_images.py --plan plan.json --count N
images/page_NN.png  (grayscale, 300 DPI)
```

6 bước viết plan:
1. Xác định **audience** (adults | kids) + **page_size** (8.5x11 | 8.5x8.5) → đọc đúng guide.
2. Viết **SEO metadata**: title, subtitle, description, 7 keywords.
3. Viết **cover prompt** (full màu).
4. Viết **20-30 page prompt** (line art đen trắng).
5. Đảm bảo **đa dạng** + tránh lỗi anatomy của AI.
6. Lưu `plan.json` + `prompts.txt`.

---

## 1. RULE CHUNG (bắt buộc cho mọi prompt)

Đây là rule KDP + chống lỗi AI áp dụng cho **mọi** page prompt, bất kể adults hay kids:

| Rule | Chi tiết |
|------|----------|
| **Black-and-white line art** | Trang tô màu hoàn chỉnh, KHÔNG phải sketch. Nền trắng. |
| **KHÔNG border/frame** | Mỗi prompt PHẢI có câu "no border / no frame / no rectangular boundary line" — model rất hay tự vẽ khung. |
| **Độ dày nét ≥ 0.75pt (0.01")** | Thêm "bold thick outlines suitable for coloring" vào mọi prompt (yêu cầu KDP). |
| **300 DPI tối thiểu** | Xử lý ở bước render (2550×3300 cho 8.5x11, 2550×2550 cho 8.5x8.5). |
| **Đúng orientation** | 8.5x11 → "PORTRAIT orientation (taller than wide)"; 8.5x8.5 → "SQUARE format (1:1 aspect ratio)". |
| **Hạn chế nhân vật** | Ít nhân vật = ít lỗi. Ưu tiên 1 nhân vật + 1 thú cưng thay vì 2 người. |
| **Nhân vật tách rời** | Khi >1 nhân vật: phải có khoảng cách, KHÔNG chạm/ôm/nắm tay/đan vào nhau (gây dính/thừa chi). |

**Câu chống lỗi anatomy** — thêm vào mọi prompt có >1 nhân vật:
> `IMPORTANT: Each character must have clearly defined, complete body with no overlapping or merged body parts`

---

## 2. RULE & PROMPT — NGƯỜI LỚN (Adults: "Cute Cozy Medium-Detail")

### Rule viết
Mỗi trang phải là **scene hoàn chỉnh, ấm cúng** — không trống rỗng, không rối mắt.

PHẢI có:
1. Line art đen trắng, nền trắng, KHÔNG border/frame.
2. **Medium detail** — đủ hấp dẫn người lớn nhưng nét sạch, đậm, dễ tô.
3. **Scene phân lớp**: foreground + midground + background.
4. **Hình trang trí to, rõ** — không cụm chi tiết nhỏ dày đặc.
5. **Cây cối đơn giản hóa** — hình to cách điệu, nét thưa, KHÔNG gân lá li ti, KHÔNG texture nét mảnh.
6. **Họa tiết nền giãn cách** — tường/vải dùng hình to, thưa.
7. **Kawaii proportions** — đầu to, thân nhỏ, mắt to; nhất quán mọi trang.
8. **Đồ vật cozy đầy đủ**: kệ, đèn, gối, cửa sổ, rèm, bàn, tranh, thảm...

MUST AVOID: border/frame, cụm hình nhỏ dày, gân lá, texture nét mảnh, họa tiết thực vật siêu chi tiết, nhiễu thị giác trên tường/vải, bố cục trống hoặc rối.

### Prompt mẫu — Adults (cấu trúc theo skill)

```
Black and white line art illustration for an adult coloring book, cute cozy kawaii
aesthetic, medium detail, bold clean outlines, large open shapes for easy coloring,
no shading. NO borders, NO frames, NO rectangular boundary lines around the image.
White background. PORTRAIT orientation (taller than wide).

Scene: [nhân vật chính] is [đang làm gì] in [bối cảnh cozy].

Foreground: [3-4 vật cụ thể trên bàn, đồ ăn, đồ thủ công].

Midground: [3-4 vật: hành động nhân vật, đồ nội thất, kệ, đèn].

Background: [3-4 vật: cửa sổ có cảnh ngoài trời, tranh tường, rèm].

Clean bold outlines, cozy relaxing environment, easy-to-color shapes, adult coloring
book page. NO borders or frames.
```

### Ví dụ cụ thể đã điền (Cozy Cat Café)

```
Black and white line art illustration for an adult coloring book, cute cozy kawaii
aesthetic, medium detail, bold clean outlines, large open shapes for easy coloring,
no shading. NO borders, NO frames, NO rectangular boundary lines around the image.
White background. PORTRAIT orientation (taller than wide).

Scene: a chubby kawaii cat barista is pouring latte art behind a wooden café counter.

Foreground: a large cup of latte with leaf art, a slice of layered cake, a small
potted succulent, a folded napkin.

Midground: the smiling cat in an apron, an espresso machine with big round knobs,
a tip jar, a stack of saucers.

Background: a tall window with a simple tree outside, a framed coffee poster, a
shelf of large jars, hanging string lights.

Clean bold outlines, cozy relaxing environment, easy-to-color shapes, adult coloring
book page. Bold thick outlines suitable for coloring. NO borders or frames.
```

---

## 3. RULE & PROMPT — TRẺ EM (Kids ages 6-12: "Bold & Easy")

### Rule viết
PHẢI có:
1. Line art đen trắng ONLY.
2. **Nét to, dày, sạch** — hợp trẻ 6-12.
3. **MỘT chủ thể, đặt giữa**, chiếm ≥ 70% trang.
4. Nền trắng, KHÔNG border/frame.
5. Phong cách cute, thân thiện, cartoon.
6. Đủ đơn giản cho bút sáp/marker — không vùng quá nhỏ.

MUST AVOID: shading/gradient/gray, mảng đen đặc, border/frame, nền phức tạp, nhiều chủ thể chồng nhau, chi tiết li ti, chữ/nhãn trong hình.

### Prompt mẫu — Kids (cấu trúc theo skill)

```
A children's coloring book page in PORTRAIT orientation. Black and white line art
only. [chủ thể cute/thân thiện] with thick, clean, bold outlines. Simple enough
for kids ages 6-12 to color. White background. The drawing fills most of the
page vertically. No shading, no gray tones, no borders or frames. Style: cute,
friendly, appealing to children.
```

### Ví dụ cụ thể đã điền (Dinosaur)

```
A children's coloring book page in PORTRAIT orientation. Black and white line art
only. A friendly smiling cartoon Triceratops standing on grass with thick, clean,
bold outlines. Simple enough for kids ages 6-12 to color. White background. The
drawing fills most of the page vertically. A few simple clouds and one small flower.
No shading, no gray tones, no borders or frames. Style: cute, friendly, appealing
to children.
```

---

## 4. BASE_PROMPT của hệ thống (config.py)

Template kids mặc định trong [scripts/config.py](scripts/config.py#L313), điền `{age}` và `{subject}`:

```
Create a children's coloring book page in PORTRAIT orientation (taller than wide). Requirements:
- PORTRAIT layout - the image must be taller than it is wide
- Black and white line art ONLY
- NO shading, NO gray tones, NO gradients, NO filled areas
- Thick, clean, bold outlines
- Simple enough for kids ages {age} to color
- White background
- The drawing should fill most of the page vertically
- Leave adequate spacing from edges
- Style: cute, friendly, appealing to children
- Single subject centered on page
- IMPORTANT: The illustration must NOT have any border, frame, or rectangular outline around the edges. The artwork should extend naturally with NO enclosing box or boundary line.

Subject: {subject}
```

---

## 5. COVER PROMPT (full màu — khác page prompt)

**Adults cover** phải có: illustration **full màu** (không đen trắng), thẩm mỹ cozy ấm/premium, nhiều props to dễ đọc, tham chiếu title + subtitle, ghi "Coloring Book for Adults".

**Kids cover** phải có: full màu, cartoon rực rỡ, nghệ thuật bìa sách trẻ em chuyên nghiệp, **KHÔNG chèn chữ/letter nào trong ảnh**, màu tươi, bố cục vui, nhắc "Coloring Book for Kids Ages 6-12".

---

## 6. Đa dạng & chống lỗi AI (Step 5)

- **Đa dạng scene**: indoor/outdoor/seasonal; nấu ăn/đọc sách/chơi/ngủ/làm thủ công; vui/yên bình/cozy/phiêu lưu; nhiều tư thế nhân vật.
- **Chống lỗi anatomy của AI** (Gemini hay dính/thừa/thiếu chi):
  - Giảm số nhân vật/scene.
  - Nhiều nhân vật → tách rời rõ ràng, không chạm nhau.
  - Ưu tiên thú cưng (mèo/chó/thỏ) thay người thứ hai.
  - Tránh ôm/nắm tay/nhảy cùng nhau.
  - Nhân vật phụ chỉ chấp nhận nếu nhỏ, xa, tách biệt.

---

## 7. Lưu plan & chạy render

`output/{theme_key}/plan.json`:
```json
{
  "theme_key": "the_theme_key",
  "audience": "adults|kids",
  "page_size": "8.5x11|8.5x8.5",
  "title": "...",
  "subtitle": "...",
  "description": "...",
  "keywords": ["kw1","kw2","kw3","kw4","kw5","kw6","kw7"],
  "cover_prompt": "...",
  "page_prompts": ["prompt1","prompt2", "..."]
}
```
Cũng lưu `output/{theme_key}/prompts.txt` (mỗi prompt 1 dòng).

Render ảnh:
```bash
python scripts/generate_images.py --plan output/{theme_key}/plan.json --count {N}
# resume sau lỗi:  --start {index}
```

| page_size | Kích thước | Aspect | Pixel @300DPI |
|-----------|-----------|--------|---------------|
| `8.5x11` (mặc định) | 8.5"×11" dọc | 3:4 | 2550×3300 |
| `8.5x8.5` | 8.5"×8.5" vuông | 1:1 | 2550×2550 |

Post-process tự động: grayscale, contrast +2.0, brightness +1.3, margin 0.25", căn giữa trên nền trắng.

---

## 8. Checklist nhanh trước khi render

- [ ] Mỗi prompt có câu "NO border / NO frame / NO rectangular boundary line".
- [ ] Mỗi prompt có "bold thick outlines suitable for coloring".
- [ ] Đúng orientation theo page_size.
- [ ] Adults: có foreground/midground/background, hình to thưa, kawaii nhất quán.
- [ ] Kids: 1 chủ thể giữa trang ≥70%, không shading/gradient.
- [ ] Scene đa dạng, không lặp.
- [ ] Prompt nhiều nhân vật có câu chống merge body.
- [ ] Cover prompt: full màu; kids cover KHÔNG có chữ.
```