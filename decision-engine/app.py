from flask import Flask, request, jsonify
import requests
import os
import time
from dotenv import load_dotenv   

load_dotenv()                     


app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# Keeps track of alerts we've already sent recently, to avoid spamming duplicates
recent_alerts = {}
DEDUP_WINDOW_SECONDS = 60


def send_telegram_message(text):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials missing. Message would have been:\n", text)
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        r = requests.post(url, json=payload, timeout=5)
        print("Telegram response:", r.status_code, r.text)
    except Exception as e:
        print("Failed to send Telegram message:", e)


def is_duplicate(fingerprint):
    now = time.time()
    last_seen = recent_alerts.get(fingerprint)
    if last_seen and (now - last_seen) < DEDUP_WINDOW_SECONDS:
        return True
    recent_alerts[fingerprint] = now
    return False


@app.route('/alert', methods=['POST'])
def receive_alert():
    data = request.get_json(force=True)
    alerts = data.get('alerts', [])
    print(f"Received {len(alerts)} alert(s) from Alertmanager")

    for alert in alerts:
        status = alert.get('status')
        labels = alert.get('labels', {})
        annotations = alert.get('annotations', {})
        fingerprint = alert.get('fingerprint', labels.get('alertname', 'unknown'))

        alertname = labels.get('alertname', 'Unknown alert')
        severity = labels.get('severity', 'info')
        summary = annotations.get('summary', '')
        description = annotations.get('description', '')

        if status == 'firing':
            if is_duplicate(fingerprint):
                print(f"Duplicate suppressed: {alertname}")
                continue
            icon = "🔴" if severity == 'critical' else "🟠"
            message = f"{icon} *{alertname}*\nSeverity: {severity}\n{summary}\n{description}"
        else:
            icon = "✅"
            message = f"{icon} *Resolved: {alertname}*\n{summary}"

        send_telegram_message(message)

    return jsonify({"status": "processed"}), 200


@app.route('/health')
def health():
    return jsonify({"status": "ok"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)