import pandas as pd
from textblob import TextBlob

# ====================================
# LOAD DATA
# ====================================
df = pd.read_csv("app_reviews_project/googleplay_reviews.csv")

print("\n===== BASIC INFO =====")
print("Shape:", df.shape)
print("Columns:", list(df.columns))


# ====================================
# SAMPLE ROWS
# ====================================
print("\n===== SAMPLE ROWS =====")
print(df.head())


# ====================================
# MISSING VALUES
# ====================================
print("\n===== MISSING VALUES =====")
print(df.isna().sum())


# ====================================
# TEXT LENGTH STATS
# ====================================
df["text_length"] = df["content"].astype(str).apply(len)

print("\n===== TEXT LENGTH STATS =====")
print(df["text_length"].describe())


# ====================================
# SENTIMENT ANALYSIS
# ====================================
def simple_sentiment(text):
    if not isinstance(text, str) or len(text.strip()) == 0:
        return "neutral"

    score = TextBlob(text).sentiment.polarity
    if score > 0.1:
        return "positive"
    elif score < -0.1:
        return "negative"
    else:
        return "neutral"

print("\nCalculating sentiment…")
df["sentiment"] = df["content"].apply(simple_sentiment)

print("\n===== SENTIMENT DISTRIBUTION =====")
print(df["sentiment"].value_counts())


# ====================================
# DUPLICATES
# ====================================
print("\n===== DUPLICATES =====")
dup_count = df.duplicated(subset=["content"]).sum()
print("Duplicate reviews:", dup_count)


# ====================================
# DATE RANGE
# ====================================
if "at" in df.columns:
    df["at"] = pd.to_datetime(df["at"], errors="coerce")
    print("\n===== DATE RANGE =====")
    print(df["at"].min(), "to", df["at"].max())
else:
    print("\n===== DATE RANGE =====")
    print("No date column available.")


print("\n===== SUMMARY COMPLETE =====\n")
