import psycopg2
import pandas as pd
import pickle

# Database connection settings
DB_PARAMS = {
    "dbname": "history_db",
    "user": "postgres",
    "password": "wwe123",
    "host": "localhost"
}

def load_model(model_path="ml_model.pkl"):
    """Load the trained ML model and vectorizer from disk."""
    with open(model_path, "rb") as f:
        model, vectorizer = pickle.load(f)
    return model, vectorizer

def fetch_uncategorized_events(conn):
    """
    Fetch events from the DB that have empty or NULL category.
    Returns a DataFrame with event id and description.
    """
    query = """
        SELECT id, event
        FROM polish_history
        WHERE category IS NULL OR category = ''
        AND event <> ''
    """
    return pd.read_sql_query(query, conn)

def update_event_category(conn, event_id, category):
    """Update the category for a single event by id."""
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE polish_history SET category = %s WHERE id = %s",
            (category, event_id)
        )
    conn.commit()

def main():
    # Connect to DB
    conn = psycopg2.connect(**DB_PARAMS)

    # Load model and vectorizer
    model, vectorizer = load_model()

    # Fetch uncategorized events
    df = fetch_uncategorized_events(conn)
    if df.empty:
        print("No uncategorized events found.")
        conn.close()
        return

    print(f"Found {len(df)} uncategorized events. Predicting categories...")

    # Vectorize event descriptions
    X_vec = vectorizer.transform(df['event'])

    # Predict categories
    predictions = model.predict(X_vec)

    # Update categories in DB
    for event_id, category in zip(df['id'], predictions):
        update_event_category(conn, event_id, category)

    print(f"Updated categories for {len(df)} events.")
    conn.close()

if __name__ == "__main__":
    main()
