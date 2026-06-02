# Parallel PDF Generator — PDC Project

## Yeh Project Kya Hai? (What is this?)

Yeh ek **Flask + Python** ka web app hai jo **CSV file upload** karke uski har row ke liye **professional PDFs generate karta hai** — aur sath hi **sequential vs parallel processing ka performance comparison** bhi dikhata hai.

**Simple words mein:** Aap ek file daalte ho jisme data ho (jaise invoice records, student marks, salary slips). Yeh app uski har row ka alag PDF banata hai. Phir dikhata hai ke kitne PDFs ek saath (parallel) banaye to kitna speedup milta hai.

---

## Ye Kaam Kaise Karta Hai? (Real Life Example)

**Real Life Example:** Socho aapko 100 letters likhne hain.

- **Sequential (ek ek karke):** Aap 1 letter likhte ho, envelope mein band karte ho, uske baad hi agla letter shuru karte ho. Kaafi time lagta hai.
- **Parallel (sath sath):** Aap 4 doston ko bula lo. Har dost 25 letters likhta hai. Kaam 4x fast ho jata hai (ideal case mein).

**Yeh app yahi karti hai:** Ek CSV (jisme 5 row hain) upload karo. App:
1. Sequential tareeke se 5 PDFs banati hai — ek khatam to agla (time measure karti hai)
2. Parallel tareeke se bhi 5 PDFs banati hai — 2 workers, 4 workers ke saath (time measure karti hai)
3. Compare karti hai: kitna speedup mila?
4. Aapko sab PDFs ka ek ZIP file deti hai + comparison chart deti hai

---

## App Ka Flow (Step by Step — Upload to Download)

```
MAIN PAGE (index.html)
    │
    ├── User ne CSV file select ki (jaise invoices.csv)
    │
    ├── "Generate PDFs" button dabaya
    │
    ▼
UPLOAD ROUTE (/upload → app.py)
    │
    ├── File save hoti hai uploads/ folder mein
    ├── Pandas CSV/Excel padh leta hai → rows ki list banata hai
    │   └── Har row = ek dict (jaise: {"invoice_no": "INV-001", "client": "Ahmed Khan", ...})
    │
    ├── SEQUENTIAL PROCESSING
    │   └── process_sequential() → ek loop, har row ka PDF banao
    │       └── Har row ke liye: generate_pdf() call → modules/pdf_generator.py
    │           └── Green header + auto table + green footer wala PDF banta hai
    │
    ├── PARALLEL PROCESSING (worker count 1, 2, 4 ke saath)
    │   └── process_parallel() → rows ko chunks mein baant kar workers ko de deta hai
    │       └── Har worker apne chunk ki rows ke PDF banata hai (sath sath)
    │
    ├── COMPARISON
    │   └── ComparisonResult object → speedup, efficiency, Amdahl limit calculate
    │   └── generate_bar_chart() → matplotlib se comparison chart banta hai
    │
    ├── ZIP CREATION
    │   └── output/{task_id}/ ka har subfolder (sequential/, parallel_1/, etc.)
    │       ZIP mein add hota hai → all_reports.zip
    │
    └── JSON RESPONSE → browser ko result bhejta hai
        │
        ▼
RESULTS SHOW ON PAGE
    ├── 4 METRIC CARDS: Rows, Seq Time, Best Par Time, Best Speedup
    ├── PERFORMANCE TABLE: Workers × Time × Speedup × Efficiency
    ├── COMPARISON CHART: Bar chart image
    └── DOWNLOAD BUTTON: ZIP download karo
```

---

## Files Aur Unka Kaam (File-by-File Explanation)

### 1. `app.py` — Yeh App Ka Boss Hai (Main Server)

Yeh Flask server hai. Jab aap browser mein `localhost:5000` kholte ho to yeh page serve karta hai. Routes:

| Route | Matlab | Kya karta hai |
|-------|--------|--------------|
| `GET /` | Home page | `index.html` serve karta hai |
| `POST /upload` | File upload | CSV/Excel accept karta hai, processing chala ta hai, ZIP banata hai |
| `GET /status/<id>` | Status check | Processing progress batata hai (0% → 100%) |
| `GET /download/<id>` | ZIP download | Aapko ZIP file deta hai |
| `GET /chart/<id>` | Chart image | Comparison chart PNG serve karta hai |
| `GET /sample/<file>` | Sample CSVs | Sample CSV files download karne deta hai |

