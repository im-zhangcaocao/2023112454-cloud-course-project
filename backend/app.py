import os
import redis
import pandas as pd
import numpy as np
from flask import Flask, jsonify, request

app = Flask(__name__)

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", "")

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD if REDIS_PASSWORD else None,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5,
)


@app.route("/api/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok"})


@app.route("/api/health", methods=["GET"])
def health():
    try:
        redis_client.ping()
        redis_status = "connected"
    except Exception:
        redis_status = "disconnected"
    return jsonify({"redis": redis_status, "service": "backend"})


@app.route("/api/counter", methods=["GET"])
def counter():
    try:
        count = redis_client.incr("visit_counter")
        return jsonify({"visits": count})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/data", methods=["POST"])
def store_data():
    try:
        data = request.get_json()
        if not data or "key" not in data or "value" not in data:
            return jsonify({"error": "key and value required"}), 400
        redis_client.set(data["key"], data["value"])
        return jsonify({"status": "stored", "key": data["key"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/data/<key>", methods=["GET"])
def get_data(key):
    try:
        value = redis_client.get(key)
        if value is None:
            return jsonify({"error": "key not found"}), 404
        return jsonify({"key": key, "value": value})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/stats", methods=["GET"])
def compute_stats():
    try:
        df = pd.DataFrame({
            "x": np.random.randn(100),
            "y": np.random.randn(100),
        })
        stats = {
            "x_mean": float(df["x"].mean()),
            "x_std": float(df["x"].std()),
            "y_mean": float(df["y"].mean()),
            "y_std": float(df["y"].std()),
            "correlation": float(df["x"].corr(df["y"])),
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)