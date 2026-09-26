import streamlit as st
import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings("ignore")

try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

# Try loading Plotly, with fallback to Native Streamlit / Matplotlib if not installed
try:
    import plotly.express as px
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

st.set_page_config(
    page_title="JEE Admission Counselor & Analytics Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for rich aesthetics
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    # 1. Primary path for lightweight deployment dataset
    app_data_path = os.path.join(os.path.dirname(__file__), "josaa_app_data.csv")
    if os.path.exists(app_data_path):
        df_final = pd.read_csv(app_data_path)
        return df_final, df_final
        
    # 2. Secondary fallback for local dev environment
    path = os.path.join("data", "processed", "josaa_featured.csv")
    if not os.path.exists(path):
        path = os.path.join("..", "data", "processed", "josaa_featured.csv")
    
    if os.path.exists(path):
        df = pd.read_csv(path)
        last_round = (
            df[df["is_special_round"] == False]
            .groupby(["year", "institute_type"])["round"]
            .max().reset_index().rename(columns={"round": "last_round"})
        )
        df_merged = df.merge(last_round, on=["year", "institute_type"], how="left")
        df_final = df_merged[
            (df_merged["round"] == df_merged["last_round"]) &
            (df_merged["is_special_round"] == False) &
            (df_merged["is_pwd"] == False)
        ].copy()
        return df, df_final
        
    raise FileNotFoundError("JoSAA Dataset file not found.")

try:
    df_full, df_final = load_data()
except Exception as e:
    st.error(f"Error loading dataset: {e}")
    st.stop()

# Helper function to shorten institute names
def short_name(name):
    if not isinstance(name, str):
        return name
    return (name
            .replace("Indian Institute of Technology", "IIT")
            .replace("National Institute of Technology", "NIT")
            .replace("Indian Institute of Information Technology", "IIIT"))

# --- Sidebar ---
st.sidebar.title("🎓 Counseling Settings")
st.sidebar.markdown("---")

user_rank = st.sidebar.number_input("Enter Your JEE Rank:", min_value=1, max_value=1500000, value=5000, step=500)
category = st.sidebar.selectbox("Category:", options=sorted(df_final["category_base"].unique()), index=sorted(df_final["category_base"].unique()).index("OPEN") if "OPEN" in df_final["category_base"].unique() else 0)
gender = st.sidebar.selectbox("Gender Seat Type:", options=["GN", "FO"], format_func=lambda x: "Gender-Neutral (GN)" if x == "GN" else "Female-Only (FO)")
quota = st.sidebar.selectbox("Quota:", options=["AI", "HS", "OS"], format_func=lambda x: "All India (AI)" if x == "AI" else ("Home State (HS)" if x == "HS" else "Other State (OS)"))

st.sidebar.markdown("---")
st.sidebar.markdown("**About Dataset**")
st.sidebar.info(f"📊 **432,524** JoSAA Records  \n📅 **8 Years Data** (2018–2025)  \n🏫 **IITs, NITs, IIITs, GFTIs**")

# --- Main App Header ---
st.markdown('<div class="main-header">🎓 JEE Admission Counselor & Analytics Portal</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Data-driven admission counseling & historical cut-off analytics based on 2018–2025 JoSAA Data</div>', unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 ML Admission Predictor",
    "📈 Historical Cutoff Trends",
    "📊 Tier & Branch Analytics",
    "🔮 ML Model Performance"
])

