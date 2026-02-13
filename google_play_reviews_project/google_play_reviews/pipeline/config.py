from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]  # google_play_reviews/.. (repo root)
PROJECT_ROOT = REPO_ROOT / "google_play_reviews"

PIPELINE_CONFIG = {

    "input_csv": str(PROJECT_ROOT / "data" / "raw" / "reviews_latest.csv"),

    # Output locations
    "raw_out_dir": str(PROJECT_ROOT / "data" / "raw"),
    "processed_out_dir": str(PROJECT_ROOT / "data" / "processed"),
    "logs_dir": str(PROJECT_ROOT / "data" /"logs"),
    "app_id": "com.openai.chatgpt",
    "lang": "en",
    "country": "us",
    "target_per_mode": 2500,
    "use_scraper": True,

    # Database config
    "load_to_db": True,
    "db_path": str(PROJECT_ROOT / "data" / "db" / "reviews.db"),
}

