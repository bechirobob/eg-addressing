#!/usr/bin/env python3
"""Render EG Addressing training manuals using the frozen public-service visual system."""
from __future__ import annotations

import base64
import html
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CHROME = "/usr/bin/google-chrome"
COAT_OF_ARMS = ROOT / "apps/admin-portal/public/eg-coat-of-arms.svg"

CSS = """
@page {
  size: A4;
  margin: 17mm 18mm 18mm 18mm;
}
:root {
  --eg-green: #25633a;
  --eg-red: #a8322d;
  --eg-blue: #174f82;
  --eg-blue-deep: #0d2f4f;
  --eg-gold: #a67c2d;
  --eg-focus: #f4b300;
  --eg-ink: #14202b;
  --eg-muted: #51616f;
  --eg-line: #cbd5da;
  --eg-line-strong: #9daeb8;
  --eg-ivory: #f5f0e5;
  --eg-paper: #fffdf8;
  --eg-white: #ffffff;
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  background: var(--eg-ivory);
  color: var(--eg-ink);
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-size: 10.7pt;
  line-height: 1.58;
}
.manual {
  max-width: 176mm;
  margin: 0 auto;
  background: var(--eg-paper);
}
.flag-ribbon {
  width: 100%;
  height: 14px;
  margin-bottom: 22px;
  background: linear-gradient(90deg, var(--eg-blue) 0 20%, var(--eg-green) 20% 47%, #ffffff 47% 72%, var(--eg-red) 72% 100%);
  box-shadow: 0 1px 0 rgba(13, 47, 79, 0.16);
}
.cover {
  min-height: 246mm;
  padding: 0 0 18mm;
  display: flex;
  flex-direction: column;
  page-break-after: always;
}
.cover-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 10mm 10mm 18mm;
}
.official-lockup {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  margin-bottom: 24mm;
}
.crest-frame {
  width: 36mm;
  padding: 3.5mm;
  border: 1px solid rgba(13, 47, 79, 0.24);
  border-bottom: 4px solid var(--eg-gold);
  background: var(--eg-paper);
  box-shadow: 6px 6px 0 rgba(13, 47, 79, 0.06);
}
.crest-frame img {
  width: 100%;
  height: auto;
  display: block;
}
.republic-line {
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 9pt;
  font-weight: 850;
  color: var(--eg-blue);
}
.platform-line {
  margin: 0;
  color: var(--eg-muted);
  font-size: 10.2pt;
  font-weight: 650;
}
.cover-eyebrow {
  display: inline-block;
  margin: 0 0 9mm;
  padding-left: 3.5mm;
  border-left: 4px solid var(--eg-gold);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 8.5pt;
  font-weight: 850;
  color: var(--eg-blue-deep);
}
.cover h1 {
  max-width: 150mm;
  margin: 0;
  color: var(--eg-blue-deep);
  font-family: Georgia, "Times New Roman", serif;
  font-size: 31pt;
  line-height: 0.98;
  letter-spacing: -0.025em;
}
.cover-subtitle {
  max-width: 135mm;
  margin: 8mm auto 0;
  color: var(--eg-muted);
  font-size: 11.5pt;
  line-height: 1.7;
}
.cover-footer {
  border-top: 1px solid rgba(13, 47, 79, 0.14);
  padding: 7mm 9mm 0;
  color: var(--eg-muted);
  font-size: 9.2pt;
  display: flex;
  justify-content: space-between;
  gap: 10mm;
}
.content {
  padding: 0 1mm 4mm;
}
h1, h2, h3, h4 {
  color: var(--eg-blue-deep);
  font-family: Georgia, "Times New Roman", serif;
  letter-spacing: -0.015em;
  line-height: 1.2;
}
h1 { font-size: 22pt; margin: 0 0 7mm; }
h2 {
  font-size: 15.5pt;
  margin: 9mm 0 3.4mm;
  padding-top: 5mm;
  border-top: 1px solid rgba(13, 47, 79, 0.14);
}
h3 { font-size: 12.5pt; margin: 5mm 0 2mm; color: var(--eg-blue); }
h4 { font-size: 11pt; margin: 4mm 0 1.5mm; color: var(--eg-ink); }
p { margin: 0 0 3.4mm; }
ul, ol { margin: 0 0 4.2mm 7mm; padding-left: 6mm; }
li { margin-bottom: 1.5mm; padding-left: 1mm; }
ol > li::marker { color: var(--eg-blue); font-weight: 750; }
ul > li::marker { color: var(--eg-green); }
strong { color: var(--eg-blue-deep); }
.section-break { page-break-after: always; }
.document-control p {
  margin-bottom: 2.5mm;
}
.document-control p strong {
  display: inline-block;
  min-width: 42mm;
}
footer.print-note {
  margin-top: 9mm;
  padding-top: 4mm;
  border-top: 1px solid var(--eg-line);
  color: var(--eg-muted);
  font-size: 8.8pt;
}
"""


def sanitize_svg(svg: str) -> str:
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S)
    svg = re.sub(r"<metadata.*?</metadata>", "", svg, flags=re.S)
    svg = re.sub(r"\s(?:sodipodi|inkscape|dc|cc|rdf):[\w-]+=(['\"]).*?\1", "", svg)
    svg = re.sub(r"\s+xmlns:(?:sodipodi|inkscape|dc|cc|rdf)=(['\"]).*?\1", "", svg)
    return svg.strip()


