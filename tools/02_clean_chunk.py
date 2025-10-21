import re, json
from pathlib import Path

RAW_DIR = Path("data/raw")
IDX_DIR = Path("index"); IDX_DIR.mkdir(parents=True, exist_ok=True)

def chunk(text, url, title, max_chars=1200, overlap=150):
    text = re.sub(r"\n{3,}", "\n\n", text or "").strip()
    if not text:
        # Minimal placeholder so the pipeline keeps working
        text = f"{title or 'SAP Basis'} — See the source for details. This is a short placeholder summary to maintain index continuity."
    out, i = [], 0
    n = len(text)
    if n <= max_chars:
        out.append({"url": url, "title": title, "text": text})
        return out
    while i < n:
        piece = text[i:i+max_chars]
        end = piece.rfind(". ")
        if end > 300:
            piece = piece[:end+1]
        out.append({"url": url, "title": title, "text": piece.strip()})
        i += max(len(piece)-overlap, 1)
    return out

all_chunks = []
md_files = sorted(RAW_DIR.glob("*.md"))

for p in md_files:
    md = p.read_text(encoding="utf-8")
    lines = md.splitlines()
    if not lines:
        continue
    url = lines[0].replace("# Source:", "").strip()
    title = next((l.strip("# ").strip() for l in lines[1:8] if l.startswith("#")), url)
    body = "\n".join(lines[1:]).strip()
    # If body is just the “extraction failed” line, we still create a tiny chunk
    all_chunks += chunk(body, url, title)

Path("index/meta.json").write_text(json.dumps(all_chunks, ensure_ascii=False), encoding="utf-8")
print("md files seen:", len(md_files))
print("chunks:", len(all_chunks))
