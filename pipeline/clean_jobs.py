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

# --- Save ---
df.to_csv(output_filename, index=False)
print(f"Saved enriched file: {output_filename}")
print(f"\nSkill mention counts:")
for skill in skills.keys():
    col = f"skill_{skill}"
    count = df[col].sum()
    pct = round(count / len(df) * 100, 1)
    print(f"  {skill}: {count} postings ({pct}%)")
