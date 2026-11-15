#!/usr/bin/env python3
"""KDP pre-flight PDF checker.

Validates interior or cover PDFs against KDP's manual-review requirements
before upload. Exits non-zero if any CRITICAL check fails.

Dependencies: pypdf (pure Python, already common). Falls back gracefully
if pypdf isn't installed — reports skipped checks instead of crashing.

Usage:
  python3 pdf_qc.py --pdf path.pdf --trim 8.5x11
  python3 pdf_qc.py --pdf cover.pdf --cover --expected-width 17.37 --expected-height 11.25 --expected-bleed 0.125
  python3 pdf_qc.py --pdf interior.pdf --trim 8.5x11 --require-even-pages --min-line-weight 0.75pt
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from pypdf import PdfReader  # type: ignore
    HAS_PYPDF = True
except Exception:
    HAS_PYPDF = False

POINTS_PER_INCH = 72.0
TOLERANCE_IN = 0.01

TRIM_SIZES_IN = {
    "8.5x11":  (8.5, 11.0),
    "8.5x8.5": (8.5, 8.5),
    "6x9":     (6.0, 9.0),
    "7x10":    (7.0, 10.0),
    "8x10":    (8.0, 10.0),
}


class Report:
    def __init__(self) -> None:
        self.critical: list[str] = []
        self.warnings: list[str] = []
        self.notes: list[str] = []
        self.skipped: list[str] = []

    def crit(self, msg: str) -> None:
        self.critical.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def note(self, msg: str) -> None:
        self.notes.append(msg)

    def skip(self, msg: str) -> None:
        self.skipped.append(msg)

    @property
    def verdict(self) -> str:
        return "NO_GO" if self.critical else "GO"

    def to_dict(self) -> dict:
        return {
            "verdict": self.verdict,
            "critical_issues": self.critical,
            "warnings": self.warnings,
            "notes": self.notes,
            "skipped": self.skipped,
        }


def _image_xobjects(page) -> list:
    """Return direct image resources without decoding large image streams."""
    resources = page.get("/Resources") or {}
    objects = resources.get("/XObject") or {}
    return [ref.get_object() for ref in objects.values()
            if ref.get_object().get("/Subtype") == "/Image"]


def _check_flat_pdf(reader: "PdfReader", report: Report) -> None:
    if reader.is_encrypted:
        report.crit("PDF is encrypted")
    if reader.trailer.get("/Root", {}).get("/AcroForm"):
        report.crit("PDF contains form fields")
    annotated = [i + 1 for i, page in enumerate(reader.pages) if page.get("/Annots")]
    if annotated:
        report.crit(f"PDF contains annotations on page(s): {annotated[:8]}")


def _check_coloring_layout(reader: "PdfReader", plan_path: Path, report: Report,
                           verify_image_order: bool = False) -> None:
    try:
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        report.crit(f"Cannot read plan for layout validation: {exc}")
        return
    count = plan.get("page_count") or len(plan.get("page_prompts", []))
    if not isinstance(count, int) or count <= 0:
        report.crit("Plan has no valid coloring page count")
        return
    order = plan.get("page_order")
    if order is not None and (not isinstance(order, list) or
                              len(order) != count or
                              any(type(number) is not int for number in order) or
                              sorted(order) != list(range(1, count + 1))):
        report.crit("Plan page_order must contain each coloring page number once")
    expected_pages = 4 + 2 * count + 1
    if len(reader.pages) != expected_pages:
        report.crit(f"Interior has {len(reader.pages)} pages; plan/layout expects {expected_pages}")
        return
    expected_front = [True, True, True, plan.get("audience") != "adults"]
    for index, should_have_image in enumerate(expected_front):
        if bool(_image_xobjects(reader.pages[index])) != should_have_image:
            report.crit(f"Front-matter page {index + 1} has incorrect image/blank layout")
    bad_picture = []
    bad_back = []
    for index in range(count):
        picture_page = 4 + 2 * index
        back_page = picture_page + 1
        if not _image_xobjects(reader.pages[picture_page]):
            bad_picture.append(picture_page + 1)
        if _image_xobjects(reader.pages[back_page]) or reader.pages[back_page].extract_text().strip():
            bad_back.append(back_page + 1)
    if bad_picture:
        report.crit(f"Coloring artwork missing from page(s): {bad_picture[:10]}")
    if bad_back:
        report.crit(f"Single-sided blank backs contain content on page(s): {bad_back[:10]}")
    if not _image_xobjects(reader.pages[-1]):
        report.crit("Closing page is missing its artwork")
    if not bad_picture and not bad_back:
        report.note(f"Verified {count} coloring pages on right-hand pages with blank backs")
        report.note("Closing page is the final manuscript page")
    if verify_image_order and not bad_picture:
        try:
            from PIL import Image
            order_to_check = order or list(range(1, count + 1))
            mismatches = []
            for index, source_number in enumerate(order_to_check):
                path = plan_path.parent / "images" / f"page_{source_number:02d}.png"
                image_obj = _image_xobjects(reader.pages[4 + 2 * index])[0]
                mode = "L" if image_obj.get("/ColorSpace") == "/DeviceGray" else "RGB"
                with Image.open(path) as source:
                    same = (source.size == (int(image_obj["/Width"]), int(image_obj["/Height"]))
                            and source.convert(mode).tobytes() == image_obj.get_data())
                if not same:
                    mismatches.append((4 + 2 * index + 1, source_number))
            if mismatches:
                report.crit(f"PDF artwork does not match plan page_order: {mismatches[:8]}")
            else:
                report.note(f"Verified exact artwork order for all {count} coloring pages")
        except (OSError, KeyError, ValueError, ImportError, IndexError) as exc:
            report.crit(f"Cannot verify PDF artwork order: {exc}")


def _check_barcode_zone(cover_png: Path, plan_path: Path, report: Report) -> None:
    try:
        from PIL import Image
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        trim_w, _ = TRIM_SIZES_IN[plan["page_size"]]
        with Image.open(cover_png) as raw:
            dpi = raw.info.get("dpi", (300, 300))[0]
            image = raw.convert("RGB")
        bleed = round(0.125 * dpi)
        safe = round(0.375 * dpi)
        width = round(2.0 * dpi)
        height = round(1.2 * dpi)
        left = bleed + round(trim_w * dpi) - safe - width
        top = image.height - bleed - safe - height
        if left < 0 or top < 0:
            report.crit("Barcode zone falls outside the cover")
            return
        pixels = image.crop((left + 8, top + 8, left + width - 8, top + height - 8))
        white = sum(all(channel >= 248 for channel in pixel) for pixel in pixels.getdata())
        white_pct = 100 * white / (pixels.width * pixels.height)
        report.note(f"Barcode zone: {white_pct:.1f}% white in 2.0 × 1.2 inch box")
        if white_pct < 98:
            report.crit("Barcode zone is not clear white")
    except (OSError, KeyError, ValueError, ImportError) as exc:
        report.crit(f"Cannot validate barcode zone: {exc}")


def _page_dims_inches(reader: "PdfReader", page_index: int) -> tuple[float, float]:
    page = reader.pages[page_index]
    box = page.mediabox
    width_pt = float(box.width)
    height_pt = float(box.height)
    return (width_pt / POINTS_PER_INCH, height_pt / POINTS_PER_INCH)


def check_interior(args, report: Report) -> None:
    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        report.crit(f"PDF not found: {pdf_path}")
        return
    if not HAS_PYPDF:
        report.crit("pypdf is required for PDF validation (`pip install pypdf`)")
        return

    try:
        reader = PdfReader(str(pdf_path))
    except Exception as exc:
        report.crit(f"Cannot open PDF: {exc}")
        return
    n_pages = len(reader.pages)
    report.note(f"Page count: {n_pages}")
    _check_flat_pdf(reader, report)

    if args.require_even_pages and n_pages % 2 != 0:
        report.note(f"KDP rounds the {n_pages}-page manuscript up to {n_pages + 1} pages for printing")

    if args.trim:
        if args.trim not in TRIM_SIZES_IN:
            report.crit(f"Unknown trim: {args.trim}")
        else:
            expected_w, expected_h = TRIM_SIZES_IN[args.trim]
            for i in range(n_pages):
                w, h = _page_dims_inches(reader, i)
                if abs(w - expected_w) > TOLERANCE_IN or abs(h - expected_h) > TOLERANCE_IN:
                    report.crit(
                        f"Page {i + 1} is {w:.3f}×{h:.3f}\" — expected {expected_w}×{expected_h}\""
                    )
                    break
            else:
                report.note(f"All {n_pages} pages match trim {args.trim}")

    mb = pdf_path.stat().st_size / (1024 * 1024)
    report.note(f"File size: {mb:.1f} MB")
    if mb > 650:
        report.crit(f"File size {mb:.1f} MB exceeds KDP limit 650 MB")
    elif mb > 400:
        report.warn(f"File size {mb:.1f} MB is large — consider optimizing")

    if args.min_line_weight:
        report.skip(f"Line-weight check ({args.min_line_weight}) — delegate to kdp-image-reviewer")
    if args.plan:
        _check_coloring_layout(reader, Path(args.plan), report, args.verify_image_order)


def check_cover(args, report: Report) -> None:
    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        report.crit(f"PDF not found: {pdf_path}")
        return
    if not HAS_PYPDF:
        report.crit("pypdf is required for PDF validation (`pip install pypdf`)")
        return

    try:
        reader = PdfReader(str(pdf_path))
    except Exception as exc:
        report.crit(f"Cannot open PDF: {exc}")
        return
    _check_flat_pdf(reader, report)
    n_pages = len(reader.pages)
    if n_pages != 1:
        report.crit(f"Cover PDF must be exactly 1 page, got {n_pages}")
        return

    w, h = _page_dims_inches(reader, 0)
    report.note(f"Cover dimensions: {w:.3f}\" × {h:.3f}\"")

    if args.expected_width and abs(w - args.expected_width) > TOLERANCE_IN:
        report.crit(
            f"Cover width {w:.3f}\" ≠ expected {args.expected_width}\" (Δ {w - args.expected_width:+.3f}\")"
        )
    if args.expected_height and abs(h - args.expected_height) > TOLERANCE_IN:
        report.crit(
            f"Cover height {h:.3f}\" ≠ expected {args.expected_height}\" (Δ {h - args.expected_height:+.3f}\")"
        )

    mb = pdf_path.stat().st_size / (1024 * 1024)
    report.note(f"File size: {mb:.1f} MB")
    if mb > 650:
        report.crit(f"File size {mb:.1f} MB exceeds KDP limit 650 MB")
    images = _image_xobjects(reader.pages[0])
    if len(images) == 1:
        image = images[0]
        dpi_x = int(image.get("/Width", 0)) / w
        dpi_y = int(image.get("/Height", 0)) / h
        report.note(f"Embedded cover image: {dpi_x:.1f} × {dpi_y:.1f} DPI")
        if min(dpi_x, dpi_y) < 299:
            report.crit("Embedded cover image is below 300 DPI")
    else:
        report.skip("Cover raster DPI needs review (not a single flattened image)")
    if reader.pages[0].get("/Resources", {}).get("/Font"):
        report.warn("Cover PDF contains font resources; verify all fonts are embedded")
    cover_png = pdf_path.with_suffix(".png")
    if cover_png.exists() and args.plan:
        _check_barcode_zone(cover_png, Path(args.plan), report)
    else:
        report.skip("Barcode zone check requires sibling cover.png and --plan")


def main() -> int:
    parser = argparse.ArgumentParser(description="KDP pre-flight PDF checker")
    parser.add_argument("--pdf", required=True, help="Path to PDF")
    parser.add_argument("--plan", help="Plan JSON for coloring-page layout and barcode validation")
    parser.add_argument("--verify-image-order", action="store_true",
                        help="Compare each embedded coloring image with plan.page_order sources")
    parser.add_argument("--trim", help="Expected trim size (e.g. 8.5x11)")
    parser.add_argument("--require-even-pages", action="store_true")
    parser.add_argument("--min-line-weight", help="Minimum line weight (e.g. 0.75pt)")
    parser.add_argument("--cover", action="store_true", help="Treat as cover PDF")
    parser.add_argument("--expected-width", type=float)
    parser.add_argument("--expected-height", type=float)
    parser.add_argument("--expected-bleed", type=float, default=0.125)
    parser.add_argument("--json", action="store_true", help="Emit JSON only")
    args = parser.parse_args()

    report = Report()
    if args.cover:
        check_cover(args, report)
    else:
        check_interior(args, report)

    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(f"📋 PDF QC — {args.pdf}")
        print(f"   Verdict: {'✅ GO' if report.verdict == 'GO' else '🛑 NO_GO'}")
        if report.critical:
            print("\n🛑 CRITICAL:")
            for m in report.critical:
                print(f"  • {m}")
        if report.warnings:
            print("\n⚠  WARNINGS:")
            for m in report.warnings:
                print(f"  • {m}")
        if report.notes:
            print("\n• NOTES:")
            for m in report.notes:
                print(f"  • {m}")
        if report.skipped:
            print("\n… SKIPPED:")
            for m in report.skipped:
                print(f"  • {m}")

    return 1 if report.verdict == "NO_GO" else 0


if __name__ == "__main__":
    sys.exit(main())
