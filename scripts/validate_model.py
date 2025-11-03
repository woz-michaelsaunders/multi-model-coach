"""
Validate a local Hugging Face model folder for presence of required files.

Usage:
  python scripts/validate_model.py --model-dir /path/to/bart-large-cnn

Checks for files typically required to load a Transformers model: config.json,
tokenizer files, and either pytorch_model.bin or tf_model.h5.
"""
import argparse
from pathlib import Path
import sys


def check_model_dir(model_dir: Path) -> bool:
    if not model_dir.is_dir():
        print(f"Model directory not found: {model_dir}")
        return False

    required = ["config.json"]
    optional_model_files = ["pytorch_model.bin", "tf_model.h5", "flax_model.msgpack"]

    files = {p.name for p in model_dir.rglob('*') if p.is_file()}

    ok = True
    for r in required:
        if r not in files:
            print(f"Missing required file: {r}")
            ok = False

    if not any(x in files for x in optional_model_files):
        print("Missing model weights file (pytorch_model.bin / tf_model.h5 / flax_model.msgpack)")
        ok = False

    # Tokenizer: check for at least one tokenizer file
    tokenizer_indicators = ["tokenizer.json", "vocab.txt", "merges.txt", "tokenizer_config.json", "spiece.model"]
    if not any(x in files for x in tokenizer_indicators):
        print("Warning: no tokenizer files found (tokenizer.json / vocab.txt / merges.txt / spiece.model)")

    if ok:
        print("Model directory looks valid.")
    else:
        print("Model directory is missing required files.")

    return ok


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", required=True, type=Path)
    args = parser.parse_args()
    ok = check_model_dir(args.model_dir)
    sys.exit(0 if ok else 2)


if __name__ == '__main__':
    main()
