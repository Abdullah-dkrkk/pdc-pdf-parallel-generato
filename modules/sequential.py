import time
from .pdf_generator import generate_pdf


def process_sequential(rows, output_dir):
    start = time.perf_counter()
    for i, row in enumerate(rows):
        generate_pdf(row, output_dir, f'report_{i+1}.pdf')
    return time.perf_counter() - start