# ---------------------------------------------------------
# TAB 1: ML ADMISSION PREDICTOR
# ---------------------------------------------------------
with tab1:
    st.subheader("Personalized College & Branch Admission Chance Predictor")
    st.markdown("Filter options based on your rank cushion margin ($\text{Closing Rank} - \text{Your Rank}$).")
    
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        inst_types = st.multiselect("Filter Institute Types:", options=sorted(df_final["institute_type"].unique()), default=sorted(df_final["institute_type"].unique()))
    with col_f2:
        program_keyword = st.text_input("Search Branch / Program (e.g. Computer Science, Mechanical):", value="")
    with col_f3:
        margin_range = st.slider("Rank Cushion Margin (Closing Rank - Your Rank):", min_value=-5000, max_value=20000, value=(-1000, 10000), step=500)

    # Filter logic
    data_filtered = df_final[
        (df_final["category_base"] == category) &
        (df_final["gender_short"] == gender) &
        (df_final["quota"] == quota)
    ].copy()
    
    if inst_types:
        data_filtered = data_filtered[data_filtered["institute_type"].isin(inst_types)]
    if program_keyword:
        data_filtered = data_filtered[data_filtered["program"].str.contains(program_keyword, case=False, na=False)]
        
    # Get latest available cutoff per institute-program
    data_filtered = data_filtered.sort_values("year", ascending=False)
    latest_options = data_filtered.drop_duplicates(
        subset=["institute", "program", "category_base", "gender_short", "quota"],
        keep="first"
    ).copy()
    
    latest_options["margin"] = latest_options["closing_rank"] - user_rank
    
    results = latest_options[
        (latest_options["margin"] >= margin_range[0]) &
        (latest_options["margin"] <= margin_range[1])
    ].copy()
    
    def assign_verdict(m):
        if m < -200:
            return "🔴 Out of Reach"
        elif m < 0:
            return "🟡 Borderline (Risky)"
        elif m <= 1500:
            return "✅ Safe"
        else:
            return "🟢 Comfortable"

    results["verdict"] = results["margin"].apply(assign_verdict)
    results = results.sort_values("margin", ascending=True)

    # Summary Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Colleges Found", f"{len(results):,}")
    m2.metric("🟢 Comfortable Options", f"{(results['verdict'] == '🟢 Comfortable').sum():,}")
    m3.metric("✅ Safe Options", f"{(results['verdict'] == '✅ Safe').sum():,}")
    m4.metric("🟡 Borderline / Risky", f"{(results['verdict'] == '🟡 Borderline (Risky)').sum():,}")
    
    st.markdown("---")
    
    if results.empty:
        st.warning("No colleges found matching your search criteria. Try widening the margin slider or selecting different branch/institute types.")
    else:
        st.markdown(f"### Eligible Choices for Rank **{user_rank:,}** ({category} | {gender} | {quota})")
        
        display_df = results[[
            "institute", "institute_type", "program", "year", "closing_rank", "margin", "verdict"
        ]].copy()
        display_df["institute"] = display_df["institute"].apply(short_name)
        display_df.columns = ["Institute", "Type", "Academic Program", "Reference Year", "Closing Rank", "Margin (Cushion)", "Admission Verdict"]
        
        st.dataframe(
            display_df,
            column_config={
                "Closing Rank": st.column_config.NumberColumn(format="%d"),
                "Margin (Cushion)": st.column_config.NumberColumn(format="%+d"),
            },
            use_container_width=True,
            hide_index=True
        )

# ---------------------------------------------------------
# TAB 2: HISTORICAL CUTOFF TRENDS
# ---------------------------------------------------------
with tab2:
    st.subheader("Historical Cutoff & YoY Closing Rank Trend Analytics")
    
    t_col1, t_col2 = st.columns(2)
    with t_col1:
        selected_inst = st.selectbox("Select Institute:", options=sorted(df_full["institute"].unique()), index=0)
    with t_col2:
        inst_programs = sorted(df_full[df_full["institute"] == selected_inst]["program"].unique())
        selected_prog = st.selectbox("Select Academic Program:", options=inst_programs, index=0)
        
    trend_df = df_final[
        (df_final["institute"] == selected_inst) &
        (df_final["program"] == selected_prog) &
        (df_final["category_base"] == category) &
        (df_final["gender_short"] == gender) &
        (df_final["quota"] == quota)
    ].sort_values("year")
    
    if trend_df.empty:
        st.warning("No specific trend data found for this exact Category/Gender/Quota combination. Displaying general trend across available categories...")
        trend_df = df_final[
            (df_final["institute"] == selected_inst) &
            (df_final["program"] == selected_prog)
        ].groupby("year")["closing_rank"].median().reset_index()
        
        if HAS_PLOTLY:
            fig = px.line(trend_df, x="year", y="closing_rank", markers=True,
                          title=f"Median Closing Rank Trend (2018–2025): {short_name(selected_inst)}",
                          labels={"closing_rank": "Median Closing Rank", "year": "Year"},
                          color_discrete_sequence=["#1E3A8A"])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.line_chart(trend_df.set_index("year")["closing_rank"])
    else:
        if HAS_PLOTLY:
            fig = px.line(trend_df, x="year", y="closing_rank", markers=True,
                          title=f"Closing Rank Cutoff Trend (2018–2025): {short_name(selected_inst)}",
                          labels={"closing_rank": "Closing Rank Cutoff", "year": "Year"},
                          color_discrete_sequence=["#2563EB"])
            fig.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.line_chart(trend_df.set_index("year")["closing_rank"])
        
        # Trend Statistics
        stat_c1, stat_c2, stat_c3, stat_c4 = st.columns(4)
        first_rank = trend_df["closing_rank"].iloc[0]
        last_rank = trend_df["closing_rank"].iloc[-1]
        pct_change = ((last_rank - first_rank) / first_rank) * 100
        
        stat_c1.metric("Earliest Rank Cutoff", f"{int(first_rank):,}")
        stat_c2.metric("Latest Rank Cutoff", f"{int(last_rank):,}")
        stat_c3.metric("YoY Rank Shift %", f"{pct_change:+.1f}%")
        stat_c4.metric("Data Years Available", f"{len(trend_df)} Years")

