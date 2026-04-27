import pandas as pd
from datetime import datetime

# --- File names ---
filename = f"jobs_{datetime.today().strftime('%Y-%m-%d')}.csv"
output_filename = f"jobs_{datetime.today().strftime('%Y-%m-%d')}_clean.csv"

# --- Load ---
df = pd.read_csv(filename)
print(f"Before dedup: {len(df)} rows")

# --- Deduplicate ---
df = df.drop_duplicates(subset=["URL"])
print(f"After dedup: {len(df)} rows")

# --- Add source and date parsed ---
df["source"] = "adzuna"
df["date_parsed"] = datetime.today().strftime('%Y-%m-%d')

# --- Prep description for matching ---
df["Description_lower"] = df["Description"].fillna("").str.lower()

# --- Skill definitions ---
skills = {
    # Core tools
    "SQL":            ["sql"],
    "Python":         ["python"],
    "Excel":          ["excel"],
    "Power_BI":       ["power bi"],
    "Tableau":        ["tableau"],
    "R":              [r"\br\b"],
    # Cloud / infrastructure
    "Azure":          ["azure"],
    "AWS":            ["aws"],
    "Snowflake":      ["snowflake"],
    "Databricks":     ["databricks"],
    # Concepts
    "ETL":            ["etl"],
    "DAX":            ["dax"],
    "Statistics":     ["statistics", "statistical"],
    # AI cluster
    "AI":             [r"\bai\b"],
    "Machine_Learning": ["machine learning"],
    "LLM":            [r"\bllm\b", "large language model"],
    "Generative_AI":  ["generative ai", "gen ai"],
    "Copilot":        ["copilot"],
    "NLP":            [r"\bnlp\b", "natural language processing"],
    "Automation":     ["automation"],
}

# --- Keyword matching ---
for skill, patterns in skills.items():
    df[f"skill_{skill}"] = df["Description_lower"].str.contains(
        "|".join(patterns), regex=True, na=False
    ).astype(int)

# --- Skills found summary column ---
skill_cols = [f"skill_{s}" for s in skills.keys()]
df["skills_found"] = df[skill_cols].apply(
    lambda row: ", ".join([
        skill for skill, val in zip(skills.keys(), row) if val == 1
    ]),
    axis=1
)

# --- Drop helper column ---
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
df.to_csv(output_filename, index=False)
print(f"Saved enriched file: {output_filename}")
print(f"\nSkill mention counts:")
for skill in skills.keys():
    col = f"skill_{skill}"
    count = df[col].sum()
    pct = round(count / len(df) * 100, 1)
    print(f"  {skill}: {count} postings ({pct}%)")
