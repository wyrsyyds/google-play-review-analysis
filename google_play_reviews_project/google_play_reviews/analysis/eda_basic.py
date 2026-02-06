from __future__ import annotations

import argparse
import json
from pathlib import Path
from datetime import datetime

import pandas as pd


def load_df(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")
    df = pd.read_csv(csv_path)

    # Ensure key types
    if "review_date" in df.columns:
        df["review_date"] = pd.to_datetime(df["review_date"], errors="coerce")
    if "scrape_time" in df.columns:
        df["scrape_time"] = pd.to_datetime(df["scrape_time"], errors="coerce")
    if "rating" in df.columns:
        df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    if "thumbs_up" in df.columns:
        df["thumbs_up"] = pd.to_numeric(df["thumbs_up"], errors="coerce")

    if "review_text" in df.columns:
        df["review_text"] = df["review_text"].fillna("").astype(str)

    return df


def add_text_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "review_text" not in df.columns:
        df["review_text"] = ""
    df["char_len"] = df["review_text"].astype(str).str.len()
    df["word_len"] = df["review_text"].astype(str).str.split().str.len()
    df["is_emoji_or_symbol_only"] = df["review_text"].str.match(r"^[\W_]+$", na=False) & (df["char_len"] > 0)
    df["is_very_short"] = df["word_len"] <= 3
    return df


def basic_profile(df: pd.DataFrame) -> dict:
    out = {}

    out["rows"] = int(len(df))
    out["cols"] = int(df.shape[1])

    # Time range
    if "review_date" in df.columns:
        out["review_date_min"] = None if df["review_date"].isna().all() else str(df["review_date"].min())
        out["review_date_max"] = None if df["review_date"].isna().all() else str(df["review_date"].max())

    # Ratings distribution + stats
    if "rating" in df.columns:
        counts = df["rating"].value_counts(dropna=False).sort_index()
        out["rating_counts"] = {str(k): int(v) for k, v in counts.items()}

        non_na = df["rating"].dropna()
        if len(non_na) > 0:
            out["rating_mean"] = float(non_na.mean())
            out["rating_median"] = float(non_na.median())
            out["rating_std"] = float(non_na.std(ddof=1)) if len(non_na) > 1 else 0.0
        else:
            out["rating_mean"] = None
            out["rating_median"] = None
            out["rating_std"] = None

    # Text length stats
    if "word_len" in df.columns:
        wl = df["word_len"]
        out["word_len_mean"] = float(wl.mean())
        out["word_len_median"] = float(wl.median())
        out["word_len_p25"] = float(wl.quantile(0.25))
        out["word_len_p75"] = float(wl.quantile(0.75))
        out["word_len_p95"] = float(wl.quantile(0.95))
        out["word_len_max"] = int(wl.max())

        out["pct_very_short_le_3_words"] = float((df["is_very_short"]).mean())
        out["pct_emoji_or_symbol_only"] = float((df["is_emoji_or_symbol_only"]).mean())

    # Missingness (top 10)
    miss = df.isna().mean().sort_values(ascending=False).head(10)
    out["missingness_top10"] = {c: float(p) for c, p in miss.items()}

    # Sort mode breakdown
    if "sort_mode" in df.columns:
        sm = df["sort_mode"].value_counts(dropna=False)
        out["sort_mode_counts"] = {str(k): int(v) for k, v in sm.items()}

    # App version breakdown (top 10)
    if "app_version" in df.columns:
        av = df["app_version"].fillna("MISSING").value_counts().head(10)
        out["app_version_top10"] = {str(k): int(v) for k, v in av.items()}
        out["pct_app_version_missing"] = float((df["app_version"].isna() | (df["app_version"].astype(str).str.strip() == "")).mean())

    return out


def time_aggregation(df: pd.DataFrame) -> pd.DataFrame | None:
    if "review_date" not in df.columns:
        return None
    d = df.dropna(subset=["review_date"]).copy()
    if d.empty:
        return None

    d["date"] = d["review_date"].dt.date
    agg = d.groupby("date").agg(
        reviews=("review_uid", "count") if "review_uid" in d.columns else ("review_date", "count"),
        avg_rating=("rating", "mean") if "rating" in d.columns else ("review_date", "count"),
    ).reset_index()

    # If rating column missing, avg_rating will be nonsense—guard:
    if "rating" not in d.columns:
        agg["avg_rating"] = None

    return agg


def write_markdown(summary: dict, out_path: Path) -> None:
    lines = []
    lines.append("# Google Play Reviews – EDA Summary")
    lines.append("")
    lines.append(f"- Generated: {datetime.now().isoformat()}")
    lines.append(f"- Rows: {summary.get('rows')}")
    lines.append(f"- Columns: {summary.get('cols')}")
    lines.append(f"- Review date range: {summary.get('review_date_min')} → {summary.get('review_date_max')}")
    lines.append("")

    if "rating_counts" in summary:
        lines.append("## Rating distribution")
        lines.append(f"- Mean: {summary.get('rating_mean')}")
        lines.append(f"- Median: {summary.get('rating_median')}")
        lines.append(f"- Std: {summary.get('rating_std')}")
        lines.append("")
        lines.append("Counts:")
        for k, v in summary["rating_counts"].items():
            lines.append(f"- {k}: {v}")
        lines.append("")

    lines.append("## Text length")
    if "word_len_mean" in summary:
        lines.append(f"- Word count mean / median: {summary['word_len_mean']:.2f} / {summary['word_len_median']:.2f}")
        lines.append(f"- P25 / P75 / P95: {summary['word_len_p25']:.2f} / {summary['word_len_p75']:.2f} / {summary['word_len_p95']:.2f}")
        lines.append(f"- Max words: {summary['word_len_max']}")
        lines.append(f"- % very short (≤3 words): {summary['pct_very_short_le_3_words']:.3f}")
        lines.append(f"- % emoji/symbol-only: {summary['pct_emoji_or_symbol_only']:.3f}")
        lines.append("")

    lines.append("## Data quality (missingness top 10)")
    for c, p in summary.get("missingness_top10", {}).items():
        lines.append(f"- {c}: {p:.3f}")
    lines.append("")

    if "sort_mode_counts" in summary:
        lines.append("## Sort mode breakdown")
        for k, v in summary["sort_mode_counts"].items():
            lines.append(f"- {k}: {v}")
        lines.append("")

    if "pct_app_version_missing" in summary:
        lines.append("## App version")
        lines.append(f"- % missing app_version: {summary['pct_app_version_missing']:.3f}")
        lines.append("Top 10 versions:")
        for k, v in summary.get("app_version_top10", {}).items():
            lines.append(f"- {k}: {v}")
        lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Basic EDA for Google Play processed reviews CSV")
    parser.add_argument("--csv", required=True, help="Path to processed CSV")
    parser.add_argument("--outdir", default=None, help="Output directory (default: alongside CSV)")
    args = parser.parse_args()

    csv_path = Path(args.csv).expanduser().resolve()
    # Determine output directory
    if args.outdir:
        outdir = Path(args.outdir).expanduser().resolve()
    else:
    # Default: google_play_reviews/reports/eda
        project_root = Path(__file__).resolve().parents[1]
        outdir = project_root / "reports" / "eda"

    outdir.mkdir(parents=True, exist_ok=True)

    df = load_df(csv_path)
    df = add_text_features(df)

    summary = basic_profile(df)

    # Save JSON + MD
    json_out = outdir / f"eda_summary_{csv_path.stem}.json"
    md_out = outdir / f"eda_summary_{csv_path.stem}.md"
    json_out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_markdown(summary, md_out)

    # Save time aggregation (CSV)
    agg = time_aggregation(df)
    if agg is not None:
        agg_out = outdir / f"eda_time_{csv_path.stem}.csv"
        agg.to_csv(agg_out, index=False)

    print(f"Saved:\n- {json_out}\n- {md_out}" + (f"\n- {agg_out}" if agg is not None else ""))


if __name__ == "__main__":
    main()
