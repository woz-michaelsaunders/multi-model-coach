# Corporate Helper

A Python-based corporate helper application with a modern GUI built using PySide6.

## Requirements

- Python 3.11 or higher
- PySide6

## Setup

1. Create a virtual environment:
```powershell
python -m venv venv
.\venv\Scripts\activate
```

2. Install dependencies:
```powershell
pip install -r requirements.txt
```

## Running the Application

```powershell
python src/main.py
```

## Offline model delivery (GitHub Release / release asset)

If your client cannot download models from Hugging Face, a straightforward option is to package the model as a release asset and upload it to a GitHub Release. The client can then download the release asset and extract the model into a local folder.

Steps to prepare a model artifact (on the machine that can access Hugging Face):

1. Download the model to disk (example using `transformers` or `huggingface_hub`):

```python
from huggingface_hub import snapshot_download
snapshot_download(repo_id="facebook/bart-large-cnn", cache_dir="/tmp/bart-model")
```

2. Package the model directory into a compressed archive (this repo includes a helper):

```powershell
# Example: package model folder into a tar.gz
python scripts/package_model.py --model-dir C:\path\to\bart-model --out C:\path\to\release-bart.tar.gz
```

3. Create a GitHub Release and upload `release-bart.tar.gz` as a release asset. You can use the web UI or GitHub CLI:

```powershell
# create a release and upload the asset (from project root)
gh release create v1.0.0 --title "Model release v1.0.0" --notes "BART model release" --repo <owner>/multi-model-coach
gh release upload v1.0.0 C:\path\to\release-bart.tar.gz --repo <owner>/multi-model-coach
```

Client installation instructions (client machine with no HF access):

1. Download release asset from the GitHub Release page and extract it to a folder, e.g. `C:\models\bart-large-cnn`.

2. In your app, configure the summarizer to use the local model path. You can set an environment variable or pass the path when creating the summarizer.

Example (pass model path in code):

```python
from jira_summarizer import JiraStorySummarizer

# point to the folder you extracted from the release asset
model_path = r"C:\models\bart-large-cnn"
summarizer = JiraStorySummarizer(model_path=model_path)
```

Or set an env var and the app can read it (we can wire this in if you'd like):

```powershell
# Windows PowerShell
setx MODEL_PATH "C:\models\bart-large-cnn"
```

Notes and caveats

- Model archives are large (hundreds of MB). Use a fast upload method. GitHub release assets are a convenient distribution mechanism.
- If you want tighter control or programmatic downloads with expiry, hosting the model on S3 and issuing presigned URLs is recommended.
- If you want me to automate creation of the GitHub Release and upload from this repo (I can add a helper that runs `gh release upload`), say so and I will add it.
