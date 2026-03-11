#!/usr/bin/env python3
"""
Generate a foldable parallel-text HTML page from a JSON source.

Usage:
  python generate_parallel_html.py parallel-texts.json template.html parallel-texts.html
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

PLACEHOLDER = "__DATA__"


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def normalize_sentences(
    items: List[Dict[str, Any]], default_section: str, default_lang: str
) -> List[Dict[str, Any]]:
    """Normalize a flat list of sentences into sectioned data for the template."""
    sections: Dict[str, List[Dict[str, Any]]] = {}

    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Entry {index} is not an object: {item!r}")

        if "original" not in item:
            raise ValueError(f"Entry {index} is missing 'original': {item!r}")

        original = item["original"]
        translations: Dict[str, Any] = {}

        if "translations" in item:
            if isinstance(item["translations"], dict):
                translations.update(item["translations"])
            elif item["translations"] is not None:
                raise ValueError(f"'translations' on entry {index} must be an object if provided.")

        if "translation" in item:
            raw_translation = item["translation"]
            if isinstance(raw_translation, str):
                translations.setdefault(default_lang, raw_translation)
            elif isinstance(raw_translation, dict):
                translations.update(raw_translation)
            elif raw_translation is not None:
                raise ValueError(f"'translation' on entry {index} must be a string or object.")

        section_title = item.get("section") or default_section
        sections.setdefault(section_title, []).append(
            {
                "original": original,
                "translations": translations,
                "root": bool(item.get("root", False)),
            }
        )

    return [
        {"sectionTitle": section_name, "sentences": sentences}
        for section_name, sentences in sections.items()
    ]


def normalize_data(raw_data: Any, default_section: str, default_lang: str) -> List[Dict[str, Any]]:
    """Coerce various JSON shapes into the array of sections expected by the template."""
    if isinstance(raw_data, list):
        # Already in sectioned shape?
        if all(isinstance(item, dict) and "sectionTitle" in item and "sentences" in item for item in raw_data):
            normalized_sections = []
            for section in raw_data:
                section_title = section.get("sectionTitle", default_section)
                sentences = []
                for sentence in section.get("sentences", []):
                    if not isinstance(sentence, dict):
                        raise ValueError(f"Sentence must be an object: {sentence!r}")
                    sentences.append(
                        {
                            "original": sentence.get("original", ""),
                            "translations": sentence.get("translations", {}),
                            "root": bool(sentence.get("root", False)),
                        }
                    )
                normalized_sections.append({"sectionTitle": section_title, "sentences": sentences})
            return normalized_sections

        # Treat as a flat list of sentences.
        return normalize_sentences(raw_data, default_section, default_lang)

    if isinstance(raw_data, dict) and "sections" in raw_data:
        return normalize_data(raw_data["sections"], default_section, default_lang)

    raise ValueError("Unsupported JSON shape. Expected a list of sentences or sections.")


def render_html(template_path: Path, output_path: Path, data: List[Dict[str, Any]]) -> None:
    template = template_path.read_text(encoding="utf-8")
    if PLACEHOLDER not in template:
        raise ValueError(
            f"Placeholder '{PLACEHOLDER}' not found in template {template_path}"
        )

    rendered = template.replace(PLACEHOLDER, json.dumps(data, ensure_ascii=False, indent=2))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a parallel-text HTML page from a JSON file."
    )
    parser.add_argument("json_path", type=Path, help="Path to the JSON input file.")
    parser.add_argument("template_path", type=Path, help="HTML template containing the __DATA__ placeholder.")
    parser.add_argument("output_path", type=Path, help="Where to write the generated HTML.")
    parser.add_argument(
        "--default-section",
        default="Text",
        help="Section title to use when the JSON is a flat list (default: %(default)s).",
    )
    parser.add_argument(
        "--default-lang",
        default="en",
        help="Language code used when the JSON uses a single 'translation' string (default: %(default)s).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raw = load_json(args.json_path)
    normalized = normalize_data(raw, args.default_section, args.default_lang)
    render_html(args.template_path, args.output_path, normalized)


if __name__ == "__main__":
    main()
