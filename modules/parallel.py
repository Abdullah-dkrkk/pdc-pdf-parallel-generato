import time
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from .pdf_generator import generate_pdf


def _process_chunk(args):
    rows, output_dir, start_idx = args
    for i, row in enumerate(rows):
        generate_pdf(row, output_dir, f'report_{start_idx+i+1}.pdf')


def process_parallel(rows, output_dir, workers):
    start = time.perf_counter()
    chunk_size = max(1, len(rows) // workers)
    chunks = []
    for i in range(0, len(rows), chunk_size):
        chunk = rows[i:i+chunk_size]
        chunks.append((chunk, output_dir, i))
    with ProcessPoolExecutor(max_workers=workers) as pool:
        pool.map(_process_chunk, chunks)
    return time.perf_counter() - start


def process_parallel_thread(rows, output_dir, workers):
    start = time.perf_counter()
    chunk_size = max(1, len(rows) // workers)
    chunks = []
    for i in range(0, len(rows), chunk_size):
        chunk = rows[i:i+chunk_size]
        chunks.append((chunk, output_dir, i))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        pool.map(_process_chunk, chunks)
    return time.perf_counter() - start
