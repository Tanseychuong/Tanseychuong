import requests
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter

USERNAME = "Tanseychuong"
TOKEN = "YOUR_GITHUB_TOKEN"  # Optional but recommended

headers = {
    "Authorization": f"token {TOKEN}"
} if TOKEN else {}

# Fetch user events
url = f"https://api.github.com/users/{USERNAME}/events/public"

events = []
page = 1

while True:
    r = requests.get(f"{url}?page={page}", headers=headers)

    if r.status_code != 200:
        print("Error:", r.status_code)
        break

    data = r.json()

    if not data:
        break

    events.extend(data)
    page += 1

print(f"Collected {len(events)} events")

commit_dates = []
repos = []

for event in events:
    if event["type"] == "PushEvent":
        date = pd.to_datetime(event["created_at"])

        for commit in event["payload"]["commits"]:
            commit_dates.append(date)
            repos.append(event["repo"]["name"])

df = pd.DataFrame({
    "date": commit_dates,
    "repo": repos
})

if df.empty:
    print("No commit data found.")
    exit()

df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month_name()
df["weekday"] = df["date"].dt.day_name()
df["hour"] = df["date"].dt.hour

# -----------------------------
# Commits per year
# -----------------------------
year_counts = df["year"].value_counts().sort_index()

plt.figure(figsize=(8,5))
year_counts.plot(kind="bar")
plt.title("Commits Per Year")
plt.ylabel("Commits")
plt.tight_layout()
plt.savefig("commits_per_year.png")

# -----------------------------
# Commits per hour
# -----------------------------
hour_counts = df["hour"].value_counts().sort_index()

plt.figure(figsize=(10,5))
hour_counts.plot(kind="bar")
plt.title("Coding Hours")
plt.xlabel("Hour")
plt.ylabel("Commits")
plt.tight_layout()
plt.savefig("coding_hours.png")

# -----------------------------
# Weekday activity
# -----------------------------
weekday_order = [
    "Monday","Tuesday","Wednesday",
    "Thursday","Friday","Saturday","Sunday"
]

weekday_counts = (
    df["weekday"]
    .value_counts()
    .reindex(weekday_order)
)

plt.figure(figsize=(10,5))
weekday_counts.plot(kind="bar")
plt.title("Activity by Day")
plt.ylabel("Commits")
plt.tight_layout()
plt.savefig("weekday_activity.png")

# -----------------------------
# Top repositories
# -----------------------------
top_repos = df["repo"].value_counts().head(10)

plt.figure(figsize=(10,5))
top_repos.plot(kind="barh")
plt.title("Top Repositories")
plt.tight_layout()
plt.savefig("top_repositories.png")

# -----------------------------
# Summary
# -----------------------------
print("\n===== GitHub Analytics =====")
print(f"Total Commits: {len(df)}")
print(f"Years Active: {df['year'].nunique()}")

best_day = weekday_counts.idxmax()
best_hour = hour_counts.idxmax()

print(f"Most Active Day: {best_day}")
print(f"Most Active Hour: {best_hour}:00")

df.to_csv("github_commit_data.csv", index=False)
