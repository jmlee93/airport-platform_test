# Airport Platform Report Generator

This repository contains a lightweight reporting toolkit that transforms structured financial data into presentation-ready documents. Key features include:

- **Markdown-based rendering pipeline** that exports to PDF, Word (DOCX), PowerPoint (PPTX), or keeps the Markdown output as-is.
- **Template-driven natural language summaries**, enriched through an optional LLM integration.
- **Automatic numbering of tables and figures** with cross-references and a generated table of contents.
- **Custom branding controls** driven by a configuration file (logo, colors, output format).

## Project layout

```
configs/
  default.yaml         # Example configuration
report_generator/
  cli.py               # CLI entry point
  config.py            # Configuration parsing
  data_models.py       # Typed containers for report content
  renderer.py          # Output exporters (PDF, DOCX, PPTX, Markdown)
  references.py        # Auto-numbering logic for tables & figures
  summarizer.py        # Summary template + optional LLM enrichment
  templating.py        # Markdown templating helpers
sample_payload.json    # Example payload to render
templates/
  report.md.j2         # Jinja2-based Markdown template
  summary_template.txt # Baseline summary sentence template
```

## Getting started

1. Install the project with the optional exporters you require:

   ```bash
   pip install -r requirements.txt  # (create this list based on optional deps)
   ```

   | Feature | Dependency |
   | --- | --- |
   | PDF export | `weasyprint`
   | DOCX export | `python-docx`
   | PPTX export | `python-pptx`
   | LLM enrichment | `openai`

   > If the optional dependency is missing, the exporter gracefully falls back with an informative error.

2. Update `configs/default.yaml` or create a new config with your branding, template, and output preferences.
3. Provide a JSON payload that follows the structure shown in `sample_payload.json`.
4. Run the CLI:

   ```bash
   python -m report_generator.cli configs/default.yaml sample_payload.json
   ```

   The rendered artifact is saved to the configured output directory (defaults to `output/`).

## Customization

- **Branding:** Update the `branding` block with `company_name`, `logo_path`, and color palette.
- **Templates:** Point `markdown_template` to a different `.j2` file or edit `templates/report.md.j2` to adjust layout.
- **Summary templates:** Modify `templates/summary_template.txt` to alter the baseline narrative. Set `enrich_summary_via_llm: true` to invoke an LLM (requires valid API credentials in your environment).
- **Output formats:** Choose between `md`, `pdf`, `docx`, or `pptx` in the configuration.

## Extending

The codebase is modular, making it easy to plug in additional exporters or data sources. See `report_generator/renderer.py` and `report_generator/templating.py` for reference points when adding new capabilities.
