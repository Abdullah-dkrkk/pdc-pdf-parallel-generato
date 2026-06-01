# Parallel PDF Report Generator — PDC Project

Real-time PDF report generator demonstrating **parallel vs sequential processing** with live speedup comparison dashboard — PDC (Parallel & Distributed Computing) final project.

## Problem

School admins, HR managers, clinic staff, and small businesses waste hours generating bulk PDFs (report cards, salary slips, invoices) manually or using expensive tools.

## Solution

A free, web-based tool that:
1. Takes Excel/CSV data + HTML template with `{{placeholders}}`
2. Generates N individual PDFs using **parallel processing**
3. Shows **LIVE speed comparison** (sequential vs parallel with 1,2,4,8 workers)
4. Provides ZIP download of all PDFs

## PDC Concepts Demonstrated

| Concept | Implementation |
|---------|---------------|
| Data Parallelism | Rows divided equally among worker processes |
| Task Decomposition | Big job → smaller chunks per worker |
| Speedup (S) | `S = T_seq / T_par` — calculated and charted |
| Amdahl's Law | Theoretical max speedup plotted alongside actual |
| Efficiency (E) | `E = Speedup / cores` — measures overhead cost |
| Scalability | Run with 1,2,4,8 workers → see scaling curve |

## Tech Stack

- **Backend:** Python Flask
- **PDF Generation:** ReportLab
- **Parallel Processing:** multiprocessing.Pool
- **Charts:** matplotlib
- **Data:** pandas (Excel/CSV)
- **Frontend:** Tailwind v4 + Vercel Geist design tokens

## Quick Start

```bash
pip install -r requirements.txt
python app.py
```

Open http://localhost:5000

1. Upload a CSV/Excel file (see `sample/students.csv`)
2. Enter HTML template with `{{column_name}}` placeholders
3. Click "Generate PDFs"
4. View performance comparison chart + download ZIP

## Deployment

See `vercel.json` for Vercel deployment config. Note: multiprocessing has limitations on serverless — use local run for true parallel metrics.

## Project Structure

```
├── app.py                    # Flask application
├── modules/
│   ├── pdf_generator.py      # Core PDF generation
│   ├── sequential.py         # Sequential processing
│   ├── parallel.py           # Parallel processing
│   └── comparator.py         # Timing, speedup, charts
├── templates/index.html       # Single-page UI
├── static/css/style.css       # Geist design tokens
├── sample/students.csv        # Sample data
├── requirements.txt
└── vercel.json
```
