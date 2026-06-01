# Parallel PDF Report Generator — PDC Project

> **Project Name:** `pdc-pdf-parallel-generator`
> **Git Description:** Real-time PDF report generator demonstrating parallel vs sequential processing with live speedup comparison dashboard — PDC (Parallel & Distributed Computing) final project  
> **Stack:** Python Flask + Vercel Geist design tokens + multiprocessing + reportlab + matplotlib  
> **Design System:** Vercel Geist (colors, typography, spacing — no Vercel functionality used)  
> **Deployment:** Vercel (Flask via vercel.json — separate from design system)  
> **Timeline:** Build ready in ~4-5 hours

---

## 1. Problem Statement (Real User Pain)

### Who feels this pain?
- **School admins** → generating 500+ report cards monthly (8-10 hours lost)
- **HR managers** → salary slips for 200+ employees every month
- **Clinic staff** → patient test reports daily
- **Small businesses** → invoices, receipts, certificates

### What's the current situation?
- Excel data + Word template → manually copy-paste each row → hours of work
- Google Docs "Email merge" → slow, limited to 50 at a time
- Paid tools (Adobe Acrobat Pro, Docmosis, Zoho) → expensive for small orgs
- Open-source libraries (ReportLab, Pandoc) → CLI only, no UI, no parallel processing

### What's the gap?
**No simple, free, web-based tool exists** that:
1. Takes Excel + template
2. Generates bulk PDFs  
3. Uses **parallel processing** to do it FAST
4. Shows LIVE speed comparison (sequential vs parallel)
5. Non-technical user can operate

---

## 2. What the App Does (End to End)

```
User uploads Excel file → User uploads PDF/HTML template → 
System processes rows → Shows speed comparison →
Downloads all PDFs as ZIP
```

### Inputs
| Input | Format | Example |
|-------|--------|---------|
| Data file | `.xlsx` / `.csv` | Columns: name, marks, grade, etc. |
| Template | `.html` with `{{placeholders}}` | `<p>Student {{name}} got {{marks}}</p>` |

### Outputs
| Output | Details |
|--------|---------|
| N individual PDFs | One per row, named by row identifier |
| ZIP download | All PDFs bundled for easy download |
| Speed comparison chart | Sequential vs Parallel (1,2,4,8 workers) |
| Statistics table | Time taken, speedup, efficiency, overhead |

---

## 3. PDC Concepts Demonstrated

| Concept | How It's Shown |
|---------|----------------|
| **Data Parallelism** | Rows divided equally among N worker processes |
| **Task Decomposition** | Big job (1000 PDFs) → smaller chunks (250 × 4 workers) |
| **Speedup (S)** | `S = T_sequential / T_parallel` — calculated and charted |
| **Amdahl's Law** | Theoretical max speedup = `1 / (1-P) + P/N` where P = parallel fraction |
| **Efficiency (E)** | `E = Speedup / Number of cores` — shows overhead cost |
| **Load Balancing** | Equal chunk sizes = workers finish at similar times |
| **Overhead** | Process spawning time measured separately |
| **Scalability** | Run with 1, 2, 4, 8 workers → show scaling curve |

---

## 4. Tech Stack & Dependencies

```
Python 3.10+
├── flask            → Web server & API
├── pandas           → Read Excel/CSV
├── reportlab        → Generate PDFs
├── jinja2           → Template rendering (built into Flask)
├── matplotlib       → Speed comparison charts
├── multiprocessing  → Parallel processing (built into Python)
├── gunicorn         → Production WSGI server (for Vercel)
└── waitress         → Alternative WSGI (for local)
```

**Frontend:** HTML + Vercel Geist design tokens + Tailwind v4 (CDN) — minimal, no React needed  
**Deployment:** Vercel (Serverless Functions via Flask — separate from design tokens)

---

## 5. Directory Structure

