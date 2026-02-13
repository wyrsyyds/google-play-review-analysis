import sqlite3
from pathlib import Path
import pandas as pd

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schema" / "schema_sqlite.sql"


def init_db(db_path: str):
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))


def upsert_reviews(df: pd.DataFrame, db_path: str, app_id: str, run_id: str):
    init_db(db_path)

    df = df.copy()
    df["app_id"] = app_id
    df["run_id"] = run_id
       
    if "rating" in df.columns:
        df["rating"] = pd.to_numeric(df["rating"], errors="coerce").astype("Int64")

    if "thumbs_up" in df.columns:
        df["thumbs_up"] = pd.to_numeric(df["thumbs_up"], errors="coerce").astype("Int64")

    df["rating"] = df["rating"].astype(object).where(df["rating"].notna(), None)
    df["thumbs_up"] = df["thumbs_up"].astype(object).where(df["thumbs_up"].notna(), None)



    for col in ["review_date", "scrape_time"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce") \
                         .dt.strftime("%Y-%m-%d %H:%M:%S")

    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO apps(app_id) VALUES (?)",
            (app_id,),
        )

        rows = df[[
            "review_uid", "app_id", "user_name", "rating",
            "review_text", "review_date", "thumbs_up",
            "app_version", "sort_mode", "scrape_time", "run_id"
        ]].to_records(index=False)

        conn.executemany(
            """
            INSERT INTO reviews (
                review_uid, app_id, user_name, rating,
                review_text, review_date, thumbs_up,
                app_version, sort_mode, scrape_time, run_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(review_uid) DO UPDATE SET
                rating=excluded.rating,
                review_text=excluded.review_text,
                review_date=excluded.review_date,
                thumbs_up=excluded.thumbs_up,
                app_version=excluded.app_version,
                sort_mode=excluded.sort_mode,
                scrape_time=excluded.scrape_time,
                run_id=excluded.run_id
            """,
            list(rows),
        )
