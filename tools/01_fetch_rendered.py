import asyncio, time, pathlib, re
from urllib.parse import urlparse
import trafilatura
from playwright.async_api import async_playwright

RAW = pathlib.Path("data/raw"); RAW.mkdir(parents=True, exist_ok=True)

def read_seeds(path="data/seeds.txt"):
    p = pathlib.Path(path)
    if not p.exists(): return []
    lines = [l.strip() for l in p.read_text(encoding="utf-8").splitlines()]
    return [l for l in lines if l and not l.startswith("#") and l.startswith("http")]

COOKIE_BUTTON_SELECTORS = [
    'button#onetrust-accept-btn-handler',
    'button#truste-consent-button',
    'button[aria-label*="Accept"]',
    'button:has-text("Accept All")',
    'button:has-text("Accept all")',
    'button:has-text("I accept")',
    'button:has-text("Allow all cookies")',
    'text=Accept',
    'text=Agree',
]
MAIN_WAIT_SELECTORS = ['main','article','[role="main"]','.article','.content','.applicationShell']
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36 sap-basis-bot/1.0"

async def fetch_one(page, url, idx):
    host = urlparse(url).netloc.replace(":", "-")
    base = f"{idx:04d}-{host}"
    await page.set_user_agent(UA)
    await page.goto(url, wait_until="domcontentloaded", timeout=60000)
    for sel in COOKIE_BUTTON_SELECTORS:
        try:
            btn = await page.wait_for_selector(sel, timeout=2000)
            if btn:
                await btn.click()
                await page.wait_for_timeout(300)
                break
        except Exception:
            pass
    for sel in MAIN_WAIT_SELECTORS:
        try:
            await page.wait_for_selector(sel, timeout=4000); break
        except Exception: continue
    for y in (400, 1000, 2000):
        try:
            await page.evaluate(f"window.scrollTo(0,{y});"); await page.wait_for_timeout(200)
        except Exception:
            pass
    html = await page.content()
    (RAW / f"{base}.html").write_text(html, encoding="utf-8", errors="ignore")
    md = None
    for recall in (False, True):
        try:
            md = trafilatura.extract(html, include_links=True, output="markdown", favor_recall=recall, url=url)
            if md and len(md.strip()) > 200: break
        except Exception: md = None
    if not md:
        (RAW / f"{base}.md").write_text(f"# Source: {url}\n\n*(extraction failed — add a short summary here)*", encoding="utf-8")
        return False
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    (RAW / f"{base}.md").write_text(f"# Source: {url}\n\n{md}", encoding="utf-8")
    return True

async def main():
    seeds = read_seeds()
    if not seeds:
        print("No URLs in data/seeds.txt"); return
    ok = 0
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width":1280,"height":2000})
        page = await context.new_page()
        for i, url in enumerate(seeds, 1):
            try:
                if await fetch_one(page, url, i): ok += 1
                await page.wait_for_timeout(250)
            except Exception:
                pass
        await context.close(); await browser.close()
    print(f"Fetched OK: {ok} / {len(seeds)}")

if __name__ == "__main__":
    asyncio.run(main())
