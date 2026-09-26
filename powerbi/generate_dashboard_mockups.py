import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Use standard matplotlib styles
plt.style.use('ggplot')
plt.rcParams['font.sans-serif'] = 'Arial'

def create_powerbi_dashboards():
    print("Creating Power BI Dashboard Visual Mockups...")
    
    proc_path = os.path.join("data", "processed", "josaa_featured.csv")
    if not os.path.exists(proc_path):
        proc_path = os.path.join("..", "data", "processed", "josaa_featured.csv")
        
    df = pd.read_csv(proc_path)
    
    out_dir = os.path.join("powerbi", "dashboards")
    os.makedirs(out_dir, exist_ok=True)
    
    # ---------------------------------------------------------
    # DASHBOARD 1: EXECUTIVE OVERVIEW
    # ---------------------------------------------------------
    fig = plt.figure(figsize=(16, 9), dpi=150)
    fig.patch.set_facecolor('#F8FAFC')
    
    fig.text(0.05, 0.93, "Power BI Dashboard: Executive Overview & Admission Key Metrics", 
             fontsize=20, fontweight='bold', color='#0F172A')
    fig.text(0.05, 0.90, "JoSAA Counseling Analytics (2018-2025) | Star Schema Data Model", 
             fontsize=12, color='#475569')
             
    kpis = [
        ("432,524", "TOTAL ADMISSION RECORDS", "#2563EB"),
        ("136", "PARTICIPATING INSTITUTES", "#059669"),
        ("8 YEARS", "HISTORICAL TIMELINE", "#D97706"),
        ("79.64%", "LEAKAGE-FREE ML ACCURACY", "#7C3AED")
    ]
    for i, (val, title, color) in enumerate(kpis):
        ax_kpi = fig.add_axes([0.05 + i*0.225, 0.76, 0.20, 0.10])
        ax_kpi.set_facecolor('white')
        ax_kpi.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
        for spine in ax_kpi.spines.values():
            spine.set_color('#E2E8F0')
        ax_kpi.text(0.5, 0.65, val, fontsize=20, fontweight='bold', color=color, ha='center', va='center')
        ax_kpi.text(0.5, 0.25, title, fontsize=9, fontweight='bold', color='#64748B', ha='center', va='center')

    ax1 = fig.add_axes([0.05, 0.10, 0.43, 0.58])
    ax1.set_facecolor('white')
    yoy_seats = df.groupby('year').size().reset_index(name='count')
    bars = ax1.bar(yoy_seats['year'], yoy_seats['count'], color='#3B82F6', width=0.55, edgecolor='#1D4ED8')
    ax1.set_title("Annual Admission Seat Volume Growth (2018-2025)", fontsize=13, fontweight='bold', color='#1E293B', pad=12)
    ax1.set_ylabel("Total Recorded Seats", fontsize=11, color='#475569')
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    for bar in bars:
        height = bar.get_height()
        ax1.annotate(f'{height:,}', xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='bold', color='#1E293B')

    ax2 = fig.add_axes([0.53, 0.10, 0.42, 0.58])
    ax2.set_facecolor('white')
    inst_counts = df['institute_type'].value_counts()
    colors = ['#2563EB', '#10B981', '#F59E0B', '#6366F1']
    wedges, texts, autotexts = ax2.pie(inst_counts, labels=inst_counts.index, autopct='%1.1f%%',
                                        startangle=140, colors=colors, textprops=dict(color="#1E293B", fontweight='bold'))
    ax2.set_title("Seat Proportion by Institute Category", fontsize=13, fontweight='bold', color='#1E293B', pad=12)

    plt.savefig(os.path.join(out_dir, "01_executive_overview_dashboard.png"), bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    print("Saved 01_executive_overview_dashboard.png")

    # ---------------------------------------------------------
    # DASHBOARD 2: CUTOFF & COMPETITIVENESS
    # ---------------------------------------------------------
    fig = plt.figure(figsize=(16, 9), dpi=150)
    fig.patch.set_facecolor('#F8FAFC')
    
    fig.text(0.05, 0.93, "Power BI Dashboard: Cutoff Ranks & Tier Competitiveness", 
             fontsize=20, fontweight='bold', color='#0F172A')
    fig.text(0.05, 0.90, "Comparative Opening/Closing Rank Analysis by Tier, Category, and Gender", 
             fontsize=12, color='#475569')

    ax1 = fig.add_axes([0.05, 0.10, 0.43, 0.72])
    ax1.set_facecolor('white')
    tier_ranks = df.groupby('institute_type')['closing_rank'].median().reset_index().sort_values('closing_rank')
    bars = ax1.barh(tier_ranks['institute_type'], tier_ranks['closing_rank'], color='#6366F1', height=0.5)
    ax1.set_title("Median Closing Rank Cutoff by Institute Tier (Open Category)", fontsize=13, fontweight='bold', color='#1E293B', pad=12)
    ax1.set_xlabel("Median Closing Rank", fontsize=11, color='#475569')
    ax1.grid(axis='x', linestyle='--', alpha=0.7)
    ax1.invert_yaxis()
    for bar in bars:
        width = bar.get_width()
        ax1.annotate(f'{int(width):,}', xy=(width, bar.get_y() + bar.get_height()/2),
                    xytext=(5, 0), textcoords="offset points", ha='left', va='center', fontsize=10, fontweight='bold')

    ax2 = fig.add_axes([0.53, 0.10, 0.42, 0.72])
    ax2.set_facecolor('white')
    cat_ranks = df.groupby('category_base')['closing_rank'].median().reset_index().sort_values('closing_rank')
    bars = ax2.bar(cat_ranks['category_base'], cat_ranks['closing_rank'], color='#8B5CF6', width=0.55)
    ax2.set_title("Median Closing Rank Spread Across Categories", fontsize=13, fontweight='bold', color='#1E293B', pad=12)
    ax2.set_ylabel("Median Closing Rank Cutoff", fontsize=11, color='#475569')
    ax2.set_xlabel("Category Base", fontsize=11, color='#475569')
    ax2.grid(axis='y', linestyle='--', alpha=0.7)

    plt.savefig(os.path.join(out_dir, "02_cutoff_competitiveness_dashboard.png"), bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    print("Saved 02_cutoff_competitiveness_dashboard.png")

    # ---------------------------------------------------------
    # DASHBOARD 3: BRANCH TREND ANALYTICS
    # ---------------------------------------------------------
    fig = plt.figure(figsize=(16, 9), dpi=150)
    fig.patch.set_facecolor('#F8FAFC')
    
    fig.text(0.05, 0.93, "Power BI Dashboard: Branch & Academic Program Trends", 
             fontsize=20, fontweight='bold', color='#0F172A')
    fig.text(0.05, 0.90, "YoY Cutoff Trends for Top Disciplines (CSE, ECE, ME, CE, EE)", 
             fontsize=12, color='#475569')

    ax1 = fig.add_axes([0.05, 0.10, 0.43, 0.72])
    ax1.set_facecolor('white')
    branches = ['CS', 'Electrical_Electronics', 'Mechanical', 'Civil']
    branch_colors = {'CS': '#E11D48', 'Electrical_Electronics': '#2563EB', 'Mechanical': '#D97706', 'Civil': '#059669'}
    
    for b in branches:
        b_data = df[df['program_category'] == b].groupby('year')['closing_rank'].median().reset_index()
        ax1.plot(b_data['year'], b_data['closing_rank'], marker='o', linewidth=2.5, label=b, color=branch_colors[b])
        
    ax1.set_title("YoY Median Closing Rank Trajectory (2018-2025)", fontsize=13, fontweight='bold', color='#1E293B', pad=12)
    ax1.set_ylabel("Median Closing Rank", fontsize=11, color='#475569')
    ax1.grid(True, linestyle='--', alpha=0.7)
    ax1.legend(loc='upper right')

    ax2 = fig.add_axes([0.53, 0.10, 0.42, 0.72])
    ax2.set_facecolor('white')
    top_prog = df.groupby('program')['closing_rank'].median().reset_index().sort_values('closing_rank').head(10)
    top_prog['program_short'] = top_prog['program'].apply(lambda x: x[:35] + '...' if len(x)>35 else x)
    
    bars = ax2.barh(top_prog['program_short'], top_prog['closing_rank'], color='#0D9488')
    ax2.set_title("Top 10 Most Competitive Academic Programs", fontsize=13, fontweight='bold', color='#1E293B', pad=12)
    ax2.set_xlabel("Median Closing Rank", fontsize=11, color='#475569')
    ax2.grid(axis='x', linestyle='--', alpha=0.7)
    ax2.invert_yaxis()

    plt.savefig(os.path.join(out_dir, "03_branch_trend_analytics_dashboard.png"), bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    print("Saved 03_branch_trend_analytics_dashboard.png")

    # ---------------------------------------------------------
    # DASHBOARD 4: ML ADMISSION PREDICTOR (LEAKAGE-FREE)
    # ---------------------------------------------------------
    fig = plt.figure(figsize=(16, 9), dpi=150)
    fig.patch.set_facecolor('#F8FAFC')
    
    fig.text(0.05, 0.93, "Power BI Dashboard: ML Admission Predictor (Leakage-Free)", 
             fontsize=20, fontweight='bold', color='#0F172A')
    fig.text(0.05, 0.90, "Leakage-Free Machine Learning Metrics (Trained on 2018-2023, Tested on 2024-2025)", 
             fontsize=12, color='#475569')

    ax1 = fig.add_axes([0.05, 0.10, 0.43, 0.72])
    ax1.set_facecolor('white')
    feat_df = pd.DataFrame({
        'Feature': ['category_base', 'program_category', 'quota', 'institute_type', 'iit_generation', 'is_top_tier_college', 'nit_region'],
        'Importance': [0.396, 0.163, 0.093, 0.082, 0.076, 0.061, 0.047]
    }).sort_values('Importance', ascending=True)
    
    ax1.barh(feat_df['Feature'], feat_df['Importance'], color='#8B5CF6')
    ax1.set_title("Feature Weight in Admission Accessibility Classification", fontsize=13, fontweight='bold', color='#1E293B', pad=12)
    ax1.set_xlabel("Relative Importance Score", fontsize=11, color='#475569')
    ax1.grid(axis='x', linestyle='--', alpha=0.7)

    ax2 = fig.add_axes([0.53, 0.10, 0.42, 0.72])
    ax2.set_facecolor('white')
    models_df = pd.DataFrame({
        'Model': ['Gradient Boost', 'Extra Trees', 'Random Forest', 'Logistic Reg.'],
        'Accuracy': [79.64, 78.38, 77.76, 48.30]
    })
    bars = ax2.bar(models_df['Model'], models_df['Accuracy'], color=['#10B981', '#3B82F6', '#6366F1', '#F59E0B'], width=0.5)
    ax2.set_ylim(0, 100)
    ax2.set_title("Leakage-Free ML Model Test Accuracy (%)", fontsize=13, fontweight='bold', color='#1E293B', pad=12)
    ax2.set_ylabel("Accuracy (%)", fontsize=11, color='#475569')
    ax2.grid(axis='y', linestyle='--', alpha=0.7)
    for bar in bars:
        height = bar.get_height()
        ax2.annotate(f'{height:.2f}%', xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.savefig(os.path.join(out_dir, "04_ml_admission_predictor_dashboard.png"), bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    print("Saved 04_ml_admission_predictor_dashboard.png")
    print("All Power BI dashboard visual mockups created successfully in powerbi/dashboards/")

if __name__ == "__main__":
    create_powerbi_dashboards()
