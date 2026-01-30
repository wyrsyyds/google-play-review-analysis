import pandas as pd
import requests

# Choose an app (example: Spotify)
app_id = "547702041"  # Replace with any iOS app ID
country = "ca"        # Canada
limit = 200           # Apple RSS returns 200 max per request

print(f"Fetching Apple App Store reviews for app {app_id}…")

url = f"https://itunes.apple.com/{country}/rss/customerreviews/id={app_id}/sortBy=mostRecent/json"

response = requests.get(url, timeout=10)

if response.status_code != 200:
    print("Error:", response.status_code)
    exit()

data = response.json()

# Extract reviews
entries = data.get("feed", {}).get("entry", [])[1:]  # first entry is app metadata

reviews = []
for entry in entries:
    reviews.append({
        "id": entry["id"]["label"],
        "author": entry["author"]["name"]["label"],
        "rating": entry["im:rating"]["label"],
        "title": entry["title"]["label"],
        "content": entry["content"]["label"],
        "version": entry.get("im:version", {}).get("label"),
        "voteCount": entry.get("im:voteCount", {}).get("label"),
        "updated": entry["updated"]["label"]
    })

df = pd.DataFrame(reviews)

output_file = "appstore_reviews.csv"
df.to_csv(output_file, index=False, encoding="utf-8")

print(f"Saved {len(df)} reviews to {output_file} 🎉")
