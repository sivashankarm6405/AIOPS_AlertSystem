# AIOps Alert System

A small alerting pipeline that detects a problem automatically and sends a message straight to Telegram — no manual checking needed.

## How it works

Sample App → Prometheus → Alert Rule → Alertmanager → Decision Engine → Telegram

1. **Sample App** — a Flask app exposing a fake CPU metric, with `/spike/on` and `/spike/off` to simulate a problem on demand.
2. **Prometheus** — scrapes the metric every 5 seconds and checks it against a rule (CPU > 80% for 10s).
3. **Alertmanager** — receives firing alerts from Prometheus and routes them to a webhook.
4. **Decision Engine** — a small Flask service that receives the alert, filters out duplicates, and sends a formatted message to Telegram.
5. **Telegram** — delivers the final alert to a chat.

## Folder structure
sample-app/ Flask app with the fake CPU metric
prometheus/ Scrape config and alert rule
alertmanager/ Routing config, forwards to decision-engine
decision-engine/ Receives alerts, filters out repeats, sends to Telegram


## Setup

1. Each folder with a `requirements.txt` needs its own virtual environment and `pip install -r requirements.txt`.
2. In `decision-engine`, copy `.env.example` to `.env` and fill in your own Telegram bot token and chat ID.
3. Run each component in its own terminal: `sample-app` (`python app.py`), `prometheus` (`prometheus.exe --config.file=prometheus.yml`), `alertmanager` (`alertmanager.exe --config.file=alertmanager.yml`), `decision-engine` (`python app.py`).
4. Trigger a test: `curl http://localhost:5000/spike/on`, wait ~20 seconds, check Telegram.

## What makes this "AIOps"

The decision engine is the intelligence layer between raw alerting and notification — it suppresses duplicate alerts within a time window before anything reaches Telegram. This can be extended with real anomaly detection (e.g. rolling average + standard deviation) instead of a fixed threshold.
