from __future__ import annotations

import importlib
from pathlib import Path
from typing import Literal

from markdown import markdown

OutputFormat = Literal["pdf", "pptx", "docx", "md"]


def export_markdown(markdown_text: str, target: Path) -> Path:
    target.write_text(markdown_text, encoding="utf-8")
    return target


def export_pdf(markdown_text: str, target: Path) -> Path:
    html = markdown(markdown_text, extensions=["tables", "fenced_code"])  # type: ignore[arg-type]
    try:
        weasyprint = importlib.import_module("weasyprint")
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("PDF export requires the 'weasyprint' package.") from exc
    pdf = weasyprint.HTML(string=html)
    pdf.write_pdf(target)
    return target


def export_docx(markdown_text: str, target: Path) -> Path:
    try:
        docx = importlib.import_module("docx")
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("DOCX export requires the 'python-docx' package.") from exc

    document = docx.Document()
    for line in markdown_text.splitlines():
        if line.startswith("# "):
            document.add_heading(line[2:], level=1)
        elif line.startswith("## "):
            document.add_heading(line[3:], level=2)
        elif line.startswith("### "):
            document.add_heading(line[4:], level=3)
        else:
            document.add_paragraph(line)
    document.save(target)
    return target


def export_pptx(markdown_text: str, target: Path) -> Path:
    try:
        pptx = importlib.import_module("pptx")
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("PPTX export requires the 'python-pptx' package.") from exc

    presentation = pptx.Presentation()
    slide_layout = presentation.slide_layouts[1]
    for section in markdown_text.split("\n\n"):
        slide = presentation.slides.add_slide(slide_layout)
        slide.shapes.title.text = section.splitlines()[0][:255]
        body = slide.shapes.placeholders[1].text_frame
        for line in section.splitlines()[1:]:
            p = body.add_paragraph()
            p.text = line
    presentation.save(target)
    return target


EXPORTERS = {
    "md": export_markdown,
    "pdf": export_pdf,
    "docx": export_docx,
    "pptx": export_pptx,
}


def export(markdown_text: str, output_format: OutputFormat, destination: Path) -> Path:
    exporter = EXPORTERS.get(output_format)
    if exporter is None:
        raise ValueError(f"Unsupported output format: {output_format}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    return exporter(markdown_text, destination)
