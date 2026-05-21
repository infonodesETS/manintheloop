"""
Convert report1.md → report1.pdf via HTML intermediate + Chromium headless.
Run from refactoringDB/: python3 reports/generate_pdf.py
"""

import subprocess
import sys
import re
import base64
from pathlib import Path
import markdown

REPORTS = Path(__file__).parent
CHARTS = REPORTS / "charts"
MD_FILE = REPORTS / "report1.md"
HTML_FILE = REPORTS / "_report1_tmp.html"
PDF_FILE = REPORTS / "report1.pdf"

# --- Read and parse markdown ---
md_text = MD_FILE.read_text()

# Inline images as base64 so chromium doesn't need file:// quirks
def inline_images(md_src):
    def replace(m):
        alt = m.group(1)
        path_str = m.group(2)
        # resolve relative to reports/
        img_path = REPORTS / path_str
        if img_path.exists():
            ext = img_path.suffix.lstrip('.').lower()
            mime = 'image/png' if ext == 'png' else f'image/{ext}'
            b64 = base64.b64encode(img_path.read_bytes()).decode()
            return f'![{alt}](data:{mime};base64,{b64})'
        return m.group(0)
    return re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace, md_src)

md_text = inline_images(md_text)

# Convert markdown to HTML
md_engine = markdown.Markdown(extensions=['tables', 'fenced_code'])
body_html = md_engine.convert(md_text)

# --- Build full HTML ---
CSS = """
  @page {
    margin: 20mm 18mm 22mm 18mm;
    size: A4;
  }
  * { box-sizing: border-box; }
  body {
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.65;
    color: #1a1a1a;
    background: #ffffff;
    max-width: 170mm;
    margin: 0 auto;
  }
  h1 {
    font-size: 20pt;
    font-weight: 800;
    color: #0d1117;
    border-bottom: 3px solid #2a7d7d;
    padding-bottom: 6px;
    margin-top: 0;
    margin-bottom: 4px;
  }
  h2 {
    font-size: 15pt;
    font-weight: 700;
    color: #1a5c5c;
    border-left: 4px solid #2a7d7d;
    padding-left: 10px;
    margin-top: 28px;
    margin-bottom: 6px;
    page-break-after: avoid;
  }
  h3 {
    font-size: 12pt;
    font-weight: 700;
    color: #1a1a1a;
    margin-top: 20px;
    margin-bottom: 4px;
    page-break-after: avoid;
  }
  p {
    margin: 6px 0 12px 0;
    text-align: justify;
  }
  blockquote {
    border-left: 3px solid #2a7d7d;
    margin: 8px 0;
    padding: 4px 12px;
    color: #555;
    font-size: 10pt;
    background: #f5fafa;
  }
  img {
    display: block;
    max-width: 100%;
    height: auto;
    margin: 14px auto 18px auto;
    border-radius: 4px;
    page-break-inside: avoid;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 10pt;
    margin: 12px 0 18px 0;
    page-break-inside: avoid;
  }
  th {
    background: #2a7d7d;
    color: #fff;
    padding: 6px 10px;
    text-align: left;
    font-weight: 600;
  }
  td {
    padding: 5px 10px;
    border-bottom: 1px solid #dde8e8;
  }
  tr:nth-child(even) td { background: #f5fafa; }
  code {
    background: #f0f4f4;
    padding: 1px 4px;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
    font-size: 9.5pt;
    color: #2a7d7d;
  }
  pre {
    background: #f0f4f4;
    padding: 10px 14px;
    border-radius: 4px;
    overflow-x: auto;
    font-size: 9pt;
    page-break-inside: avoid;
  }
  hr {
    border: none;
    border-top: 1px solid #cde0e0;
    margin: 20px 0;
  }
  ul, ol {
    padding-left: 22px;
    margin: 6px 0 12px 0;
  }
  li { margin-bottom: 3px; }
  /* Section separator before each h2 angolo */
  .section-break { page-break-before: always; }
"""

HTML = f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Report 1 — Man in the Loop</title>
<style>{CSS}</style>
</head>
<body>
{body_html}
</body>
</html>"""

HTML_FILE.write_text(HTML, encoding='utf-8')
print(f"HTML written → {HTML_FILE}")

# --- Chromium headless print to PDF ---
chromium = None
for candidate in ['google-chrome', 'chromium-browser', 'chromium']:
    result = subprocess.run(['which', candidate], capture_output=True, text=True)
    if result.returncode == 0:
        chromium = result.stdout.strip()
        break

if not chromium:
    print("ERROR: no chromium found", file=sys.stderr)
    sys.exit(1)

print(f"Using: {chromium}")

cmd = [
    chromium,
    '--headless=new',
    '--no-sandbox',
    '--disable-gpu',
    '--disable-dev-shm-usage',
    f'--print-to-pdf={PDF_FILE}',
    '--print-to-pdf-no-header',
    f'file://{HTML_FILE.resolve()}',
]

result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

if result.returncode == 0 and PDF_FILE.exists():
    size_kb = PDF_FILE.stat().st_size // 1024
    print(f"PDF saved → {PDF_FILE}  ({size_kb} KB)")
    HTML_FILE.unlink()  # clean up temp HTML
else:
    print("STDOUT:", result.stdout[-500:] if result.stdout else '')
    print("STDERR:", result.stderr[-500:] if result.stderr else '')
    print(f"Return code: {result.returncode}")
    sys.exit(1)
