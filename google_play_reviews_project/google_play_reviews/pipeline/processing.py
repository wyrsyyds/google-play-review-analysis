import pandas as pd

def basic_clean(df: pd.DataFrame, logger=None) -> pd.DataFrame:
    df = df.copy()

    # Standardize column names & Ensure expected columns exist
    expected = [
        "review_uid", "user_name", "rating", "review_text",
        "review_date", "thumbs_up", "app_version", "sort_mode", "scrape_time"
    ]
    missing = [c for c in expected if c not in df.columns]
    if logger:
        logger.info(f"[SCHEMA_CHECK] missing_cols={missing}")

    # Coerce types safely
    if "rating" in df.columns:
        df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

    if "thumbs_up" in df.columns:
        df["thumbs_up"] = pd.to_numeric(df["thumbs_up"], errors="coerce")

    # Parse dates
    for col in ["review_date", "scrape_time"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Normalize text
    if "review_text" in df.columns:
        df["review_text"] = df["review_text"].fillna("").astype(str).str.strip()

    # Basic duplicate check
    if "review_uid" in df.columns:
        dup_count = df["review_uid"].duplicated().sum()
        if logger:
            logger.info(f"[DUP_CHECK] review_uid_duplicates={dup_count}")

    # Basic missingness summary
    if logger:
        na_summary = df.isna().mean().sort_values(ascending=False).head(10)
        logger.info(f"[MISSINGNESS_TOP10] {na_summary.to_dict()}")

    return df
