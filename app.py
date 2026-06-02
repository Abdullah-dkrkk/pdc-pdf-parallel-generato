import os
import uuid
import shutil
import zipfile
import pandas as pd
from flask import Flask, request, jsonify, render_template, send_file, url_for

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['OUTPUT_FOLDER'] = os.path.join(os.path.dirname(__file__), 'output')
app.config['CHARTS_FOLDER'] = os.path.join(os.path.dirname(__file__), 'charts')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs(app.config['CHARTS_FOLDER'], exist_ok=True)

tasks = {}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    if 'data_file' not in request.files:
        return jsonify({'error': 'No data file uploaded'}), 400
    data_file = request.files['data_file']
    if data_file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    task_id = str(uuid.uuid4())[:8]
    task_dir = os.path.join(app.config['OUTPUT_FOLDER'], task_id)
    os.makedirs(task_dir, exist_ok=True)
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{task_id}_{data_file.filename}")
    data_file.save(upload_path)
    tasks[task_id] = {
        'status': 'processing',
        'progress': 0,
        'task_dir': task_dir,
        'upload_path': upload_path,
        'result': None
    }
    try:
        if upload_path.endswith('.csv'):
            df = pd.read_csv(upload_path)
        else:
            df = pd.read_excel(upload_path)
        rows = df.to_dict(orient='records')
        num_rows = len(rows)
        from modules.sequential import process_sequential
        from modules.parallel import process_parallel_thread
        from modules.comparator import ComparisonResult
        import time
        seq_dir = os.path.join(task_dir, 'sequential')
        os.makedirs(seq_dir, exist_ok=True)
        tasks[task_id]['progress'] = 10
        seq_time = process_sequential(rows, seq_dir)
        tasks[task_id]['progress'] = 40
        par_times = {}
        worker_counts_to_run = [1, 2, 4]
        for wc in worker_counts_to_run:
            if wc > num_rows:
                continue
            par_dir = os.path.join(task_dir, f'parallel_{wc}')
            os.makedirs(par_dir, exist_ok=True)
            t = process_parallel_thread(rows, par_dir, wc)
            par_times[wc] = t
            tasks[task_id]['progress'] = min(40 + int(50 * (worker_counts_to_run.index(wc) + 1) / len(worker_counts_to_run)), 90)
        result = ComparisonResult(seq_time, par_times, num_rows)
        chart_path = os.path.join(app.config['CHARTS_FOLDER'], f'{task_id}.png')
        result.generate_bar_chart(chart_path)
        tasks[task_id]['progress'] = 95
        zip_path = os.path.join(task_dir, 'all_reports.zip')
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for folder_name in os.listdir(task_dir):
                folder_path = os.path.join(task_dir, folder_name)
                if os.path.isdir(folder_path) and folder_name != 'all_reports.zip':
                    for fname in os.listdir(folder_path):
                        if fname.endswith('.pdf'):
                            file_path = os.path.join(folder_path, fname)
                            arcname = f"{folder_name}/{fname}"
                            zf.write(file_path, arcname)
        tasks[task_id].update({
            'status': 'completed',
            'progress': 100,
            'result': {
                'task_id': task_id,
                'num_rows': num_rows,
                'sequential_time': round(seq_time, 3),
                'parallel_times': {str(k): round(v, 3) for k, v in par_times.items()},
                'worker_data': result.get_worker_table_data(),
                'chart_url': url_for('chart', task_id=task_id),
                'download_url': url_for('download', task_id=task_id),
            }
        })
        os.remove(upload_path)
        return jsonify({'task_id': task_id, 'status': 'completed', 'result': tasks[task_id]['result']})
    except Exception as e:
        tasks[task_id]['status'] = 'error'
        tasks[task_id]['error'] = str(e)
        return jsonify({'error': str(e)}), 500


@app.route('/status/<task_id>')
def status(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    return jsonify(task)


@app.route('/download/<task_id>')
def download(task_id):
    task = tasks.get(task_id)
    if not task or not task.get('result'):
        return jsonify({'error': 'Task not found'}), 404
    zip_path = os.path.join(task['task_dir'], 'all_reports.zip')
    if not os.path.exists(zip_path):
        return jsonify({'error': 'File not found'}), 404
    return send_file(zip_path, as_attachment=True, download_name=f'reports_{task_id}.zip')


@app.route('/sample/<path:filename>')
def sample_file(filename):
    sample_dir = os.path.join(os.path.dirname(__file__), 'sample')
    return send_file(os.path.join(sample_dir, filename))

@app.route('/chart/<task_id>')
def chart(task_id):
    chart_path = os.path.join(app.config['CHARTS_FOLDER'], f'{task_id}.png')
    if not os.path.exists(chart_path):
        return jsonify({'error': 'Chart not found'}), 404
    return send_file(chart_path, mimetype='image/png')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
