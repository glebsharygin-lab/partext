#!/usr/bin/env python3
"""
Publish script: convert all JSON files in jsons/ to HTML using generate_parallel_html.py
"""
import sys
import shutil
from pathlib import Path
from generate_parallel_html import load_json, normalize_data, render_html


def publish(json_dir: Path, output_dir: Path, template_path: Path = None) -> None:
    """
    Process all JSON files in json_dir and generate HTML in output_dir.
    
    Args:
        json_dir: Directory containing JSON files to process
        output_dir: Directory where HTML files will be written
        template_path: Path to HTML template (defaults to templates/template.html)
    """
    json_dir = Path(json_dir)
    output_dir = Path(output_dir)
    
    if template_path is None:
        template_path = Path(__file__).parent.parent / "templates" / "template.html"
    else:
        template_path = Path(template_path)
    
    if not json_dir.exists():
        print(f"Error: JSON directory does not exist: {json_dir}")
        sys.exit(1)
    
    if not template_path.exists():
        print(f"Error: Template file does not exist: {template_path}")
        sys.exit(1)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy styles.css to output directory
    styles_src = Path(__file__).parent.parent / "templates" / "styles.css"
    if styles_src.exists():
        styles_dst = output_dir / "styles.css"
        shutil.copy2(styles_src, styles_dst)
        print(f"Copied styles to {styles_dst}")
    
    json_files = sorted(json_dir.glob("*.json"))
    
    if not json_files:
        print(f"Warning: No JSON files found in {json_dir}")
        return
    
    print(f"Processing {len(json_files)} JSON file(s)...")
    
    for json_file in json_files:
        try:
            output_file = output_dir / (json_file.stem + ".html")
            
            print(f"  {json_file.name} → {output_file}")
            
            raw = load_json(json_file)
            normalized = normalize_data(raw, default_section="Text", default_lang="en")
            render_html(template_path, output_file, normalized)
            
        except Exception as e:
            print(f"  ERROR processing {json_file.name}: {e}")
            sys.exit(1)
    
    print(f"✓ Published {len(json_files)} file(s) to {output_dir}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python publish.py <json_dir> <output_dir> [template_path]")
        sys.exit(1)
    
    json_dir = sys.argv[1]
    output_dir = sys.argv[2]
    template_path = sys.argv[3] if len(sys.argv) > 3 else None
    
    publish(json_dir, output_dir, template_path)