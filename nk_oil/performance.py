"""Wall time and sampled process RSS. Sampling may miss short-lived peaks."""
import threading
import time

import psutil


def measure(function, *args, **kwargs):
    process = psutil.Process()
    baseline = process.memory_info().rss
    samples = [baseline]
    stop = threading.Event()

    def poll():
        while not stop.wait(.01):
            samples.append(process.memory_info().rss)

    worker = threading.Thread(target=poll, daemon=True)
    worker.start()
    started = time.perf_counter()
    try:
        result = function(*args, **kwargs)
    finally:
        seconds = time.perf_counter() - started
        samples.append(process.memory_info().rss)
        stop.set()
        worker.join()
    return result, {'wall_seconds': seconds, 'rss_baseline_mb': baseline / 1e6,
                    'sampled_peak_rss_mb': max(samples) / 1e6,
                    'rss_increment_mb': (max(samples) - baseline) / 1e6}
