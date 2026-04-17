import streamlit as st
import pandas as pd
import re
import os

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Job Market Analyzer", layout="wide")

st.title("📊 Job Market Analyzer")

st.markdown("""
### 📌 About
This dashboard analyzes job market trends including:
- Skill demand
- Location trends
- Salary distribution
""")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    file_path = os.path.join("data", "DataAnalyst.csv")
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.lower()
    return df

df = load_data()

st.write("Dataset loaded:", len(df), "rows")

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("🔍 Filters")

locations = st.sidebar.multiselect(
    "Select Location",
    options=sorted(df["location"].dropna().unique())
)

job_titles = st.sidebar.multiselect(
    "Select Job Title",
    options=sorted(df["job title"].dropna().unique())
)

# Default: show all if nothing selected
if not locations:
    locations = df["location"].dropna().unique()

if not job_titles:
    job_titles = df["job title"].dropna().unique()

filtered_df = df[
    (df["location"].isin(locations)) &
    (df["job title"].isin(job_titles))
]

st.write("Filtered rows:", len(filtered_df))

# Stop if no data
if len(filtered_df) == 0:
    st.warning("No data available for selected filters")
    st.stop()

# ---------------- SKILLS EXTRACTION (FIXED) ----------------
skills_keywords = [
    "python", "sql", "excel", "tableau", "power bi",
    "r", "machine learning", "deep learning",
    "aws", "azure", "spark", "hadoop"
]

skills_count = {skill: 0 for skill in skills_keywords}

for desc in filtered_df["job description"].dropna():
    desc = desc.lower()
    for skill in skills_keywords:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, desc):
            skills_count[skill] += 1

skills_df = pd.Series(skills_count).sort_values(ascending=False)

# ---------------- SALARY CLEANING ----------------
def extract_salary(s):
    if isinstance(s, str):
        nums = re.findall(r'\d+', s)
        if len(nums) >= 2:
            return (int(nums[0]) + int(nums[1])) / 2
    return None

filtered_df = filtered_df.copy()
filtered_df["avg_salary"] = filtered_df["salary estimate"].apply(extract_salary)

# ---------------- LAYOUT ----------------
col1, col2 = st.columns(2)

# Skills chart
with col1:
    st.subheader("🔥 Top Skills in Demand")
    st.bar_chart(skills_df)

# Location chart
with col2:
    st.subheader("📍 Top Job Locations")
    st.bar_chart(filtered_df["location"].value_counts().head(10))

# Salary chart
st.subheader("💰 Salary Distribution")
st.bar_chart(filtered_df["avg_salary"].dropna())

# ---------------- EXTRA SECTION ----------------
st.subheader("📄 Top Job Titles")
st.bar_chart(filtered_df["job title"].value_counts().head(10))

# ---------------- RAW DATA ----------------
if st.checkbox("Show Raw Data"):
    st.dataframe(filtered_df)

# ---------------- INSIGHTS ----------------
st.subheader("🧠 Key Insights")

top_skill = skills_df.idxmax()
top_location = filtered_df["location"].value_counts().idxmax()
avg_salary = int(filtered_df["avg_salary"].mean())

st.markdown(f"""
- 🔥 **Most in-demand skill:** {top_skill.upper()}
- 📍 **Top hiring location:** {top_location}
- 💰 **Average salary:** ${avg_salary}K
""")