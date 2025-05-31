import subprocess
import os
import psycopg2
import pandas as pd
import pickle

def run_spider(spider_subdir, spider_name):
    print(f"Running spider: {spider_name}")
    full_path = os.path.join("scraper", spider_subdir)
    output_file = os.path.join(full_path, f"{spider_name}.json")

    if os.path.exists(output_file):
        os.remove(output_file)

    subprocess.run(["python", "-m", "scrapy", "crawl", spider_name, "-o", f"{spider_name}.json"], cwd=full_path)

def run_import_script():
    print("Running import_data.py")
    subprocess.run(["python", "import_data.py"])

def run_ml_training():
    print("Training ML model (category_classifier.py)")
    subprocess.run(["python", "ml/category_classifier.py"])

def classify_uncategorized_events():
    print("Classifying uncategorized events using trained ML model...")
    
    # Load trained model and vectorizer
    with open("ml_model.pkl", "rb") as f:
        model, vectorizer = pickle.load(f)

    # Connect to database and fetch uncategorized events
    conn = psycopg2.connect(
    dbname="history_db",
    user="postgres",
    password="wwe123",
    host="db"
)

    cursor = conn.cursor()

    df = pd.read_sql_query(
        "SELECT id, event FROM polish_history WHERE category IS NULL AND event <> ''",
        conn
    )

    if df.empty:
        print("No uncategorized events found.")
        conn.close()
        return

    # Vectorize and predict
    X_vec = vectorizer.transform(df["event"])
    predictions = model.predict(X_vec)

    # Update DB with predictions
    for idx, pred in zip(df["id"], predictions):
        cursor.execute(
            "UPDATE polish_history SET category = %s WHERE id = %s",
            (pred, idx)
        )

    conn.commit()
    conn.close()
    print(f"Updated {len(df)} uncategorized events with predicted categories.")

if __name__ == "__main__":
    run_spider("warsaw_history/warsaw_history", "warsaw_history")
    run_spider("poznan_history/poznan_history", "poznan_history")
    run_import_script()
    run_ml_training()
    classify_uncategorized_events()
    print("All tasks completed.")