```
pdc-pdf-parallel-generator/
├── app.py                    # Main Flask application
├── vercel.json               # Vercel deployment config
├── requirements.txt          # Python dependencies
├── templates/
│   └── index.html            # Single-page UI
├── uploads/                  # Uploaded files (temp)
├── output/                   # Generated PDFs (temp)
├── charts/                   # Generated comparison charts
├── modules/
│   ├── __init__.py
│   ├── pdf_generator.py      # Core PDF generation logic
│   ├── sequential.py         # Sequential processing
│   ├── parallel.py           # Parallel processing (multiprocessing.Pool)
│   └── comparator.py         # Timing, speedup, chart generation
├── static/
│   └── css/
│       └── style.css         # (minimal, Tailwind CDN preferred)
└── PDC-PDF-GENERATOR-ROADMAP.md  # This file
```

---

## 6. Component Details

### 6.1 `app.py` — Flask Routes

```
GET  /              → index.html (upload form)
POST /upload        → receive file + template, start processing
GET  /status/<id>   → polling endpoint for progress
GET  /download/<id> → download final ZIP
GET  /chart/<id>    → view speed comparison chart
```

**Flow:**
1. User uploads Excel + template via `/upload`
2. Backend generates a unique task ID
3. Runs BOTH sequential and parallel processing
4. Stores timing data + generated PDFs
5. Returns results page with chart + download button

### 6.2 `modules/pdf_generator.py` — Core Logic

```python
def generate_single_pdf(row_data: dict, template_str: str, output_path: str):
    """
    Takes 1 row of data + template → renders → saves 1 PDF
    """
    rendered_content = template_str
    for key, value in row_data.items():
        placeholder = "{{" + key + "}}"
        rendered_content = rendered_content.replace(placeholder, str(value))
    
    # Render to PDF using reportlab or weasyprint
    pdf_buffer = render_html_to_pdf(rendered_content)
    with open(output_path, 'wb') as f:
        f.write(pdf_buffer.getvalue())
```

### 6.3 `modules/sequential.py` — Row by Row

```python
def process_sequential(rows: list[dict], template: str, output_dir: str) -> float:
    start = time.time()
    for i, row in enumerate(rows):
        path = f"{output_dir}/report_{i+1}.pdf"
        generate_single_pdf(row, template, path)
    end = time.time()
    return end - start  # Total time in seconds
```

### 6.4 `modules/parallel.py` — Chunked Processing

```python
def process_chunk(chunk_data: tuple) -> None:
    rows, template, output_dir, chunk_id = chunk_data
    for i, row in enumerate(rows):
        path = f"{output_dir}/report_{chunk_id}_{i+1}.pdf"
        generate_single_pdf(row, template, path)

def process_parallel(rows: list[dict], template: str, output_dir: str, num_workers: int) -> float:
    chunks = np.array_split(rows, num_workers)
    chunked_data = [(chunk, template, output_dir, idx) for idx, chunk in enumerate(chunks)]
    
    start = time.time()
    with Pool(processes=num_workers) as pool:
        pool.map(process_chunk, chunked_data)
    end = time.time()
    return end - start
```

### 6.5 `modules/comparator.py` — Results + Charts

**Calculations:**
```python
speedup = sequential_time / parallel_time
efficiency = speedup / num_workers
parallel_fraction = (speedup - 1) / (num_workers - 1) * num_workers  # Approximate
amdahl_limit = 1 / (1 - parallel_fraction)  # Theoretical max speedup
```

