"""
Helper to create a GitHub Release and upload a model archive using the GitHub CLI (`gh`).

Requirements:
 - GitHub CLI (`gh`) installed and authenticated (run `gh auth login` prior)

Usage:
  python scripts/gh_release_upload.py --tag v1.0.0 --title "Model v1.0.0" --notes "BART model" --asset /path/to/release-bart.tar.gz

This will run `gh release create` and `gh release upload` for the current repository.
"""
import argparse
import shutil
import subprocess
import sys


def ensure_gh():
    if shutil.which("gh") is None:
        print("Error: GitHub CLI 'gh' not found in PATH. Install it and authenticate (gh auth login).")
        sys.exit(1)


def run(cmd):
    print('> ' + ' '.join(cmd))
    subprocess.check_call(cmd)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True, help="Release tag (e.g. v1.0.0)")
    parser.add_argument("--title", required=True, help="Release title")
    parser.add_argument("--notes", default="", help="Release notes")
    parser.add_argument("--asset", required=True, help="Path to asset file to upload")
    parser.add_argument("--repo", default=None, help="Optional repo (owner/repo). If omitted, uses current git remote")
    args = parser.parse_args()

    ensure_gh()

    create_cmd = ["gh", "release", "create", args.tag, "-t", args.title, "-n", args.notes]
    if args.repo:
        create_cmd += ["--repo", args.repo]

    # Create release (will fail if exists)
    try:
        run(create_cmd)
    except subprocess.CalledProcessError:
        print("Release creation failed (maybe it already exists). Continuing to upload asset...")

    upload_cmd = ["gh", "release", "upload", args.tag, args.asset]
    if args.repo:
        upload_cmd += ["--repo", args.repo]

    run(upload_cmd)


if __name__ == '__main__':
    main()