**`upload()` function ka flow:**

1. File aayi → `uploads/{task_id}_filename.csv` save kiya
2. Pandas ne file padha → `df.to_dict(orient='records')` → rows ki list
3. Sequential chala: `process_sequential(rows, output_dir)`
4. Parallel chala: har worker count (1,2,4) ke liye `process_parallel()`
5. ComparisonResult ne analysis kiya
6. Chart generate kiya
7. ZIP bana kar sab folders daal diye
8. Task status "completed" kar diya
9. JSON response bhej diya

---

### 2. `modules/pdf_generator.py` — PDF Banane Wali Machine

Yeh actual PDF banata hai using **ReportLab** library.

#### `_detect_info(row)` — Document Type Pata Karta Hai

Ek row of data leta hai aur CSV column names dekh kar decide karta hai:

- Agar column mein "invoice" hai → **INVOICE** → Footer: "Thank you for your business"
- Agar "marks", "grade", "roll_no", "subject" hai → **STUDENT REPORT** → Footer: "Best wishes for your future"
- Agar "emp_id", "net_pay", "deductions" hai → **SALARY REPORT** → Footer: "This is a computer-generated statement"
- Kuch nahi mila → **REPORT** → Footer: "Thank you"

**Real life example:** Jaise aap kisi ko uske dress se pahchan te ho (uniform = student, suit = office wala), waise hi yeh CSV column names se document type pata karta hai.

#### `generate_pdf(row, output_dir, filename)` — PDF Ka Map

Har row ke liye ek PDF banata hai. Structure aisa hai:

```
┌──────────────────────────────────────┐
│         INVOICE (Green BG)            │  ← Header (95px height)
├──────────────────────────────────────┤
│            INV-001                    │  ← Subtitle (invoice no / name)
├──────────────────────────────────────┤
│  Field           │ Value             │
│  ────────────────┼────────────────── │
│  invoice_no      │ INV-001           │  ← Auto table (sab columns)
│  client          │ Ahmed Khan        │     2 columns: Field | Value
│  company         │ Tech Solutions PK │     Green header row
│  amount          │ 1,50,000         │     Alternating row colors
│  date            │ 2026-05-01        │     Grid lines
│  status          │ Paid              │
├──────────────────────────────────────┤
│    Thank you for your business       │  ← Footer message
├──────────────────────────────────────┤
│         INVOICE (Green BG)            │  ← Footer (50px height)
└──────────────────────────────────────┘
```

**Colors jo use hote hain:**
- Green: `#059669` (header, footer, table header)
- Light bg: `#f1f5f9` (alternating rows)
- Border: `#cbd5e1` (table grid)
- Text: `#1e293b` (dark slate)
- Muted: `#64748b` (subtitle, message)

---

### 3. `modules/sequential.py` — Ek Ek Karke Kaam

```
process_sequential(rows, output_dir):
    start_time = abhi ka time
    for i, row in enumerate(rows):
        generate_pdf(row, output_dir, f'report_{i+1}.pdf')
    total_time = abhi ka time - start_time
    return total_time
```

- Ek simple loop hai
- Pehla PDF banao, khatam hone do, phir agla shuru karo
- Time measure karta hai poori process ka
- Files: `report_1.pdf`, `report_2.pdf`, ..., `report_N.pdf`

---

### 4. `modules/parallel.py` — Sath Sath Kaam

#### `_process_chunk(args)` — Worker Ka Kaam
- Ek worker ko chunk milta hai (jaise rows 0-4)
- Woh apne chunk ki saari rows ke PDF banata hai

#### `process_parallel(rows, output_dir, workers)` — ProcessPoolExecutor
- Rows ko `workers` chunks mein baant deta hai
- Har chunk alag **process** ko milta hai
- Saare processes sath sath chaltay hain (true parallelism)
- **Process = alag alag program ki tarah** (apna memory, apni CPU)

#### `process_parallel_thread(rows, output_dir, workers)` — ThreadPoolExecutor
- Same as above, lekin processes ki jagah **threads** use karta hai
- **Thread = ek program ke andar multiple kaam** (memory share karte hain)
- Vercel (cloud) pe deploy karne ke liye fallback hai

