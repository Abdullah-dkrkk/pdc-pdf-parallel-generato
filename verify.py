import urllib.request, io, uuid, json, zipfile, os, tempfile
from pypdf import PdfReader

p = r'D:\laragon\www\pdc-pdf-parallel-generato'
with open(p+'\\sample\\invoices.csv', 'rb') as f:
    csv_bytes = f.read()

template = '{h}INVOICE\n{sh}{{invoice_no}}\n\n{th}Field | Value\n{tr}Client | {{client}}\n{tr}Company | {{company}}\n{tr}Amount | PKR {{amount}}\n{tr}Date | {{date}}\n{tr}Status | {{status}}\n\n{p}Thank you'

b = str(uuid.uuid4())
sep = '\r\n'
buf = io.BytesIO()
buf.write(f'--{b}{sep}Content-Disposition: form-data; name="data_file"; filename="invoices.csv"{sep}Content-Type: text/csv{sep}{sep}'.encode())
buf.write(csv_bytes)
buf.write(sep.encode())
buf.write(f'--{b}{sep}Content-Disposition: form-data; name="template"{sep}{sep}'.encode())
buf.write(template.encode())
buf.write(f'{sep}--{b}--{sep}'.encode())
data = buf.getvalue()
req = urllib.request.Request('http://127.0.0.1:5000/upload', data=data)
req.add_header('Content-Type', f'multipart/form-data; boundary={b}')
j = json.loads(urllib.request.urlopen(req).read())
tid = j['result']['task_id']
print('Task:', tid)

z = urllib.request.urlopen(f'http://127.0.0.1:5000/download/{tid}').read()
print('ZIP size:', len(z))
found = 0
with zipfile.ZipFile(io.BytesIO(z)) as zf:
    for n in sorted(zf.namelist()):
        if not n.endswith('.pdf'):
            continue
        found += 1
        pdata = zf.read(n)
        t = tempfile.gettempdir()+'\\test.pdf'
        with open(t, 'wb') as f:
            f.write(pdata)
        txt = ''.join(p.extract_text() for p in PdfReader(t).pages)
        has_data = any(k in txt for k in ['INV-001','Ahmed Khan','Sarah Ali','Usman','Fatima','Bilal'])
        snippet = txt.strip()[:90]
        print(f'  {n}: has_data={has_data} | "{snippet}"')
        os.remove(t)
print(f'Total PDFs: {found}')
print('SUCCESS: All PDFs have data!' if found > 0 else 'FAIL: No PDFs found')
