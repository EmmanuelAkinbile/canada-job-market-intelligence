import os
import shutil
from datetime import datetime

folder = r"C:\Users\emman\OneDrive\Documents\canada-job-market-intelligence"
today = datetime.today().strftime('%Y-%m-%d')
source = os.path.join(folder, f"jobs_{today}_clean.csv")
destination = os.path.join(folder, "jobs_latest_clean.csv")

if os.path.exists(source):
    shutil.copy2(source, destination)
    print(f"Updated jobs_latest_clean.csv from {source}")
else:
    print(f"ERROR: {source} not found")