def coat_data_uri() -> str:
    raw = COAT_OF_ARMS.read_text(encoding="utf-8")
    clean = sanitize_svg(raw)
    encoded = base64.b64encode(clean.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    return text


def paragraph_with_labels(text: str) -> str:
    escaped = inline(text)
    if ":" in text and len(text.split(":", 1)[0]) < 42:
        left, right = text.split(":", 1)
        return f"<p><strong>{inline(left)}:</strong>{inline(right)}</p>"
    return f"<p>{escaped}</p>"


def render_markdown(md: str) -> str:
    lines = md.splitlines()
    out: list[str] = []
    in_ul = False
    in_ol = False
    para: list[str] = []
    document_control = False

    def flush_para() -> None:
        nonlocal para
        if para:
            out.append(paragraph_with_labels(" ".join(para)))
            para = []

    def close_lists() -> None:
        nonlocal in_ul, in_ol
        if in_ul:
            out.append("</ul>")
            in_ul = False
        if in_ol:
            out.append("</ol>")
            in_ol = False

    for raw in lines:
        line = raw.rstrip()
        if not line:
            flush_para()
            close_lists()
            continue
        if line == "[PAGEBREAK]":
            flush_para(); close_lists(); out.append('<div class="section-break"></div>'); continue
        if line.startswith("# "):
            # Cover title already renders separately.
            continue
        if line.startswith("## "):
            flush_para(); close_lists()
            text = line[3:].strip()
            if document_control:
                out.append("</section>")
                document_control = False
            cls = ' class="document-control"' if "control" in text.lower() or "control del documento" in text.lower() else ""
            out.append(f"<section{cls}>")
            document_control = bool(cls)
            anchor = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
            out.append(f'<h2 id="{anchor}">{inline(text)}</h2>')
            continue
        if line.startswith("### "):
            flush_para(); close_lists(); out.append(f"<h3>{inline(line[4:].strip())}</h3>"); continue
        if re.match(r"^\d+\.\s+", line):
            flush_para()
            if not in_ol:
                close_lists(); out.append("<ol>"); in_ol = True
            item_text = re.sub(r"^\d+\.\s+", "", line)
            out.append(f"<li>{inline(item_text)}</li>")
            continue
        if line.startswith("- "):
            flush_para()
            if not in_ul:
                close_lists(); out.append("<ul>"); in_ul = True
            out.append(f"<li>{inline(line[2:].strip())}</li>")
            continue
        para.append(line)
    flush_para(); close_lists()
    if document_control:
        out.append("</section>")
    return "\n".join(out)


def language_meta(source: Path) -> dict[str, str]:
    is_es = source.name.upper().startswith("ES")
    if is_es:
        return {
            "lang": "es",
            "version": "Versión española",
            "republic": "República de Guinea Ecuatorial",
            "platform": "Plataforma Nacional de Direccionamiento Digital",
            "eyebrow": "Capacitación pública",
            "subtitle": "Guía de uso para el piloto controlado: registrar una ubicación, comprobar un código de dirección y hacer seguimiento de una solicitud.",
            "status_left": "Material de capacitación para piloto controlado",
            "status_right": "Soporte operativo: BeCore",
        }
    return {
        "lang": "en",
        "version": "English version",
        "republic": "Republic of Equatorial Guinea",
        "platform": "National Digital Addressing Platform",
        "eyebrow": "Public training",
        "subtitle": "User guide for the controlled pilot: submit a location, check an address code, and track a request.",
        "status_left": "Controlled pilot training material",
        "status_right": "Operational support: BeCore",
    }


def build_html(source: Path, output: Path) -> None:
    text = source.read_text(encoding="utf-8")
    title = next((line[2:].strip() for line in text.splitlines() if line.startswith("# ")), source.stem)
    body = render_markdown(text)
    meta = language_meta(source)
    crest_src = coat_data_uri()
    html_doc = f"""<!doctype html>
<html lang="{meta['lang']}">
<head>
  <meta charset="utf-8">
  <title>{html.escape(title)}</title>
  <style>{CSS}</style>
</head>
<body>
  <main class="manual">
    <section class="cover" aria-label="Manual cover">
      <div class="flag-ribbon" aria-hidden="true"></div>
      <div class="cover-main">
        <div class="official-lockup">
          <div class="crest-frame" aria-hidden="true">
            <img src="{crest_src}" alt="" />
          </div>
          <p class="republic-line">{html.escape(meta['republic'])}</p>
          <p class="platform-line">{html.escape(meta['platform'])}</p>
        </div>
        <p class="cover-eyebrow">{html.escape(meta['eyebrow'])}</p>
        <h1>{html.escape(title)}</h1>
        <p class="cover-subtitle">{html.escape(meta['subtitle'])}</p>
      </div>
      <div class="cover-footer">
        <span>{html.escape(meta['status_left'])}</span>
        <span>{html.escape(meta['version'])} · {html.escape(meta['status_right'])}</span>
      </div>
    </section>
    <section class="content">
      {body}
      <footer class="print-note">{html.escape(meta['republic'])} · {html.escape(meta['platform'])}</footer>
    </section>
  </main>
</body>
</html>
"""
    output.write_text(html_doc, encoding="utf-8")


def chrome_pdf(html_path: Path, pdf_path: Path) -> None:
    cmd = [
        CHROME,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        html_path.as_uri(),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: render_training_manual.py SOURCE.md [SOURCE.md ...]", file=sys.stderr)
        return 2
    for arg in argv[1:]:
        source = Path(arg).resolve()
        if not source.exists():
            raise SystemExit(f"missing source: {source}")
        output_dir = source.parent / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        suffix = "ES" if source.name.upper().startswith("ES") else "EN"
        html_path = output_dir / f"EG-Addressing-Public-User-Guide-{suffix}.html"
        pdf_path = output_dir / f"EG-Addressing-Public-User-Guide-{suffix}.pdf"
        build_html(source, html_path)
        chrome_pdf(html_path, pdf_path)
        print(f"rendered {pdf_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
