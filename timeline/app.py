from flask import Flask, jsonify, request, send_from_directory
import psycopg2

app = Flask(__name__)

DB_CONFIG = {
    "dbname": "history_db",
    "user": "postgres",
    "password": "wwe123",
    "host": "db"
}

@app.route("/")
def index():
    return send_from_directory('.', 'timeline.html')

@app.route("/api/events")
def get_events():
    city = request.args.get("city", "").capitalize()
    if city not in ("Warsaw", "Poznan"):
        return jsonify([])

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT year, event, category
            FROM polish_history
            WHERE city = %s
            ORDER BY year ASC
        """, (city,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify([
        {"year": year, "description": event, "category": category}
        for year, event, category in rows
    ])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

