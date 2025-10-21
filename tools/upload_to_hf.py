import os
import pathlib
import sys
from huggingface_hub import HfApi

repo = os.environ.get("HF_REPO")
token = os.environ.get("HF_TOKEN")

if not repo:
    print("ERROR: HF_REPO env var is missing.", file=sys.stderr)
    sys.exit(1)
if not token:
    print("ERROR: HF_TOKEN env var is missing.", file=sys.stderr)
    sys.exit(1)

api = HfApi(token=token)
api.create_repo(repo_id=repo, repo_type="dataset", exist_ok=True)

files = [
    ("index/index.faiss", "index.faiss"),
    ("index/meta.json",   "meta.json"),
    ("index/dim.json",    "dim.json"),
]

any_uploaded = False
for src, dst in files:
    if pathlib.Path(src).exists():
        print(f"Uploading {src} -> {repo}:{dst}")
        api.upload_file(
            path_or_fileobj=src,
            path_in_repo=dst,
            repo_id=repo,
            repo_type="dataset",
        )
        any_uploaded = True
    else:
        print(f"SKIP: {src} not found.")
if not any_uploaded:
    print("WARNING: No artifacts found to upload (did the build step succeed?)")
else:
    print(f"Done. Artifacts now in https://huggingface.co/datasets/{repo}")
