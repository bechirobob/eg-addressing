#!/usr/bin/env python3
"""Render training manual markdown files to official HTML for Chrome PDF export."""
from __future__ import annotations

import html
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CHROME = "/usr/bin/google-chrome"

CSS = """
@page {
  size: A4;
  margin: 18mm 16mm 18mm 16mm;
}
:root {
  --navy: #18324a;
  --green: #276749;
  --gold: #b78b2f;
  --red: #9f2d2d;
  --ink: #1f2933;
  --muted: #5f6f7d;
  --line: #d6dde5;
  --paper: #fffdf7;
  --panel: #f6f2e8;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--paper);
  color: var(--ink);
  font-family: "Liberation Sans", "DejaVu Sans", Arial, sans-serif;
  font-size: 10.6pt;
  line-height: 1.48;
}
.manual {
  max-width: 178mm;
  margin: 0 auto;
}
.cover {
  min-height: 247mm;
  padding: 18mm 13mm;
  border: 1.4pt solid var(--navy);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  page-break-after: always;
  background: linear-gradient(180deg, #fffdf7 0%, #f7f3e9 100%);
}
.identity-line {
  color: var(--navy);
  font-weight: 700;
  letter-spacing: .07em;
  text-transform: uppercase;
  font-size: 9.5pt;
  border-bottom: 2pt solid var(--gold);
  padding-bottom: 5mm;
}
.cover h1 {
  color: var(--navy);
  font-family: Georgia, "Times New Roman", serif;
  font-size: 29pt;
  line-height: 1.08;
  margin: 20mm 0 7mm;
}
.cover .subtitle {
  color: var(--green);
  font-weight: 700;
  font-size: 12pt;
  text-transform: uppercase;
  letter-spacing: .04em;
}
.cover .status-box {
  border-left: 4pt solid var(--green);
  padding: 5mm 6mm;
  background: #ffffff;
  margin-top: 12mm;
}
.cover-footer {
  color: var(--muted);
  border-top: 1pt solid var(--line);
  padding-top: 5mm;
  font-size: 9.5pt;
}
h1, h2, h3, h4 {
  color: var(--navy);
  font-family: Georgia, "Times New Roman", serif;
  line-height: 1.18;
}
h1 { font-size: 21pt; margin: 0 0 6mm; }
h2 {
  font-size: 15.2pt;
  margin: 8mm 0 3mm;
  padding-top: 2mm;
  border-top: 1.2pt solid var(--line);
}
h3 { font-size: 12.5pt; margin: 5mm 0 2mm; color: var(--green); }
h4 { font-size: 11pt; margin: 4mm 0 1.5mm; }
p { margin: 0 0 3.2mm; }
ul, ol { margin: 0 0 4mm 6mm; padding-left: 5mm; }
li { margin-bottom: 1.2mm; }
table {
  width: 100%;
  border-collapse: collapse;
  margin: 3.5mm 0 5mm;
  font-size: 9.2pt;
}
th {
  background: var(--navy);
  color: white;
  text-align: left;
  font-weight: 700;
}
th, td {
  border: 0.7pt solid var(--line);
  padding: 2.2mm 2.5mm;
  vertical-align: top;
}
tr:nth-child(even) td { background: #fbf8ef; }
.callout {
  border-left: 3pt solid var(--gold);
  background: #fff8e6;
  padding: 3mm 4mm;
  margin: 4mm 0;
}
.warning {
  border-left: 3pt solid var(--red);
  background: #fff5f3;
  padding: 3mm 4mm;
  margin: 4mm 0;
}
.module {
  border: 1pt solid var(--line);
  padding: 4mm 5mm;
  margin: 5mm 0;
  background: white;
  page-break-inside: avoid;
}
.checklist li::marker { color: var(--green); }
.toc a, .index-list a { color: var(--navy); text-decoration: none; }
.page-break { page-break-after: always; }
.small { font-size: 9pt; color: var(--muted); }
.doc-control td:first-child { width: 34%; font-weight: 700; color: var(--navy); }
.section-ref { color: var(--muted); }
footer.print-note { margin-top: 8mm; color: var(--muted); font-size: 8.8pt; }
"""


def inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    return text


