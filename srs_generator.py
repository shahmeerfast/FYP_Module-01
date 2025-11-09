import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict


@dataclass
class SRSDocument:
    document_id: str
    title: str
    version: str
    date: str
    author: str
    sections: Dict[str, Any]


class SRSGenerator:
    """Exporter utilities for SRS documents. Content is produced elsewhere."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    # ---------------------------- Exporters ---------------------------- #
    def export_to_json(self, srs: SRSDocument, output_file: str | None = None) -> str:
        if output_file is None:
            output_file = f"srs_{srs.document_id}.json"
        payload = {
            "document_id": srs.document_id,
            "title": srs.title,
            "version": srs.version,
            "date": srs.date,
            "author": srs.author,
            "sections": srs.sections,
        }
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        self.logger.info("SRS exported to %s", output_file)
        return output_file

    def export_to_html(self, srs: SRSDocument, output_file: str | None = None) -> str:
        if output_file is None:
            output_file = f"srs_{srs.document_id}.html"
        html = self._generate_html(srs)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html)
        self.logger.info("SRS exported to %s", output_file)
        return output_file

    def export_to_pdf(self, srs: SRSDocument, output_file: str | None = None) -> str:
        if output_file is None:
            output_file = f"srs_{srs.document_id}.pdf"
        html = self._generate_html(srs)
        try:
            from weasyprint import HTML
            HTML(string=html).write_pdf(output_file)
            self.logger.info("SRS exported to %s (PDF)", output_file)
            return output_file
        except Exception as e:
            self.logger.warning("PDF export failed (%s). Saving HTML fallback.", e)
            html_fallback = output_file.replace(".pdf", ".html")
            with open(html_fallback, "w", encoding="utf-8") as f:
                f.write(html)
            return html_fallback

    # ---------------------------- HTML View ---------------------------- #
    def _generate_html(self, srs: SRSDocument) -> str:
        return f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <title>{srs.title}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 40px; }}
    h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; }}
    h2 {{ color: #34495e; margin-top: 30px; }}
    h3 {{ color: #7f8c8d; }}
    .metadata {{ background-color: #ecf0f1; padding: 15px; margin-bottom: 20px; }}
    ul {{ margin: 10px 0; }}
    li {{ margin: 5px 0; }}
    .toolbar {{ position: sticky; top: 0; background: #fff; padding: 10px 0 20px 0; }}
    .btn {{ display: inline-block; padding: 10px 16px; background-color: #2d6cdf; color: #fff; border-radius: 6px; text-decoration: none; border: none; cursor: pointer; }}
    .btn:hover {{ background-color: #1f56bd; }}
    @media print {{ .toolbar {{ display: none; }} }}
  </style>
</head>
<body>
  <div class=\"toolbar\">
    <button class=\"btn\" onclick=\"window.print()\">Download PDF</button>
  </div>
  <h1>{srs.title}</h1>
  <div class=\"metadata\">
    <p><strong>Document ID:</strong> {srs.document_id}</p>
    <p><strong>Version:</strong> {srs.version}</p>
    <p><strong>Date:</strong> {srs.date}</p>
    <p><strong>Author:</strong> {srs.author}</p>
  </div>
  <h2>1. Introduction</h2>
  <h3>1.1 Purpose</h3>
  <p>{srs.sections.get('introduction', {{}}).get('purpose', '')}</p>
  <h3>1.2 Scope</h3>
  <p>{srs.sections.get('introduction', {{}}).get('scope', '')}</p>
  <h3>1.3 Definitions</h3>
  <ul>{''.join(f'<li>{{d}}</li>' for d in srs.sections.get('introduction', {{}}).get('definitions', []))}</ul>
  <h3>1.4 Overview</h3>
  <p>{srs.sections.get('introduction', {{}}).get('overview', '')}</p>

  <h2>2. Overall Description</h2>
  <h3>2.1 Product Functions</h3>
  <ul>{''.join(f'<li>{{f}}</li>' for f in srs.sections.get('overall_description', {{}}).get('product_functions', []))}</ul>
  <h3>2.2 User Characteristics</h3>
  <ul>{''.join(f'<li>{{u}}</li>' for u in srs.sections.get('overall_description', {{}}).get('user_characteristics', []))}</ul>
  <h3>2.3 Constraints</h3>
  <ul>{''.join(f'<li>{{c}}</li>' for c in srs.sections.get('overall_description', {{}}).get('constraints', []))}</ul>
</body>
</html>
"""


