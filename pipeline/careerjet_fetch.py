import requests
import csv
import base64
import re
import time
from datetime import datetime

API_KEY = "7440fe7e0815163065618097277c952a"

credentials = base64.b64encode(f"{API_KEY}:".encode()).decode()

headers = {
    "Authorization": f"Basic {credentials}",
    "Referer": "https://emmanuelakinbile.github.io"
}

job_titles = [
    "data analyst",
    "business analyst",
    "business intelligence analyst",
    "reporting analyst"
]

cities = [
    "toronto", "vancouver", "ottawa", "calgary", "edmonton",
    "hamilton", "mississauga", "niagara falls", "st. catharines",
    "winnipeg", "montreal"
]

def strip_html(text):
    return re.sub(r'<[^>]+>', '', text or '').strip()

filename = f"jobs_careerjet_{datetime.today().strftime('%Y-%m-%d')}.csv"

with open(filename, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Title", "Company", "Location", "Salary Min",
                    "Salary Max", "Salary Currency", "Salary Type",
                    "Date Posted", "Search Title", "Search City",
                    "Description", "URL"])
    total = 0

    for title in job_titles:
        for city in cities:
            params = {
                "keywords": title,
                "location": f"{city}, Canada",
                "locale_code": "en_CA",
                "pagesize": 20,
                "page": 1,
                "fragment_size": 5000,
                "user_ip": "76.64.99.182",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }

            response = requests.get(
                "https://search.api.careerjet.net/v4/query",
                headers=headers,
                params=params
            )
            data = response.json()

            for job in data.get("jobs", []):
                writer.writerow([
                    job.get("title", "N/A"),
                    job.get("company", "N/A"),
                    job.get("locations", "N/A"),
                    job.get("salary_min", ""),
                    job.get("salary_max", ""),
                    job.get("salary_currency_code", ""),
                    job.get("salary_type", ""),
                    job.get("date", "N/A"),
                    title,
                    city,
                    strip_html(job.get("description", "N/A")),
                    job.get("url", "N/A")
                ])
                total += 1

            print(f"✓ {title} | {city} — {len(data.get('jobs', []))} jobs")
            time.sleep(1)

print(f"\nDone. {total} total jobs saved to {filename}")