def render_markdown(md: str) -> str:
    lines = md.splitlines()
    out: list[str] = []
    in_ul = False
    in_ol = False
    in_table = False
    in_callout = False
    in_warning = False
    para: list[str] = []

    def flush_para() -> None:
        nonlocal para
        if para:
            out.append(f"<p>{inline(' '.join(para))}</p>")
            para = []

    def close_lists() -> None:
        nonlocal in_ul, in_ol
        if in_ul:
            out.append("</ul>"); in_ul = False
        if in_ol:
            out.append("</ol>"); in_ol = False

    def close_table() -> None:
        nonlocal in_table
        if in_table:
            out.append("</tbody></table>"); in_table = False

    def close_boxes() -> None:
        nonlocal in_callout, in_warning
        if in_callout:
            out.append("</div>"); in_callout = False
        if in_warning:
            out.append("</div>"); in_warning = False

    for raw in lines:
        line = raw.rstrip()
        if not line:
            flush_para(); close_lists(); close_table(); close_boxes()
            continue
        if line == "[PAGEBREAK]":
            flush_para(); close_lists(); close_table(); close_boxes(); out.append('<div class="page-break"></div>'); continue
        if line.startswith(":::callout"):
            flush_para(); close_lists(); close_table(); close_boxes(); out.append('<div class="callout">'); in_callout = True; continue
        if line.startswith(":::warning"):
            flush_para(); close_lists(); close_table(); close_boxes(); out.append('<div class="warning">'); in_warning = True; continue
        if line == ":::":
            flush_para(); close_boxes(); continue
        if line.startswith("#"):
            flush_para(); close_lists(); close_table(); close_boxes()
            level = len(line) - len(line.lstrip("#"))
            text = line[level:].strip()
            level = min(max(level, 1), 4)
            anchor = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
            out.append(f'<h{level} id="{anchor}">{inline(text)}</h{level}>')
            continue
        if line.startswith("|") and line.endswith("|"):
            flush_para(); close_lists(); close_boxes()
            cells = [c.strip() for c in line.strip("|").split("|")]
            if all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
                continue
            if not in_table:
                out.append('<table><tbody>'); in_table = True
                tag = "th"
            else:
                tag = "td"
            out.append("<tr>" + "".join(f"<{tag}>{inline(c)}</{tag}>" for c in cells) + "</tr>")
            continue
        close_table()
        if re.match(r"^\d+\.\s+", line):
            flush_para(); close_boxes()
            if not in_ol:
                close_lists(); out.append("<ol>"); in_ol = True
            item_text = re.sub(r'^\d+\.\s+', '', line)
            out.append(f"<li>{inline(item_text)}</li>")
            continue
        if line.startswith("- "):
            flush_para(); close_boxes()
            if not in_ul:
                close_lists(); out.append('<ul class="checklist">'); in_ul = True
            out.append(f"<li>{inline(line[2:].strip())}</li>")
            continue
        para.append(line)
    flush_para(); close_lists(); close_table(); close_boxes()
    return "\n".join(out)


def build_html(source: Path, output: Path) -> None:
    text = source.read_text(encoding="utf-8")
    title = next((line[2:].strip() for line in text.splitlines() if line.startswith("# ")), source.stem)
    body = render_markdown(text)
    cover_title = html.escape(title)
    is_es = source.name.upper().startswith("ES")
    language_label = "Versión española" if is_es else "English version"
    identity_line = "República de Guinea Ecuatorial · Capacitación de Direccionamiento Digital Nacional" if is_es else "Republic of Equatorial Guinea · National Digital Addressing Training"
    status_text = "Material de capacitación para piloto controlado. Los registros públicos y la publicación pública siguen sujetos a aprobación institucional." if is_es else "Controlled pilot training material. Public records and public release remain subject to institutional approval."
    footer_text = "Soporte operativo: BeCore · Uso para capacitación, revisión y preparación del piloto controlado." if is_es else "Operational support: BeCore · Use for training, review, and controlled pilot preparation."
    html_doc = f"""<!doctype html>
<html lang="{'es' if source.name.upper().startswith('ES') else 'en'}">
<head>
  <meta charset="utf-8">
  <title>{cover_title}</title>
  <style>{CSS}</style>
</head>
<body>
  <main class="manual">
    <section class="cover">
      <div>
        <div class="identity-line">{html.escape(identity_line)}</div>
        <h1>{cover_title}</h1>
        <div class="subtitle">{language_label}</div>
        <div class="status-box">{html.escape(status_text)}</div>
      </div>
      <div class="cover-footer">{html.escape(footer_text)}</div>
    </section>
    {body}
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
