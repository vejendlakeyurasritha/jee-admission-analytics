import streamlit as st
import pandas as pd
import numpy as np
import os
import json
import re
import warnings
warnings.filterwarnings("ignore")

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq

st.set_page_config(page_title="JEE Admission Counselor AI", page_icon="🎓", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("data/josaa_featured.csv")
    last_round = (
        df[df["is_special_round"] == False]
        .groupby(["year", "institute_type"])["round"]
        .max().reset_index().rename(columns={"round": "last_round"})
    )
    df_merged = df.merge(last_round, on=["year", "institute_type"], how="left")
    df_rag = df_merged[
        (df_merged["round"] == df_merged["last_round"]) &
        (df_merged["is_special_round"] == False) &
        (df_merged["is_pwd"] == False)
    ].copy()
    return df_rag

@st.cache_resource
def load_embeddings():
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    return HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

@st.cache_resource
def load_vectorstore(_embeddings):
    return FAISS.load_local(
        "models/faiss_vectorstore",
        _embeddings,
        allow_dangerous_deserialization=True
    )

@st.cache_resource
def load_llm():
    api_key = st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY", ""))
    return ChatGroq(
        model_name="llama-3.1-8b-instant",
        temperature=0.1,
        max_tokens=1024,
        groq_api_key=api_key
    )

df_rag    = load_data()
embeddings = load_embeddings()
vectorstore = load_vectorstore(embeddings)
llm       = load_llm()

def get_eligible_colleges(student_rank, category, gender, quota,
                           program_keywords, institute_types=None,
                           margin_range=(-2000, 5000), top_n=20):
    data = df_rag.copy()
    data = data[
        (data["category_base"] == category) &
        (data["gender_short"] == gender) &
        (data["quota"] == quota)
    ]
    if institute_types:
        data = data[data["institute_type"].isin(institute_types)]
    if program_keywords:
        pattern = "|".join(program_keywords)
        data = data[data["program"].str.contains(pattern, case=False, na=False)]
    data = data.sort_values("year", ascending=False)
    data = data.drop_duplicates(
        subset=["institute", "program", "category_base", "gender_short", "quota"],
        keep="first"
    )
    data["margin"] = data["closing_rank"] - student_rank
    filtered = data[
        (data["margin"] >= margin_range[0]) &
        (data["margin"] <= margin_range[1])
    ].copy()

    def verdict(m):
        if m < -200:   return "Out of Reach"
        elif m < 0:    return "Borderline (Risky)"
        elif m <= 1000: return "Safe"
        else:          return "Comfortable"

    filtered["verdict"] = filtered["margin"].apply(verdict)
    filtered = filtered.sort_values("margin")
    return filtered[[
        "institute", "institute_type", "program",
        "year", "closing_rank", "margin", "verdict"
    ]].head(top_n)


def short_name(name):
    return (name
            .replace("Indian Institute of Technology", "IIT")
            .replace("National Institute of Technology", "NIT")
            .replace("Indian Institute of Information Technology", "IIIT"))


def get_trend(institute_search, program_search,
               category="OPEN", gender="GN", quota="AI"):
    institute_map = {
        "iit bombay"   : "Technology Bombay",
        "iit delhi"    : "Technology Delhi",
        "iit madras"   : "Technology Madras",
        "iit kanpur"   : "Technology Kanpur",
        "iit kharagpur": "Technology Kharagpur",
        "iit roorkee"  : "Technology Roorkee",
        "iit guwahati" : "Technology Guwahati",
        "iit hyderabad": "Technology Hyderabad",
        "iit bhu"      : "(BHU) Varanasi",
        "iit patna"    : "Technology Patna",
        "nit surathkal": "Karnataka, Surathkal",
        "nit trichy"   : "Tiruchirappalli",
        "nit warangal" : "Warangal",
    }
    program_map = {
        "cse": "Computer Science",
        "ece": "Electronics and Communication",
        "me" : "Mechanical",
        "ce" : "Civil",
        "ee" : "Electrical Engineering",
        "it" : "Information Technology",
    }
    institute_actual = institute_map.get(institute_search.lower().strip(), institute_search)
    program_actual   = program_map.get(program_search.lower().strip(), program_search)

    data = df_rag[
        (df_rag["institute"].str.contains(institute_actual, case=False, na=False, regex=False)) &
        (df_rag["program"].str.contains(program_actual, case=False, na=False, regex=False)) &
        (df_rag["category_base"] == category) &
        (df_rag["gender_short"] == gender) &
        (df_rag["quota"] == quota)
    ].copy()

    if data.empty:
        data = df_rag[
            (df_rag["institute"].str.contains(institute_actual, case=False, na=False, regex=False)) &
            (df_rag["program"].str.contains(program_actual, case=False, na=False, regex=False)) &
            (df_rag["category_base"] == category) &
            (df_rag["gender_short"] == gender)
        ].copy()

    if data.empty:
        return None

    trend = (
        data.groupby("year")["closing_rank"]
        .median().reset_index().sort_values("year")
    )
    trend["institute_name"] = data["institute"].iloc[0]
    trend["program_name"]   = data["program"].iloc[0]
    return trend


def get_best_colleges(program_search, institute_type=None,
                       category="OPEN", gender="GN", quota=None, top_n=10):
    program_map = {
        "cse": "Computer Science",
        "ece": "Electronics and Communication",
        "me" : "Mechanical",
        "ce" : "Civil",
        "ee" : "Electrical Engineering",
        "it" : "Information Technology",
    }
    program_actual = program_map.get(program_search.lower().strip(), program_search)
    data = df_rag[
        (df_rag["program"].str.contains(program_actual, case=False, na=False, regex=False)) &
        (df_rag["category_base"] == category) &
        (df_rag["gender_short"] == gender)
    ].copy()
    if institute_type:
        data = data[data["institute_type"] == institute_type]
    if quota:
        data = data[data["quota"] == quota]
    else:
        data = data[data["quota"].isin(["AI", "OS"])]
    if data.empty:
        return None
    recent = sorted(data["year"].unique())[-2:]
    data   = data[data["year"].isin(recent)]
    return (
        data.groupby("institute")["closing_rank"]
        .median().reset_index()
        .sort_values("closing_rank").head(top_n)
    )


def ask_general(question):
    docs    = vectorstore.similarity_search(question, k=15)
    context = "\n\n".join(d.page_content for d in docs[:15])
    prompt  = (
        "Based on this JoSAA admission data, answer concisely "
        "with specific year-wise numbers.\n\n"
        f"DATA:\n{context}\n\nQUESTION: {question}\n\nANSWER:"
    )
    return llm.invoke(prompt).content


def classify(question):
    prompt = f"""Classify this question and return ONLY valid JSON.

Question: {question}

Formats:
Admission: {{"type":"admission","rank":<int>,"category":"OPEN/OBC-NCL/SC/ST/EWS","gender":"GN/FO","quota":"AI/OS/HS","programs":["keyword"],"institute_types":["IIT/NIT/IIIT/GFTI"]}}
Trend:     {{"type":"trend","institute":"<name>","program":"<cse/ece/me/ce/ee/it>","category":"OPEN","gender":"GN","quota":"AI"}}
Best:      {{"type":"best_college","program":"<name>","institute_type":"IIT/NIT/IIIT/GFTI or null","category":"OPEN","gender":"GN"}}
General:   {{"type":"general"}}

Defaults: category=OPEN, gender=GN, quota=AI.
Return ONLY the JSON."""
    resp = llm.invoke(prompt).content.strip()
    m    = re.search(r"\{.*\}", resp, re.DOTALL)
    if m:
        resp = m.group()
    try:
        return json.loads(resp)
    except:
        return {"type": "general"}


# ── UI ──────────────────────────────────────────────────────
st.title("JEE Admission Counselor AI")
st.caption("Powered by ML + RAG + LLaMA 3.1 | 8 years of JoSAA data (2018-2025)")

with st.sidebar:
    st.header("About")
    st.markdown("""
This AI counselor uses:
- **432,524** JoSAA admission records (2018-2025)
- **Random Forest** model (R2 = 0.87)
- **FAISS** vector search over 81,112 documents
- **Groq LLaMA-3.1** for natural language understanding

**Example questions:**
- I have rank 5000 OPEN GN AI quota. Which NITs for CSE?
- How has IIT Delhi CSE closing rank changed 2018 to 2024?
- Which NIT is best for Mechanical Engineering?
""")

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hi! I am your JEE Admission Counselor. Ask me about cutoffs, trends, or which colleges you can get with your rank."
    }]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if question := st.chat_input("Ask about JEE admissions..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            params = classify(question)

            if params.get("type") == "admission":
                results = get_eligible_colleges(
                    student_rank    = params.get("rank", 5000),
                    category        = params.get("category", "OPEN"),
                    gender          = params.get("gender", "GN"),
                    quota           = params.get("quota", "AI"),
                    program_keywords= params.get("programs", []),
                    institute_types = params.get("institute_types"),
                )
                if results.empty:
                    response = "No colleges found matching your criteria. Try a different branch, category, or quota."
                else:
                    response = f"### Results for Rank {params.get('rank'):,} ({params.get('category')})\n\n"
                    for _, row in results.iterrows():
                        m      = int(row["margin"])
                        m_str  = f"+{m:,}" if m >= 0 else f"{m:,}"
                        response += f"**{short_name(row['institute'])}** ({row['institute_type']})  \n"
                        response += f"{row['program'][:80]}  \n"
                        response += f"Closing Rank: {row['closing_rank']:,} ({int(row['year'])}) | Margin: {m_str} | {row['verdict']}\n\n"

            elif params.get("type") == "trend":
                trend = get_trend(
                    institute_search = params.get("institute", ""),
                    program_search   = params.get("program", ""),
                    category         = params.get("category", "OPEN"),
                    gender           = params.get("gender", "GN"),
                    quota            = params.get("quota", "AI"),
                )
                if trend is None:
                    response = "No data found for that institute and program combination."
                else:
                    response  = f"### Trend: {trend['institute_name'].iloc[0]}\n\n"
                    response += f"**Program:** {trend['program_name'].iloc[0][:80]}\n\n"
                    for _, row in trend.iterrows():
                        response += f"- **{int(row['year'])}**: {int(row['closing_rank']):,}\n"
                    if len(trend) >= 2:
                        first = trend.iloc[0]["closing_rank"]
                        last  = trend.iloc[-1]["closing_rank"]
                        pct   = ((last - first) / first) * 100
                        direction = "increased" if pct > 0 else "decreased"
                        response += f"\n**Summary:** Closing rank {direction} by {abs(pct):.1f}% over this period."

            elif params.get("type") == "best_college":
                ranking = get_best_colleges(
                    program_search = params.get("program", ""),
                    institute_type = params.get("institute_type"),
                    category       = params.get("category", "OPEN"),
                    gender         = params.get("gender", "GN"),
                )
                if ranking is None:
                    response = "No data found for that program."
                else:
                    response = f"### Best Colleges for {params.get('program','').upper()}\n\n"
                    for i, (_, row) in enumerate(ranking.iterrows(), 1):
                        response += f"{i}. **{short_name(row['institute'])}** - Median Closing Rank: {int(row['closing_rank']):,}\n"

            else:
                response = ask_general(question)

        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
