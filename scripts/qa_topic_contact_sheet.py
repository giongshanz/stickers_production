#!/usr/bin/env python3
"""Render light and dark contact sheets from existing masters for visual review."""

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]


def render(topic_slug: str, output_dir: Path) -> None:
    plan = json.loads((ROOT / "plan" / "sticker-plan.json").read_text(encoding="utf-8"))
    topic = next(topic for topic in plan["topics"] if topic["slug"] == topic_slug)
    output_dir.mkdir(parents=True, exist_ok=True)
    font = ImageFont.load_default(size=18)
    for mode, background in (("light", (245, 240, 231, 255)), ("dark", (44, 50, 62, 255))):
        sheet = Image.new("RGBA", (1280, 720), background)
        draw = ImageDraw.Draw(sheet)
        for index, asset_id in enumerate(topic["asset_ids"]):
            file = ROOT / "masters" / f"{asset_id}.png"
            if not file.is_file():
                continue
            row, col = divmod(index, 4)
            cell_x, cell_y = col * 320, row * 360
            with Image.open(file) as source:
                image = source.convert("RGBA")
            image.thumbnail((280, 285), Image.Resampling.LANCZOS)
            x = cell_x + (320 - image.width) // 2
            y = cell_y + 12 + (285 - image.height) // 2
            sheet.alpha_composite(image, (x, y))
            label = asset_id.replace("-", " ")
            bounds = draw.textbbox((0, 0), label, font=font)
            draw.text(
                (cell_x + (320 - bounds[2] + bounds[0]) // 2, cell_y + 315),
                label,
                fill=(25, 28, 34, 255) if mode == "light" else (245, 242, 235, 255),
                font=font,
            )
        sheet.convert("RGB").save(output_dir / f"{topic_slug}-{mode}.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("topic_slug")
    parser.add_argument("output_dir")
    args = parser.parse_args()
    render(args.topic_slug, ROOT / args.output_dir)
