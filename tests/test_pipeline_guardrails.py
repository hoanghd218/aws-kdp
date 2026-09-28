from __future__ import annotations

import sys
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import kdp_config  # noqa: E402
import prepare_imagegen_asset  # noqa: E402
import rank_niches  # noqa: E402


class NicheGateTests(unittest.TestCase):
    def test_rejects_query_drift_and_audience_mismatch(self) -> None:
        query = "deep sea fishing coloring book"
        self.assertFalse(
            rank_niches.title_is_relevant(
                query,
                "Ocean Coloring Book for Kids: Learn 54 Sea Creatures",
            )
        )
        self.assertTrue(
            rank_niches.title_is_relevant(
                query,
                "Deep Sea Fishing Coloring Book for Adults",
            )
        )
        self.assertFalse(
            rank_niches.title_is_relevant(
                "frog coloring book for adults",
                "Cute Frog Coloring Book for Kids Ages 4-8",
            )
        )


class EconomicsTests(unittest.TestCase):
    def test_current_us_large_trim_rates(self) -> None:
        self.assertEqual(kdp_config.printing_cost_usd(76, page_size="8.5x8.5"), 2.84)
        self.assertEqual(kdp_config.paperback_royalty_rate_usd(9.98), 0.50)
        self.assertEqual(kdp_config.paperback_royalty_rate_usd(9.99), 0.60)
        self.assertEqual(
            kdp_config.royalty_per_sale_usd(9.99, 76, page_size="8.5x8.5"),
            3.154,
        )


class ImagePreparationTests(unittest.TestCase):
    def test_line_art_is_grayscale_and_exact_trim_pixels(self) -> None:
        source = Image.new("RGB", (1024, 1536), "white")
        prepared = prepare_imagegen_asset._prepare(source, (2550, 3300), "line-art")
        self.assertEqual(prepared.mode, "L")
        self.assertEqual(prepared.size, (2550, 3300))


if __name__ == "__main__":
    unittest.main()
