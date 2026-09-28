# Audit quy trình KDP Coloring Book — 2026-08-10

## Kết luận

Trước lần sửa này, pipeline **chưa đủ hiệu quả để quyết định ngách và sản xuất hàng loạt**. Nó có lợi thế là đã dùng dữ liệu Amazon/Apify và có review ảnh, nhưng score ngách dễ tạo false positive, economics sai công thức hiện hành, nội dung frontmatter còn generic, và đường tạo ảnh mặc định vẫn phụ thuộc provider/Gemini.

Sau thay đổi, pipeline phù hợp hơn cho mô hình **validate → làm một flagship → đo dữ liệu thật → mới mở series**. Tuy nhiên, 40 cache niche hiện tại đều quá 30 ngày nên đang bị `REFRESH_DATA`; chưa được xem niche nào là production-ready cho đến khi repull.

## Scorecard

| Khâu | Trước sửa | Sau sửa | Ghi chú |
|---|---:|---:|---|
| Khám phá ý tưởng | 6/10 | 7/10 | Web/trend chỉ dùng để discovery, không còn bị gọi là proof of profit |
| Validate ngách | 4/10 | 8/10 | Thêm relevance, median, demand depth, winner share, freshness, evidence gate |
| Economics | 3/10 | 8/10 | Sửa royalty 50%/60%, công thức và large-trim printing cost |
| Plan/content architecture | 5/10 | 8/10 | Thêm buyer promise, style bible, section arc, duplication matrix |
| Nội dung title/intro/closing | 3/10 | 8/10 | Copy theo theme; text render bằng code, không giao cho model ảnh |
| Tạo trang tô màu | 5/10 | 8/10 | Built-in imagegen mặc định; normalize 300 DPI; một call cho mỗi asset |
| Review ảnh | 7/10 | 8/10 | Review mọi trang, targeted regen, systemic-failure threshold |
| Cover | 6/10 | 8/10 | Imagegen tạo artwork không chữ; code ghép metadata/barcode/bleed |
| KDP preflight | 6/10 | 8/10 | Thêm AI disclosure và sửa low-content classification |

Điểm “sau sửa” là điểm về **thiết kế quy trình**, không phải bảo đảm lợi nhuận. Lợi nhuận chỉ được xác nhận bằng dữ liệu listing/ads/sales sau launch.

## Các lỗi lớn đã phát hiện

### 1. Opportunity Score cũ tạo false positive

Score cũ dùng:

```text
average estimated sales / average reviews
```

Vấn đề:

- một bestseller có thể kéo toàn bộ average;
- các mảng BSR/review bị mất alignment khi thiếu dữ liệu;
- không đo tỷ lệ kết quả thật sự liên quan đến keyword;
- không dùng median hoặc số lượng seller có demand;
- không từ chối cache cũ.

Diagnostic trên cache cũ cho thấy `deep_sea_fishing` từng được gọi `BLUE_OCEAN`, dù một kết quả mạnh là sách ocean animals cho trẻ em chứ không phải deep-sea fishing. V2 hạ nó xuống `RESEARCH_MORE`. `cozy_haunted_bookshop` và `frog_adults` cũng không còn tự động qua gate cũ.

### 2. Dữ liệu niche đang stale

`python3 scripts/rank_niches.py` hiện trả `REFRESH_DATA` cho 40/40 niche theo freshness mặc định 30 ngày. Đây là hành vi đúng: cache cũ không được dùng để ra quyết định sản xuất hiện tại.

### 3. Economics sai công thức KDP hiện hành

Code cũ tính gần như `(list price - printing cost) × 60%`. Công thức KDP là:

```text
(royalty rate × list price) - printing cost
```

Amazon.com dùng 50% ở mức giá $9.98 trở xuống và 60% từ $9.99. Trim 8.5x8.5 và 8.5x11 đều là large trim; với B&W 24–110 trang tại Amazon.com, fixed printing cost hiện là $2.84.

