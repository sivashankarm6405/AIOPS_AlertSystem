from flask import Flask, Response, jsonify
from prometheus_client import Gauge, generate_latest, CONTENT_TYPE_LATEST
import random
import time
import threading

app = Flask(__name__)

# This is the metric Prometheus will scrape.
cpu_usage = Gauge('simulated_cpu_usage_percent', 'Simulated CPU usage percentage')

spike_active = False


def update_metric_loop():
    """Background thread: keeps the metric moving so it looks like a real service."""
    global spike_active
    while True:
        if spike_active:
            cpu_usage.set(random.uniform(90, 99))
        else:
            cpu_usage.set(random.uniform(10, 30))
        time.sleep(2)


threading.Thread(target=update_metric_loop, daemon=True).start()


@app.route('/metrics')
def metrics():
    """Prometheus scrapes this endpoint."""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@app.route('/spike/on')
def spike_on():
    """Simulate a problem: CPU usage jumps to 90-99%."""
    global spike_active
    spike_active = True
    return jsonify({"status": "spike started", "simulated_cpu": "90-99%"})


@app.route('/spike/off')
def spike_off():
    """Go back to normal CPU usage."""
    global spike_active
    spike_active = False
    return jsonify({"status": "spike stopped", "simulated_cpu": "10-30%"})


@app.route('/')
def home():
    return jsonify({"service": "sample-app", "status": "running", "spike_active": spike_active})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)