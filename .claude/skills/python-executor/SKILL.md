---
name: python-executor
description: "Sandboxed Python code execution via inference.sh with 100+ pre-installed libraries. Use when the user needs to run Python scripts for data processing, web scraping, visualization, or image manipulation."
allowed-tools: Bash(infsh *)
---

# Python Code Executor

Execute Python code in a safe, sandboxed environment with 100+ pre-installed libraries via the inference.sh CLI.

## Quick Start

```bash
infsh app run python-executor --input '{"code": "print(\"Hello World\")"}'
```

## Capabilities

- **Python 3.10** runtime
- **Configurable RAM**: 8GB default, 16GB high-memory option
- **Adjustable timeout**: 1-300 seconds (30-second default)

## Pre-installed Libraries

- **Web scraping**: requests, BeautifulSoup, Selenium
- **Data processing**: NumPy, Pandas, SciPy
- **Visualization**: Matplotlib, Seaborn, Plotly
- **Image manipulation**: Pillow, OpenCV
- **Video editing**: MoviePy
- **3D modeling**: trimesh, Open3D

## Output Files

Files saved to the `outputs/` directory are automatically returned.

## Important Limitations

- **CPU-only** — no GPU, no ML model inference
- **Non-interactive** — visualizations must use `savefig()` rather than interactive display methods
- Focuses on traditional data processing, automation, and content manipulation

## Use Cases

Web scraping, data analysis, image processing, video creation, 3D work, API integration, PDF generation, and general automation tasks.
