import requests
import csv
from datetime import datetime
import time

APP_ID = "_____"
API_KEY = "_____"

url = "https://api.adzuna.com/v1/api/jobs/ca/search/1"

job_titles = [
    "data analyst",
    "business analyst",
    "business intelligence analyst",
    "reporting analyst"
]

cities = [
    "toronto",
    "vancouver",
    "ottawa",
    "calgary",
    "edmonton",
    "hamilton",
    "mississauga",
    "niagara falls",
    "st. catherines",
    "winnipeg",
    "montreal"
]

filename = f"jobs_{datetime.today().strftime('%Y-%m-%d')}.csv"

with open(filename, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Title", "Company", "Location", "Salary Min", "Salary Max", "Date Posted", "Search Title", "Search City", "Description", "URL"])

    total = 0

    for title in job_titles:
        for city in cities:
            params = {
                "app_id": APP_ID,
                "app_key": API_KEY,
                "results_per_page": 50,
                "what": title,
                "where": city,
                "content-type": "application/json"
            }

            response = requests.get(url, params=params)
            data = response.json()

            for job in data.get("results", []):
                writer.writerow([
                    job.get("title", "N/A"),
                    job.get("company", {}).get("display_name", "N/A"),
                    job.get("location", {}).get("display_name", "N/A"),
                    job.get("salary_min", "N/A"),
                    job.get("salary_max", "N/A"),
                    job.get("created", "N/A"),
                    title,
                    city,
                    job.get("description", "N/A"),
                    job.get("redirect_url", "N/A")
                ])
                total += 1

            print(f"✓ {title} | {city} — {len(data.get('results', []))} jobs")
            time.sleep(1)

print(f"\nDone. {total} total jobs saved to {filename}")