**Real Life Example:**
- **Process =** 4 alag alag kitchens mein 4 log khana bana rahe hain (har kitchen apna stove, apna bartan)
- **Thread =** 1 kitchen mein 4 log milkar khana bana rahe hain (1 stove, 1 bartan share karte hain — conflicts ho sakte hain)

---

### 5. `modules/comparator.py` — Comparison Engine

#### `ComparisonResult` class:

`__init__(seq_time, par_times, num_rows)`:
- Store karta hai sequential time, parallel times, row count

`get_worker_table_data()`:
- Har worker count ke liye calculate karta hai:

| Metric | Formula | Matlab |
|--------|---------|--------|
| **Speedup** | `seq_time / par_time` | Parallel kitna fast hai? 2x = do guna fast |
| **Efficiency** | `Speedup / workers` | Har worker kitna efficient hai? 1.0 = perfect |
| **Amdahl Limit** | `1 / (0.1 + 0.9/w)` | Theoretical max speedup (assumes 90% parallelizable) |

**Real Life Example (Speedup):** 
- Agar 1 aadmi 100 letters 100 minute mein likhta hai
- 4 log sath sath likhein to 25 minute lagte hain
- Speedup = 100/25 = **4x**
- Efficiency = 4/4 = **1.0** (perfect)

**Amdahl's Law simple words mein:**
- Kuch kaam aise hote hain jo parallel nahi ho sakte (jaise letter pe sign karna — sirf 1 aadmi kar sakta hai)
- Amdahl ka law batata hai ke kitna bhi parallel karo, us non-parallelizable part ki wajah se maximum speedup limited hota hai
- Formula: `1 / ((1-P) + P/N)` jahan P = parallel fraction, N = workers

`generate_bar_chart(path)`:
- **matplotlib** library use karta hai
- Dark theme mein 2 charts banata hai:
  1. **Time Comparison:** Sequential (orange) vs Parallel (green) bars
  2. **Speedup Comparison:** Green bars showing speedup per worker count

---

### 6. `templates/index.html` — Frontend Page

Yeh user ko dikhta hai. Tailwind CSS use karta hai styling ke liye.

**Sections:**
1. **Upload form:** Sirf file input (template textarea remove kar diya)
2. **4 Metric Cards:** Rows, Sequential Time, Best Parallel Time, Best Speedup
3. **Performance Table:** Har worker count ka data
4. **Chart Image:** Matplotlib se generate hua comparison chart
5. **Download Button:** ZIP download karne ke liye

**JavaScript functions:**
- `updateFileName()` → File select karne par naam dikhana
- Form submit → POST `/upload` with FormData
- `pollStatus(taskId)` → Har 800ms status check karna
- `showResults(result)` → 4 cards + table + chart + download update karna

---

### 7. `static/css/style.css` — Styling Rules

Dark theme ke design tokens. Colors, fonts, spacing, shadows sab defined hain.

---

### 8. Sample CSVs

| File | Columns | Use |
|------|---------|-----|
| `sample/invoices.csv` | invoice_no, client, company, amount, date, status | Invoice PDF ke liye |
| `sample/students.csv` | name, class, roll_no, subject, marks, grade | Student Report PDF ke liye |
| `sample/salary.csv` | emp_id, name, designation, month, year, basic, allowances, deductions, net_pay | Salary Slip PDF ke liye |

---

## ZIP Mein Kya Aata Hai? (Output Structure)

Jab aap "Download All PDFs" button dabate ho to ZIP file aati hai. Andar yeh hota hai:

```
reports_abc12345.zip
│
├── sequential/            ← Sequential processing se bani PDFs
│   ├── report_1.pdf        (1st row ka data)
│   ├── report_2.pdf        (2nd row ka data)
│   ├── report_3.pdf        (3rd row ka data)
│   ├── report_4.pdf        (4th row ka data)
│   └── report_5.pdf        (5th row ka data)
│
├── parallel_1/            ← 1 worker ke saath parallel processing
│   ├── report_1.pdf
│   ├── report_2.pdf
│   └── ...
│
├── parallel_2/            ← 2 workers ke saath parallel
│   ├── report_1.pdf
│   └── ...
│
└── parallel_4/            ← 4 workers ke saath parallel
    ├── report_1.pdf
    └── ...
```

**Har folder mein EXACT same PDFs hote hain** (same data, same look). Farq sirf itna hai ke kaise bane hain — sequential vs parallel.

