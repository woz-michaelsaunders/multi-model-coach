"""
Simple helper to package a local Hugging Face model folder into a compressed archive
suitable for attaching to a GitHub Release.

Usage:
    python scripts/package_model.py --model-dir /path/to/bart-large-cnn --out release-model.tar.gz

The created archive can then be uploaded to a GitHub Release (via web UI or `gh release upload`).
"""
import argparse
import tarfile
from pathlib import Path


def package_model(model_dir: Path, out_path: Path):
    if not model_dir.is_dir():
        raise SystemExit(f"Model directory not found: {model_dir}")
    print(f"Packaging model directory {model_dir} -> {out_path}")
    with tarfile.open(out_path, "w:gz") as tar:
        # add the model directory contents, not the absolute path
        for p in model_dir.rglob("*"):
            arcname = p.relative_to(model_dir.parent)
            tar.add(p, arcname=arcname)
    print("Packaging complete.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", required=True, type=Path, help="Local model folder to package")
    parser.add_argument("--out", required=True, type=Path, help="Output tar.gz file")
    args = parser.parse_args()
    package_model(args.model_dir, args.out)