**Chart (matplotlib):**
- X-axis: Number of workers (1, 2, 4, 8)
- Y-axis: Time in seconds
- Bars: Blue (sequential) vs Green (parallel) per worker count
- Line overlay: Theoretical speedup curve (Amdahl's Law)

### 6.6 `templates/index.html` — UI

**Sections:**
1. **Header** — Title + brief description
2. **Upload section** — File input (Excel/CSV) + Template textarea (HTML with placeholders)
3. **Processing section** — "Generate" button + progress indicator / loading spinner
4. **Results section** (shown after processing):
   - Metrics cards: Sequential Time, Parallel Time, Speedup, Efficiency
   - Comparison chart image
   - Download ZIP button
   - Worker comparison table (1, 2, 4, 8 workers)

**Design:** Single page layout using Tailwind v4 (CDN import).

---

## 7. Design System — Vercel Geist

**Important:** Vercel is used here **only** for its design tokens (colors, typography, spacing) — NOT for any functionality. The deployment platform is a separate concern (see Section 8).

### 7.1 CSS Custom Properties (Geist Design Tokens)

Copy these into `static/css/style.css` or a `<style>` block in `index.html`:

```css
:root {
  /* Backgrounds */
  --ds-background-100: #fff;
  --ds-background-200: #fafafa;

  /* Component backgrounds */
  --ds-surface-100: #fafafa;
  --ds-surface-200: #f2f2f2;
  --ds-surface-300: #ebebeb;

  /* Borders */
  --ds-border-100: #ebebeb;
  --ds-border-200: #e0e0e0;
  --ds-border-300: #ccc;

  /* High contrast */
  --ds-contrast-100: #111;
  --ds-contrast-200: #2b2b2b;

  /* Text */
  --ds-text-100: #111;        /* Primary text */
  --ds-text-200: #666;        /* Secondary text */

  /* Semantic colors */
  --ds-blue: #335bf1;
  --ds-red: #e5484d;
  --ds-amber: #f5a623;
  --ds-green: #30a46c;
  --ds-teal: #12b594;
  --ds-purple: #8e4ec6;
  --ds-pink: #d6409f;

  /* Typography — Geist font family */
  --font-sans: 'Geist Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-mono: 'Geist Mono', 'Fira Code', monospace;
}
```

### 7.2 Typography Classes (Geist Scale)

| Use | Class | Size / Weight |
|-----|-------|---------------|
| Hero heading | `.text-heading-72` | 72px / bold |
| Section heading | `.text-heading-32` | 32px / bold |
| Card title | `.text-heading-20` | 20px / bold |
| Button text | `.text-button-14` | 14px / medium |
| Body copy | `.text-copy-14` | 14px / normal |
| Secondary label | `.text-label-12` | 12px / normal |
| Mono code | `.text-copy-13-mono` | 13px / mono |

### 7.3 Geist Font (CDN)

```html
<link rel="preconnect" href="https://api.fonts.coollabs.io" crossorigin />
<link href="https://api.fonts.coollabs.io/css2?family=Geist+Sans:wght@400;500;600;700&family=Geist+Mono:wght@400;500&display=swap" rel="stylesheet" />
```

### 7.4 Tailwind v4 Config (Optional)

If using Tailwind v4 via CDN, extend the theme with Geist tokens:

```css
@import "tailwindcss";
@theme {
  --color-surface-100: #fafafa;
  --color-surface-200: #f2f2f2;
  --color-surface-300: #ebebeb;
  --color-border-100: #ebebeb;
  --color-border-200: #e0e0e0;
  --color-text-100: #111;
  --color-text-200: #666;
  --color-ds-blue: #335bf1;
  --color-ds-red: #e5484d;
  --color-ds-amber: #f5a623;
  --color-ds-green: #30a46c;
  --color-ds-teal: #12b594;
  --font-sans: 'Geist Sans', sans-serif;
  --font-mono: 'Geist Mono', monospace;
}
```

### 7.5 Key Differences from Tailwind Defaults

| Aspect | Tailwind Default | Vercel Geist |
|--------|-----------------|--------------|
| Primary blue | `#3b82f6` (blue-500) | `#335bf1` (ds-blue) |
| Success green | `#22c55e` (green-500) | `#30a46c` (ds-green) |
| Surface bg | `#f9fafb` (gray-50) | `#fafafa` (surface-100) |
| Border | `#e5e7eb` (gray-200) | `#ebebeb` (border-100) |
| Font | `Inter` / system-ui | `Geist Sans` / `Geist Mono` |

All UI in this project should use these Geist tokens for a consistent Vercel-like look.

---

## 8. Deployment (Vercel)

### `vercel.json`
```json
{
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ]
}
```

### `requirements.txt`
```
flask
pandas
reportlab
matplotlib
gunicorn
numpy
```

**Important notes for Vercel:**
- `multiprocessing` has limitations on serverless (use threading alternative or single-worker mode)
- Files are ephemeral on Vercel — use `/tmp` directory for uploads/output
- For local development, full `multiprocessing.Pool` works
- On Vercel, fall back to `concurrent.futures.ThreadPoolExecutor` as alternative
- In demo, show LOCAL run for true parallel metrics + Vercel for web UI

---

## 9. Implementation Order (4-5 Hours)

| Step | Task | Time |
|------|------|------|
| 1 | Flask app scaffold + upload route | 30 min |
| 2 | PDF generation logic (reportlab) | 45 min |
| 3 | Sequential processor | 30 min |
| 4 | Parallel processor (multiprocessing.Pool) | 45 min |
| 5 | Comparison engine + charts | 45 min |
| 6 | Results page + download ZIP | 30 min |
| 7 | UI design (Tailwind) | 30 min |
| 8 | Testing with sample data | 30 min |
| 9 | vercel.json + deployment prep | 15 min |
| 10 | README + final polish | 30 min |

**Total: ~5 hours**

---

## 10. Sample Data (for Demo)

### `students.csv`
```
name,class,marks,grade,remarks
Ali Ahmed,10-A,85,A,Excellent performance
Sara Khan,10-A,92,A+,Outstanding
Usman Ali,10-B,67,C,Needs improvement
Fatima Bibi,10-B,78,B,Good effort
... (100 rows total)
```

### Sample Template
```html
<!DOCTYPE html>
<html>
<head><style>
  body { font-family: Arial, sans-serif; padding: 40px; }
  .header { text-align: center; border-bottom: 2px solid #059669; }
  .student { font-size: 18px; margin: 20px 0; }
  .marks { font-size: 24px; color: #065f46; }
</style></head>
<body>
  <div class="header"><h1>Report Card</h1></div>
  <div class="student">
    <p>Student Name: <strong>{{name}}</strong></p>
    <p>Class: {{class}}</p>
    <p class="marks">Marks: {{marks}} | Grade: {{grade}}</p>
    <p>Remarks: {{remarks}}</p>
  </div>
</body>
</html>
```

---

## 11. Key Code Decisions

### Why `multiprocessing.Pool` and not threading?
- PDF generation is **CPU-bound** (rendering, file I/O)
- ThreadPoolExecutor would be limited by GIL
- `multiprocessing.Pool` gives true parallelism across cores
- Clear speedup visible: 4x on 4 cores, 8x on 8 cores

### Why `reportlab` and not `pdfkit` or `weasyprint`?
- `weasyprint` requires system dependencies (Pango, Cairo) — painful to install
- `pdfkit` requires wkhtmltopdf binary — not available on Vercel
- `reportlab` is pure Python, works everywhere
- Can render HTML-like content programmatically

### Why `vercel.json` and not `Dockerfile`?
- Simpler setup, free tier
- Flask + Python runtime is well-supported
- No Docker knowledge needed

---

## 12. Git Repo Setup

```bash
# Create repo
git init
git add .
git commit -m "init: parallel PDF report generator with speed comparison dashboard"

# Remote (create on GitHub first)
git remote add origin https://github.com/Abdullah-dkrkk/pdc-pdf-parallel-generator.git
git branch -M main
git push -u origin main
```

**GitHub Repo Details:**
- **Name:** `pdc-pdf-parallel-generator`
- **Description:** Parallel vs Sequential PDF report generator with live speedup comparison — PDC final project
- **Topics:** `pdc`, `parallel-computing`, `flask`, `python`, `pdf-generation`, `multiprocessing`
- **README:** Copy relevant sections from this .md

---

## 13. How Another Dev Should Use This .md

1. Read Sections 1-3 → understand the problem and PDC concepts
2. Read Section 5 → create directory structure
3. Follow Section 9 (Implementation Order) → build step by step
4. Use Section 6 → implement each module
5. Use Section 7 → apply design system
6. Use Section 8 → deploy on Vercel
7. Use Section 10 → test with sample data
8. Use Section 12 → push to GitHub

---

## 14. Final Deliverables Checklist

- [ ] Flask app with upload route
- [ ] Template rendering with `{{placeholders}}`  
- [ ] Sequential PDF generation (single-threaded)
- [ ] Parallel PDF generation (multiprocessing.Pool)
- [ ] Time measurement for both modes
- [ ] Speedup calculation (S = T_seq / T_par)
- [ ] Efficiency calculation (E = S / cores)
- [ ] Amdahl's Law theoretical max calculation
- [ ] matplotlib comparison chart
- [ ] ZIP download of all PDFs
- [ ] Tailwind v4 styled UI
- [ ] vercel.json deployment config
- [ ] requirements.txt
- [ ] README with screenshots
- [ ] Push to GitHub
- [ ] Submit to sir
