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
    # Deutsch
    "adolf", "hitler", "nazi", "nazis", "heil", "hakenkreuz", "reich",
    "fick", "ficker", "ficken", "fickst", "fickt", "fickende",
    "schlampe", "hure", "hurensohn", "fotze", "fotzen",
    "muschi", "wichser", "wichsen", "wixxer",
    "arschloch", "scheisse",
    "vergewaltigung", "vergewaltige", "vergewaltigt",
    "kinderschander", "kinderschänder", "kindesmissbrauch",
    "bastard", "missgeburt",
    "drecksau", "drecksack",
    "morder", "mörder", "umbringen", "totmachen",
    # English
    "fuck", "fucker", "fucking", "motherfucker",
    "shit", "bitch",
    "asshole", "badass", "dumbass", "jackass",
    "pussy", "pussie", "cunt",
    "dick", "dickhead", "cock", "cocksucker",
    "whore", "slut",
    "nigger", "nigga", "spic", "kike", "chink", "gook",
    "faggot", "fag", "dyke",
    "retard", "retarded",
    "rape", "rapist", "raping",
    "pedophile", "pedophilia", "pedo", "paedophile",
    "porn", "pornhub", "xvideos", "xnxx", "xhamster", "redtube", "onlyfans",
    "drug", "drugs", "cocaine", "kokain", "heroin", "meth", "crack", "weed",
    "lsd", "ecstasy", "mdma", "morphine", "opium", "drogen",
    "murder", "kill", "killer", "killah",
    "terror", "bombe", "isis",
    # Français
    "merde", "putain", "salope",
    "bite", "chatte", "enculé", "enculer", "encule",
    "niquer", "connard", "connasse", "batard",
    "branleur", "viol", "violeur",
    # Español
    "puta", "puto", "mierda", "cabron", "cabrón", "coño", "cono",
    "polla", "gilipollas", "hijoputa", "hijueputa",
    "maricon", "maricón", "joder", "pendejo",
    # Italiano
    "cazzo", "puttana", "stronzo", "merda",
    "vaffanculo", "fanculo", "coglione", "bastardo",
    "violentare", "stupro",
    # Português
    "porra", "caralho", "merda",
    "filhodaputa", "filhadaputa",
    # Nederlands
    "hoer", "hoeren", "kanker", "kankeren",
    "teringlijer", "kankerlijer",
    # Türkçe
    "amk", "amina", "amcik", "sikerim", "sikeyim",
    "orospu", "ibne", "yarrak", "yarak", "sikik",
    # Русский
    "блядь", "blyad", "хуй", "huy", "пизда", "pizda",
    "ебать", "yebat", "сука", "suka",
    # Polski
    "kurwa", "chuj", "pierdol", "pierdole",
    "jebac", "jebać", "zjebac",
    "dziwka", "skurwysyn",
    # Svenska
    "fitta", "knulla", "knullade",
    # Dansk
    "kraftedme", "krafted",
    "fisse",
    # Slovenčina / Čeština
    "kurva", "zmrd", "kokot",
    # Magyar
    "geci", "fasz", "kocsog",
    # Română
    "pula", "pizda", "curva",
    # العربية
    "شرموطة", "sharmuta",
    "خرة", "khara", "قحبة", "qahba", "كس",
    # 日本語
    "ちんこ", "chinco", "まんこ", "manko",
    # 汉语
    "操你妈", "caonima", "草泥马",
    "傻逼", "shabi",
    # 한국어
    "시발", "sibal", "씨발",
    "지랄", "jiral", "병신", "byeongsin",
    # اردو
    "چودنا", "chudai", "لنڈ",
    "بھوسڑا", "bhosra",
]

LEET = {
    "0": "o", "1": "i", "2": "z", "3": "e", "4": "a", "5": "s",
    "6": "g", "7": "t", "8": "b", "9": "g",
    "@": "a", "$": "s", "!": "i", "+": "t",
}

def name_ok(name):
    name_clean = name.lower().replace(" ", "").replace("_", "").replace("-", "").replace(".", "").replace(",", "")
    name_leet = "".join(LEET.get(c, c) for c in name_clean)
    for b in BLOCKED:
        if b in name_clean or b in name_leet:
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
