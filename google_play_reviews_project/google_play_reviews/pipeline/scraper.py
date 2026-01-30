from google_play_scraper import reviews
import pandas as pd
from tqdm import tqdm
import hashlib
from datetime import datetime


def make_review_uid(user, date, text):
    raw = f"{user}_{date}_{text}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def collect_reviews(app_id, lang, country, target_per_mode, sort_mode, sort_name):
    all_rows = []
    continuation_token = None
    pbar = None

    try:
        pbar = tqdm(total=target_per_mode, desc=f"Collecting ({sort_name})")

        while len(all_rows) < target_per_mode:
            result, continuation_token = reviews(
                app_id,
                lang=lang,
                country=country,
                sort=sort_mode,
                count=200,
                continuation_token=continuation_token
            )

            if not result:
                break

            for r in result:
                row = {
                    "review_uid": make_review_uid(
                        r.get("userName"),
                        r.get("at"),
                        r.get("content")
                    ),
                    "user_name": r.get("userName"),
                    "rating": r.get("score"),
                    "review_text": r.get("content"),
                    "review_date": r.get("at"),
                    "thumbs_up": r.get("thumbsUpCount"),
                    "app_version": r.get("reviewCreatedVersion"),
                    "sort_mode": sort_name,
                    "scrape_time": datetime.utcnow(),
                }
                all_rows.append(row)

            # only count what we *actually* added toward the target
            added = min(len(result), target_per_mode - len(all_rows) + len(result))
            pbar.update(min(len(result), target_per_mode - (len(all_rows) - len(result))))

            if continuation_token is None:
                break

    finally:
        if pbar is not None:
            pbar.close()

    df = pd.DataFrame(all_rows)
    return df


def scrape_reviews(app_id, lang, country, target_per_mode, sort_modes):
    """
    sort_modes example:
      {"newest": Sort.NEWEST, "most_relevant": Sort.MOST_RELEVANT}
    """
    dfs = []

    for sort_name, sort_mode in sort_modes.items():
        df_mode = collect_reviews(
            app_id=app_id,
            lang=lang,
            country=country,
            target_per_mode=target_per_mode,
            sort_mode=sort_mode,
            sort_name=sort_name
        )
        dfs.append(df_mode)

    raw_df = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

    # Deduplicate
    if not raw_df.empty and "review_uid" in raw_df.columns:
        raw_df = raw_df.drop_duplicates(subset="review_uid")

    # Enforce expected column order (and fill missing cols)
    expected_cols = [
        "review_uid", "user_name", "rating", "review_text", "review_date",
        "thumbs_up", "app_version", "sort_mode", "scrape_time"
    ]
    for c in expected_cols:
        if c not in raw_df.columns:
            raw_df[c] = None
    raw_df = raw_df[expected_cols]

    return raw_df
