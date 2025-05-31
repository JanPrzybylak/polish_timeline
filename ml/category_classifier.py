"""
Trains a text classification model using categorized events stored in PostgreSQL.
The trained model and vectorizer are saved to 'ml_model.pkl'.
"""

import psycopg2
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import pickle


def load_data():
    conn = psycopg2.connect(
        dbname="history_db",
        user="postgres",
        password="wwe123",
        host="db"
    )
    query = """
        SELECT event, category
        FROM polish_history
        WHERE category IS NOT NULL AND event <> ''
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def main():
    df = load_data()
    X = df['event']
    y = df['category'].str.strip().str.lower()

    vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2))
    X_vec = vectorizer.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_vec, y, test_size=0.2, random_state=42, stratify=y
    )

    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print("Classification report:\n")
    print(classification_report(y_test, y_pred))

    conf_mat = confusion_matrix(y_test, y_pred, labels=model.classes_)
    plt.figure(figsize=(8, 6))
    sns.heatmap(conf_mat, annot=True, fmt='d', cmap='Blues',
                xticklabels=model.classes_, yticklabels=model.classes_)
    plt.title("Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.tight_layout()
    plt.show()

    with open("ml_model.pkl", "wb") as f:
        pickle.dump((model, vectorizer), f)
    print("Model and vectorizer saved to ml_model.pkl")


if __name__ == "__main__":
    main()