**parallel_1 kyun hai?** — Parallel framework ka overhead (extra cost) dikhane ke liye. Sequential mein overhead nahi hai, parallel_1 mein process spawn karne ka overhead hai. Isse aap dekh sakte ho ke parallel infrastructure kitna additional time leta hai even with 1 worker.

---

## 4 Metric Cards — Kya Dikhati Hain?

| Card | Value | Matlab |
|------|-------|--------|
| **Rows Processed** | 5 | Total rows in CSV |
| **Sequential Time** | 2.5s | Time to make all PDFs one-by-one |
| **Best Parallel Time** | 0.8s | Best time among all parallel runs (e.g., 4 workers) |
| **Best Speedup** | 3.12x | Seq Time ÷ Best Par Time = how many times faster |

---

## Performance Table — Kya Dikhati Hai?

| Workers | Sequential (s) | Parallel (s) | Speedup | Efficiency | Amdahl Limit |
|---------|---------------|--------------|---------|------------|-------------|
| 1 | 2.5 | 2.7 | 0.93x | 0.93 | 1.00x |
| 2 | 2.5 | 1.4 | 1.79x | 0.89 | 1.82x |
| 4 | 2.5 | 0.8 | 3.12x | 0.78 | 3.08x |

- **Speedup:** Sequential time ÷ Parallel time (jaise 3.12x = 3.12 guna zyada fast)
- **Efficiency:** Speedup ÷ Workers (1.0 = perfect, 0.5 = half efficient)
- **Amdahl Limit:** Theoretical maximum speedup (90% parallelizable maan kar)

---

## Comparison Chart — Kya Dikhati Hai?

**Left side (Time Comparison):**
- Orange bars = Sequential time (har worker group ke liye same height)
- Green bars = Parallel time (ghat ta hai jaise workers badhte hain)
- Dikhata hai ke parallel time progressively kam hota hai

**Right side (Speedup Comparison):**
- Green bars = Speedup ratio (seq_time ÷ par_time)
- Orange dashed line = y=1 baseline (no speedup)
- Bar jaise upar jata hai, means better speedup

**matplotlib** library use hoti hai chart banane ke liye. Dark background (`#0c1222`) pe chart banta hai.

---

## Important Technical Concepts (Simple Language Mein)

### 1. Sequential vs Parallel Processing

| Aspect | Sequential | Parallel |
|--------|-----------|----------|
| **Tareeqa** | Ek kaam karo, phir agla | Ek saath kaam karo |
| **Speed** | Slow (1 worker) | Fast (multiple workers) |
| **Complexity** | Simple code | Complex (chunking, sync) |
| **Overhead** | None | Extra (spawning workers) |
| **Use case** | Simple tasks | Heavy/CPU-intensive tasks |

### 2. Process vs Thread

- **Process:** Alag program ki tarah. Apna memory, apna CPU. Pickle serialization hoti hai data transfer ke liye. Bada overhead. True parallelism. 
- **Thread:** Ek program ke andar. Memory share karte hain. Chhota overhead. GIL ki wajah se limited parallelism (Python mein).

### 3. Amdahl's Law

**Simple example:** Ek car banane mein 100 steps hain. 90 steps parallel ho sakte hain (4 log milkar karein), lekin 10 steps sequential hain (1 aadmi hi kar sakta hai).

- Maximum speedup = 1 / (0.1 + 0.9/4) = 3.08x
- Chahe 100 workers bhi daal do, 10x se zyada speedup nahi mile ga
- Yeh Amdahl's Law hai — jo bata ta hai ke parallelization ki limited hai

### 4. Speedup vs Efficiency

- **Speedup:** Kitna fast? (seq_time / par_time)
- **Efficiency:** Kitna effectively use ho rahe hain workers? (speedup / workers)
- Agar 4 workers de kar sirf 2x speedup mil raha hai → efficiency = 0.5 (50%)

---

## Setup Kaise Karein?

```bash
# 1. Requirements install karo
pip install -r requirements.txt

# 2. App chalao
py app.py

# 3. Browser mein kholo
http://localhost:5000
```

---

## Repo Links

GitHub: [https://github.com/Abdullah-dkrkk/pdc-pdf-parallel-generato](https://github.com/Abdullah-dkrkk/pdc-pdf-parallel-generato)
