from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os
import re
import socket

app = Flask(__name__, static_folder=None)
CORS(app)

DB_PATH = "/data/bestenliste.db"

BLOCKED = [
    "adolf", "hitler", "nazi", "heil",
    "badass", "pussy", "fuck", "shit", "bitch", "dick", "cock", "cunt",
    "porn", "pornhub", "xvideos", "xnxx",
    "drogen", "drug", "cocaine", "kokain", "heroin", "meth", "crack",
    "terror", "bombe", "isis",
    "fick", "ficker", "schlampe", "hure", "fotze", "muschi", "wichser",
    "arschloch", "scheisse", "vergewaltig", "kindersch",
    "bastard", "motherfucker",
]

def name_ok(name):
    name_lower = name.lower()
    for b in BLOCKED:
        if b in name_lower:
            return False
    return True

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    conn.execute("CREATE TABLE IF NOT EXISTS scores (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, punkte INTEGER NOT NULL, max INTEGER NOT NULL, prozent INTEGER NOT NULL, zeit TEXT NOT NULL, datum TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    conn.commit()
    conn.close()

init_db()

# Migration: fehlende Spalte "zeit" nachtragen (alte DB ohne diese Spalte)
try:
    conn = get_db()
    conn.execute("SELECT zeit FROM scores LIMIT 1")
    conn.close()
except sqlite3.OperationalError:
    conn.execute("ALTER TABLE scores ADD COLUMN zeit TEXT NOT NULL DEFAULT ''")
    conn.commit()
    conn.close()

# Alte Namen mit unzulaessigen Begriffen loeschen
conn = get_db()
alle = conn.execute("SELECT id, name FROM scores").fetchall()
for row in alle:
    if not name_ok(row["name"]):
        conn.execute("DELETE FROM scores WHERE id = ?", (row["id"],))
conn.commit()
conn.close()

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

@app.route("/api/score", methods=["POST"])
def add_score():
    data = request.get_json()
    name = data.get("name", "").strip()
    punkte = data.get("punkte", 0)
    max_fragen = data.get("max", 1)
    zeit = data.get("zeit", "")
    prozent = round((punkte / max_fragen) * 100) if max_fragen else 0

    if not name or not punkte:
        return jsonify({"error": "Name und Punkte erforderlich"}), 400

    if not name_ok(name):
        return jsonify({"error": "Name enthaelt unzulaessige Begriffe"}), 400

    conn = get_db()
    vorhanden = conn.execute("SELECT id FROM scores WHERE name = ?", (name,)).fetchone()
    if vorhanden:
        conn.execute("UPDATE scores SET punkte = ?, max = ?, prozent = ?, zeit = ?, datum = CURRENT_TIMESTAMP WHERE id = ?",
                     (punkte, max_fragen, prozent, zeit, vorhanden["id"]))
    else:
        conn.execute("INSERT INTO scores (name, punkte, max, prozent, zeit) VALUES (?, ?, ?, ?, ?)",
                     (name, punkte, max_fragen, prozent, zeit))
    conn.commit()
    conn.close()
    return jsonify({"ok": True}), 201

@app.route("/api/leaderboard", methods=["GET"])
def get_leaderboard():
    conn = get_db()
    rows = conn.execute("SELECT name, punkte, max, prozent, zeit, datum FROM scores ORDER BY prozent DESC, punkte DESC, datum ASC LIMIT 20").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/serverinfo", methods=["GET"])
def server_info():
    return jsonify({"ip": get_local_ip(), "port": 5000})

@app.route("/")
def index():
    return send_from_directory("/app/www", "index.html")

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory("/app/www", path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
