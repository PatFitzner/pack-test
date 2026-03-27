import os
from src.db import get_connection

MODEL_ORDER = [
    "dim_users.sql",
    "dim_mentors.sql",
    "fct_sessions.sql",
    "fct_booking_events.sql",
]

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")


def transform():
    con = get_connection()

    for model_file in MODEL_ORDER:
        path = os.path.join(MODELS_DIR, model_file)
        with open(path) as f:
            sql = f.read()
        con.execute(sql)
        table_name = model_file.replace(".sql", "")
        count = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"{model_file}: created {table_name} ({count} rows)")

    con.close()
    print("Transformation complete.")


if __name__ == "__main__":
    transform()
