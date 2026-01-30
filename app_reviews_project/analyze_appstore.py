import pandas as pd
from textblob import TextBlob

# Load your previously saved Apple CSV
df = pd.read_csv("appstore_reviews.csv")

print("===== BASIC INFO =====")
print("Shape:", df.shape)
print("Columns:", list(df.columns))
print()

print("===== SAMPLE ROWS =====")
print(df.head(), "\n")

# -----------------------------
# Missing Values
# -----------------------------
print("===== MISSING VALUES =====")
print(df.isnull().sum(), "\n")

# -----------------------------
# Text Length Analysis
# -----------------------------
df["text_length"] = df["content"].astype(str).apply(len)

print("===== TEXT LENGTH STATS =====")
print(df["text_length"].describe(), "\n")

# -----------------------------
# Sentiment Analysis (Polarity)
# -----------------------------
print("Calculating sentiment…")

def get_sentiment(text):
    score = TextBlob(str(text)).sentiment.polarity
    if score > 0.05:
        return "positive"
    elif score < -0.05:
        return "negative"
    else:
        return "neutral"

df["sentiment"] = df["content"].apply(get_sentiment)

print("\n===== SENTIMENT DISTRIBUTION =====")
print(df["sentiment"].value_counts(), "\n")

# -----------------------------
# Duplicate Detection
# -----------------------------
print("===== DUPLICATES =====")
print("Duplicate reviews:", df.duplicated(subset=["content"]).sum(), "\n")

# -----------------------------
# Date Range
# -----------------------------
print("===== DATE RANGE =====")
if "updated" in df.columns:
    print(df["updated"].min(), "to", df["updated"].max(), "\n")
else:
    print("No date field available.\n")

print("===== SUMMARY COMPLETE =====")