# ---------------------------------------------------------
# TAB 3: TIER & BRANCH ANALYTICS
# ---------------------------------------------------------
with tab3:
    st.subheader("Institute Tier Hierarchy & Branch Competitiveness Matrix")
    
    b_col1, b_col2 = st.columns(2)
    
    with b_col1:
        st.markdown("### Top Colleges by Branch (Median Closing Rank)")
        target_branch = st.selectbox("Choose Branch for Ranking:", options=["Computer Science", "Electronics", "Mechanical", "Civil", "Electrical"], index=0)
        
        top_branch_df = df_final[
            (df_final["program"].str.contains(target_branch, case=False, na=False)) &
            (df_final["category_base"] == "OPEN") &
            (df_final["gender_short"] == "GN")
        ].groupby("institute")["closing_rank"].median().reset_index().sort_values("closing_rank").head(10)
        
        top_branch_df["institute"] = top_branch_df["institute"].apply(short_name)
        
        if HAS_PLOTLY:
            fig_bar = px.bar(top_branch_df, x="closing_rank", y="institute", orientation="h",
                             title=f"Top 10 Institutes for {target_branch} (Open Category)",
                             labels={"closing_rank": "Median Closing Rank", "institute": "Institute"},
                             color="closing_rank", color_continuous_scale="Blues_r")
            fig_bar.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.dataframe(top_branch_df, use_container_width=True, hide_index=True)
        
    with b_col2:
        st.markdown("### Seat Volume Distribution by Institute Type")
        tier_counts = df_final["institute_type"].value_counts().reset_index()
        tier_counts.columns = ["Institute Type", "Total Records"]
        
        if HAS_PLOTLY:
            fig_pie = px.pie(tier_counts, values="Total Records", names="Institute Type",
                             title="Distribution of JoSAA Admission Seats (IIT / NIT / IIIT / GFTI)",
                             color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.bar_chart(tier_counts.set_index("Institute Type"))

# ---------------------------------------------------------
# TAB 4: ML MODEL PERFORMANCE
# ---------------------------------------------------------
with tab4:
    st.subheader("Machine Learning Model Evaluation & Feature Importance (Leakage-Free)")
    st.markdown("""
    Supervised learning models were evaluated **without target leakage** by training on student profile attributes (Category, Quota, Institute Type, Branch, Region, IIT Generation) on **2018–2023** data and testing on **2024–2025** data.
    """)
    
    m_col1, m_col2 = st.columns(2)
    
    with m_col1:
        st.markdown("### Leakage-Free Model Evaluation (2024–2025 Test Set)")
        model_perf = pd.DataFrame({
            "Machine Learning Model": ["Gradient Boosting Classifier", "Extra Trees Classifier", "Random Forest Classifier", "Logistic Regression"],
            "Accuracy": ["79.64%", "78.38%", "77.76%", "48.30%"],
            "Precision": ["80.09%", "78.73%", "77.75%", "34.55%"],
            "Recall": ["79.64%", "78.38%", "77.76%", "48.30%"],
            "F1-Score": ["79.60%", "78.30%", "77.50%", "40.21%"]
        })
        st.dataframe(model_perf, use_container_width=True, hide_index=True)
        
    with m_col2:
        st.markdown("### Feature Importances (No Target Leakage)")
        feat_imp = pd.DataFrame({
            "Feature": ["Category Base", "Program Discipline", "Quota", "Institute Type", "IIT Generation", "Is Top Tier", "NIT Region", "Year", "Gender Short", "Is New-Age Program"],
            "Importance (%)": [39.59, 16.25, 9.28, 8.15, 7.64, 6.15, 4.65, 4.31, 3.57, 0.40]
        }).sort_values("Importance (%)", ascending=True)
        
        if HAS_PLOTLY:
            fig_feat = px.bar(feat_imp, x="Importance (%)", y="Feature", orientation="h",
                              title="Predictive Weight of Student Profile Features",
                              color="Importance (%)", color_continuous_scale="Purples")
            st.plotly_chart(fig_feat, use_container_width=True)
        else:
            st.dataframe(feat_imp, use_container_width=True, hide_index=True)

st.markdown("---")
st.markdown("<center><small>JEE Admission Counselor & Analytics Portal | Developed with Streamlit, Scikit-Learn, and Plotly</small></center>", unsafe_allow_html=True)
