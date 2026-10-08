"""
Generate per-page PNG snapshots of the Final Program HTML using Playwright + Pillow.
Outputs: final_program_svg/ICACCESS2026_Final_Program_Page01.svg, Page02.svg, ...
(Files are PNGs saved with .svg extension to match the existing naming convention.)
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
import io

ROOT    = Path(__file__).parent
HTML    = ROOT / "ICACCESS2026_Final_Program.html"
OUT_DIR = ROOT / "final_program_svg"
OUT_DIR.mkdir(exist_ok=True)

# A4 at 96 dpi: 794 x 1123 px
PAGE_W = 794
PAGE_H = 1123

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": PAGE_W, "height": PAGE_H})
    page.goto(HTML.resolve().as_uri(), wait_until="networkidle")
    page.evaluate("document.fonts.ready")

    # Take a full-page screenshot into memory
    print("Capturing full page screenshot...")
    png_bytes = page.screenshot(full_page=True, type="png")
    browser.close()

full_img = Image.open(io.BytesIO(png_bytes))
total_w, total_h = full_img.size
print(f"Full image: {total_w}x{total_h}px")

n_pages = max(1, -(-total_h // PAGE_H))
print(f"Slicing into {n_pages} pages...")

for i in range(n_pages):
    y0 = i * PAGE_H
    y1 = min(y0 + PAGE_H, total_h)
    if y0 >= total_h:
        break

    slice_img = full_img.crop((0, y0, total_w, y1))
    out = OUT_DIR / f"ICACCESS2026_Final_Program_Page{i+1:02d}.svg"
    slice_img.save(str(out), format="PNG")
    print(f"  Saved {out.name}")

print("Done.")
