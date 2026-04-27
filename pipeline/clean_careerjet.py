import duckdb
import pandas as pd
import re
from datetime import datetime

# --- File names ---
today = datetime.today().strftime('%Y-%m-%d')
input_file  = f"jobs_careerjet_{today}.csv"
output_file = f"jobs_careerjet_{today}_clean.csv"

# --- Load into DuckDB ---
con = duckdb.connect()
con.execute(f"CREATE TABLE raw AS SELECT * FROM read_csv_auto('{input_file}')")

print(f"Raw rows: {con.execute('SELECT COUNT(*) FROM raw').fetchone()[0]}")

# --- Deduplicate on URL ---
con.execute("""
    CREATE TABLE deduped AS
    SELECT DISTINCT ON (URL) *
    FROM raw
    WHERE URL IS NOT NULL AND URL != 'N/A'
""")

print(f"After dedup: {con.execute('SELECT COUNT(*) FROM deduped').fetchone()[0]}")

# --- Standardize city names ---
con.execute("""
    CREATE TABLE cleaned AS
    SELECT
        Title,
        Company,
        Location,
        "Salary Min",
        "Salary Max",
        "Salary Type",
        "Date Posted",
        LOWER(TRIM("Search Title"))  AS "Search Title",
        LOWER(TRIM("Search City"))   AS "Search City",
        Description,
        URL,
        -- Normalize date format
        STRPTIME(SUBSTR("Date Posted", 1, 16), '%a, %d %b %Y') AS Date_Parsed
    FROM deduped
    WHERE Title IS NOT NULL AND Title != 'N/A'
""")

print(f"After cleaning: {con.execute('SELECT COUNT(*) FROM cleaned').fetchone()[0]}")

# --- Export to pandas for skill matching ---
df = con.execute("SELECT * FROM cleaned").df()
# --- Salary standardization ---
def convert_salary(row, col):
    val = row[col]
    if pd.isna(val):
        return None
    try:
        amount = float(val)
        salary_type = row["Salary Type"]
        if salary_type == "H":
            return round(amount * 2080)
        elif salary_type == "M":
            return round(amount * 12)
        else:
            return round(amount)
    except:
        return None

df["Salary Min"] = df.apply(lambda row: convert_salary(row, "Salary Min"), axis=1)
df["Salary Max"] = df.apply(lambda row: convert_salary(row, "Salary Max"), axis=1)

df["source"] = "careerjet"
# --- Strip any remaining HTML tags from description ---
def strip_html(text):
    return re.sub(r'<[^>]+>', '', str(text)).strip()

df["Description"] = df["Description"].apply(strip_html)

# --- Skill definitions (same as clean_jobs.py) ---
skills = {
    "SQL":            ["sql"],
    "Python":         ["python"],
    "Excel":          ["excel"],
    "Power_BI":       ["power bi"],
    "Tableau":        ["tableau"],
    "R":              [r"\br\b"],
    "Azure":          ["azure"],
    "AWS":            ["aws"],
    "Snowflake":      ["snowflake"],
    "Databricks":     ["databricks"],
    "ETL":            ["etl"],
    "DAX":            ["dax"],
    "Statistics":     ["statistics", "statistical"],
    "AI":             [r"\bai\b"],
    "Machine_Learning":["machine learning"],
    "LLM":            [r"\bllm\b", "large language model"],
    "Generative_AI":  ["generative ai", "gen ai"],
    "Copilot":        ["copilot"],
    "NLP":            [r"\bnlp\b", "natural language processing"],
    "Automation":     ["automation"],
}

# --- Keyword matching on description ---
df["Description_lower"] = df["Description"].fillna("").str.lower()

for skill, patterns in skills.items():
    df[f"skill_{skill}"] = df["Description_lower"].str.contains(
        "|".join(patterns), regex=True, na=False
    ).astype(int)

skill_cols = [f"skill_{s}" for s in skills.keys()]
df["skills_found"] = df[skill_cols].apply(
    lambda row: ", ".join([
        skill for skill, val in zip(skills.keys(), row) if val == 1
    ]), axis=1
)

df = df.drop(columns=["Description_lower"])

# --- Seniority Level (Title first, then Description) ---
def get_seniority(title, desc):
    for text in [str(title).lower(), str(desc).lower()]:
        if any(k in text for k in ["senior", "sr.", " sr "]):
            return "Senior"
        elif any(k in text for k in ["junior", "jr.", " jr ", "entry"]):
            return "Junior"
        elif any(k in text for k in ["lead", "manager", "director", "head of"]):
            return "Leadership"
    return "Not Specified"

df["seniority_level"] = df.apply(lambda row: get_seniority(row["Title"], row["Description"]), axis=1)

# --- Contract Type (Title first, then Description) ---
def get_contract_type(title, desc):
    for text in [str(title).lower(), str(desc).lower()]:
        if any(k in text for k in ["intern", "internship", "co-op", "coop"]):
            return "Internship"
        elif any(k in text for k in ["contract", "temporary", "temp", "fixed-term", "fixed term"]):
            return "Contract"
        elif "part-time" in text or "part time" in text:
            return "Part-Time"
    return "Full-Time"

df["contract_type"] = df.apply(lambda row: get_contract_type(row["Title"], row["Description"]), axis=1)

# --- Save ---
df.to_csv(output_file, index=False)
print(f"\nSaved: {output_file}")
print(f"Total clean rows: {len(df)}")
print("\nSkill mention counts:")
for skill in skills.keys():
    col = f"skill_{skill}"
    count = df[col].sum()
    pct = round(count / len(df) * 100, 1)
    print(f"  {skill}: {count} postings ({pct}%)")