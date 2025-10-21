import time, pathlib, trafilatura
from urllib.parse import urlparse

raw = pathlib.Path("data/raw"); raw.mkdir(parents=True, exist_ok=True)
seeds = [l.strip() for l in open("data/seeds.txt", encoding="utf-8")
         if l.strip() and not l.startswith("#")]

count = 0
for i, url in enumerate(seeds, 1):
    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded: continue
        md = trafilatura.extract(downloaded, include_links=True, output="markdown")
        if not md: continue
        fn = f"{i:04d}-{urlparse(url).netloc}.md"
        (raw / fn).write_text(f"# Source: {url}\n\n{md}", encoding="utf-8")
        count += 1
        time.sleep(0.5)  # be polite
    except Exception:
        pass
print("fetched:", count)
