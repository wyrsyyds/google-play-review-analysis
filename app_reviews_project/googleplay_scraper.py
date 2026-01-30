import pandas as pd
from google_play_scraper import reviews

# Choose an app (example: Spotify)
app_id = "com.spotify.music"

print(f"Fetching Google Play reviews for {app_id}…")

result, token = reviews(
    app_id,
    lang="en",
    country="ca",
    count=500  # fetch ~500 reviews
)

# Convert to dataframe
df = pd.DataFrame(result)

output_file = "googleplay_reviews.csv"
df.to_csv(output_file, index=False, encoding="utf-8")

print(f"Saved {len(df)} reviews to {output_file} 🎉")
