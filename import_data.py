import json
import psycopg2
import unicodedata
import re
import pickle
import os

# === Load ML Model ===
MODEL_PATH = "ml/ml_model.pkl"
model, vectorizer = None, None
if os.path.exists(MODEL_PATH):
    with open(MODEL_PATH, "rb") as f:
        model, vectorizer = pickle.load(f)
    print("ML model and vectorizer loaded.")
else:
    print("Warning: ML model not found, using keyword-based only.")

# === Connect to DB ===
conn = psycopg2.connect(
    dbname="history_db",  # <- match docker-compose
    user="postgres",
    password="wwe123",
    host="db"  # <- Docker service name
)
conn.set_client_encoding('UTF8')
cur = conn.cursor()

# === Create table if not exists ===
cur.execute("""
    CREATE TABLE IF NOT EXISTS polish_history (
        id SERIAL PRIMARY KEY,
        city TEXT,
        year TEXT,
        event TEXT,
        category TEXT
    );
""")
conn.commit()

# === Truncate table before import ===
cur.execute("TRUNCATE TABLE polish_history RESTART IDENTITY;")
print("Table 'polish_history' truncated.")

def clean_year(year_data):
    if isinstance(year_data, list):
        year_data = year_data[0]

    year_str = str(year_data).strip().replace('û', '-')
    for dash in ['–', '—', '−', '‑']:
        year_str = year_str.replace(dash, '-')

    if len(year_str) == 8 and year_str.isdigit():
        year_str = f"{year_str[:4]}-{year_str[4:]}"
    return year_str

def categorize_event_keyword(event_text):
    event_lower = event_text.lower()
    categories = {
        "war": ["battle", "war", "invade", "siege", "uprising", "army", "military", "revolt", "occupation", "artillery"],
        "science": ["university", "academy", "research", "institute", "science", "scientific", "astronomy", "education", "college"],
        "culture": ["theatre", "museum", "concert", "festival", "art", "exhibition", "cultural", "library"],
        "sports": ["championship", "team", "football", "basketball", "sport", "athlete", "olympic"],
        "religion": ["church", "cathedral", "religion", "diocese", "monastery", "bishop", "christian"],
        "politics": ["sejm", "mayor", "law", "governor", "rights", "magdeburg", "constitution", "election", "parliament", "diet", "confederation", "elections"]
    }
    for category, keywords in categories.items():
        if any(re.search(rf'\b{re.escape(k)}\b', event_lower) for k in keywords):
            return category
    return "other"

def categorize_with_confidence(description, threshold=0.7):
    if model is None or vectorizer is None:
        return categorize_event_keyword(description)

    vec = vectorizer.transform([description])
    probas = model.predict_proba(vec)[0]
    best_idx = probas.argmax()
    confidence = probas[best_idx]
    predicted = model.classes_[best_idx]

    return predicted if confidence >= threshold else categorize_event_keyword(description)

def normalize_text(text):
    if isinstance(text, bytes):
        text = text.decode('utf-8', errors='replace')
    return unicodedata.normalize('NFC', text)

def import_events(filepath, city_name, cursor):
    print(f"Importing from {filepath} for city {city_name}")
    with open(filepath, 'r', encoding='utf-8') as f:
        events = json.load(f)
        for item in events:
            description = normalize_text(item['description'])
            year_str = clean_year(item['year'])
            if not year_str:
                continue

            category = categorize_with_confidence(description)

            try:
                cursor.execute(
                    """
                    INSERT INTO polish_history (city, year, event, category)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (city_name, year_str, description, category)
                )
            except Exception as e:
                print(f"Error inserting event: {e}")

# === Define JSON paths ===
warsaw_json_path = os.path.join("scraper", "warsaw_history", "warsaw_history", "warsaw_history.json")
poznan_json_path = os.path.join("scraper", "poznan_history", "poznan_history", "poznan_history.json")

# === Run imports ===
import_events(warsaw_json_path, 'Warsaw', cur)
import_events(poznan_json_path, 'Poznan', cur)

conn.commit()
cur.close()
conn.close()

print("Data imported successfully!")
