import re, json
from pathlib import Path

raw = Path("data/raw")
idx = Path("index"); idx.mkdir(parents=True, exist_ok=True)

def chunk(md, url, title, max_chars=1200, overlap=150):
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    out, i = [], 0
    while i < len(md):
        piece = md[i:i+max_chars]
        end = piece.rfind(". ")
        if end > 300: piece = piece[:end+1]
        out.append({"url": url, "title": title, "text": piece.strip()})
        i += max(len(piece)-overlap, 1)
    return out

all_chunks = []
for p in sorted(raw.glob("*.md")):
    md = p.read_text(encoding="utf-8")
    lines = md.splitlines()
    if not lines: continue
    url = lines[0].replace("# Source:", "").strip()
    # heuristic: first markdown heading after source acts as title
    title = next((l.strip("# ").strip() for l in lines[1:8] if l.startswith("#")), url)
    body = "\n".join(lines[1:])  # everything but source line
    # (Optional) Keep summaries short: If long, you can truncate body here.
    all_chunks += chunk(body, url, title)

Path("index/meta.json").write_text(json.dumps(all_chunks, ensure_ascii=False), encoding="utf-8")
print("chunks:", len(all_chunks))
