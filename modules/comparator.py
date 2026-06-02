import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


class ComparisonResult:
    def __init__(self, seq_time, par_times, num_rows):
        self.seq_time = seq_time
        self.par_times = par_times
        self.num_rows = num_rows

    def get_worker_table_data(self):
        data = []
        for workers, par_time in sorted(self.par_times.items()):
            speedup = round(self.seq_time / par_time, 2) if par_time > 0 else 0
            efficiency = round(speedup / workers, 2) if workers > 0 else 0
            amdahl_limit = round(1 / (0.1 + 0.9 / workers), 2)
            data.append({
                'workers': workers,
                'sequential_time': round(self.seq_time, 3),
                'parallel_time': round(par_time, 3),
                'speedup': speedup,
                'efficiency': efficiency,
                'amdahl_limit': amdahl_limit,
            })
        return data

    def generate_bar_chart(self, path):
        workers = sorted(self.par_times.keys())
        seq_times = [self.seq_time] * len(workers)
        par_times = [self.par_times[w] for w in workers]
        speedups = [round(self.seq_time / self.par_times[w], 2) for w in workers]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        fig.patch.set_facecolor('#0c1222')

        x = np.arange(len(workers))
        w = 0.3

        ax1.bar(x - w/2, seq_times, w, label='Sequential', color='#f97316', edgecolor='none')
        ax1.bar(x + w/2, par_times, w, label='Parallel', color='#10b981', edgecolor='none')
        ax1.set_xlabel('Workers', fontsize=11, color='#94a3b8')
        ax1.set_ylabel('Time (s)', fontsize=11, color='#94a3b8')
        ax1.set_title('Time Comparison', fontsize=13, fontweight='bold', color='#e2e8f0')
        ax1.set_xticks(x)
        ax1.set_xticklabels([str(w) for w in workers], fontsize=10, color='#94a3b8')
        ax1.legend(fontsize=10, facecolor='#1e293b', edgecolor='#1e293b', labelcolor='#e2e8f0')
        ax1.set_facecolor('#0c1222')
        ax1.tick_params(colors='#94a3b8')
        ax1.spines['bottom'].set_color('#1e293b')
        ax1.spines['left'].set_color('#1e293b')
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)

        ax2.bar(x, speedups, w, color='#10b981', edgecolor='none')
        ax2.axhline(y=1, color='#f97316', linestyle='--', linewidth=1, alpha=0.7)
        ax2.set_xlabel('Workers', fontsize=11, color='#94a3b8')
        ax2.set_ylabel('Speedup (x)', fontsize=11, color='#94a3b8')
        ax2.set_title('Speedup Comparison', fontsize=13, fontweight='bold', color='#e2e8f0')
        ax2.set_xticks(x)
        ax2.set_xticklabels([str(w) for w in workers], fontsize=10, color='#94a3b8')
        ax2.set_facecolor('#0c1222')
        ax2.tick_params(colors='#94a3b8')
        ax2.spines['bottom'].set_color('#1e293b')
        ax2.spines['left'].set_color('#1e293b')
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)

        plt.tight_layout()
        plt.savefig(path, dpi=120, bbox_inches='tight', facecolor='#0c1222')
        plt.close()