### 4. Text giao cho image model làm chất lượng sách thô và dễ sai

Frontmatter cũ yêu cầu model viết cả paragraph, copyright và CTA vào ảnh. Đây là nguồn misspelling, text méo và copy generic. Luồng mới:

```text
imagegen artwork-only → exact copy trong plan.json → deterministic compositor → PNG/PDF
```

### 5. Hai đường tạo ảnh xung đột

Luồng active trước đây vẫn gọi `generate_images.py`/`generate_cover.py` qua `IMAGE_RENDERER`. Luồng Codex mới dùng built-in imagegen làm mặc định và chỉ giữ provider CLI làm fallback khi user chủ động chọn.

### 6. Checklist KDP thiếu hai policy quan trọng

- Artwork cover/interior do AI tạo phải được khai báo AI-generated trong KDP.
- Amazon nói coloring books nói chung không được xem là low-content; checklist cũ đánh dấu coloring book “always low-content”, là sai.

### 7. Workflow cũ bị phân mảnh

Repo có `kdp-niche-finder`, `niche-hunter`, `.agents`, `.claude`, và một số absolute path trỏ sang workspace cũ. `kdp-niche-finder` trong `.agents` giờ là canonical; `niche-hunter` được đánh dấu compatibility route để không chạy các path cũ.

## Production gate mới

Chỉ cho phép `GO` khi:

1. Amazon pull còn mới.
2. Có ít nhất 8 kết quả, ≥60% liên quan đúng search intent.
3. Có ≥5 BSR và ≥5 review observations dùng được.
4. Có demand depth từ nhiều seller, không phải một winner.
5. Median demand và median reviews đạt ngưỡng.
6. Giá bán chịu được printing cost, royalty tier và ads.
7. Có ít nhất 30 concept trang khác nhau thật sự.
8. Có product gap rõ so với top competitor.
9. Qua seasonality và IP/trademark check.
10. Chỉ sản xuất một flagship trước khi mở series.

## Content standard mới

Mỗi `plan.json` phải có:

- buyer promise;
- style bible;
- 4–6 section content arc;
- duplication matrix;
- exact frontmatter copy;
- text-free prompts cho cover/frontmatter;
- one-to-one mapping giữa page count, prompts và duplication rows.

Closing page phải nhắc đến trải nghiệm/đối tượng thật của sách. Có thể xin một review trung thực, nhưng không ép đánh giá tốt hoặc 5 sao.

## Những việc vẫn cần làm trước khi gọi pipeline “hoàn thiện”

1. Repull các niche muốn làm ngay và lưu evidence packet mới.
2. Thêm feedback loop từ Amazon Ads/CTR/conversion/sales vào quyết định series.
3. Có bước trademark/IP search chính thức trước production.
4. Chạy proof copy vật lý hoặc ít nhất KDP Print Previewer cho flagship.
5. Đo chất lượng built-in imagegen trên một cuốn thử 30–40 trang; nếu lỗi style drift cao, bổ sung reference-image strategy.
6. Dọn hoặc đồng bộ workflow `.claude` cũ nếu vẫn cần hỗ trợ Claude Code; pipeline canonical hiện là `.agents`/Codex.

## Nguồn KDP chính thức

- AI-generated disclosure và content quality: https://kdp.amazon.com/en_US/help/topic/G200672390
- Coloring books thường không phải low-content: https://kdp.amazon.com/en_US/help/topic/GGE5T76TWKA85DJM
- Paperback royalty 50%/60%: https://kdp.amazon.com/en_US/help/topic/G201834330
- Paperback printing cost: https://kdp.amazon.com/en_US/help/topic/G201834340
- Cover/spine/bleed: https://kdp.amazon.com/en_US/help/topic/G201953020
- Blank-page và formatting issues: https://kdp.amazon.com/en_US/help/topic/G201834260
