import pandas as pd
import numpy as np
import os

def generate_powerbi_star_schema():
    print("Generating Power BI Star-Schema Datasets...")
    
    # Path to featured dataset
    proc_path = os.path.join("data", "processed", "josaa_featured.csv")
    if not os.path.exists(proc_path):
        proc_path = os.path.join("..", "data", "processed", "josaa_featured.csv")
        
    df = pd.read_csv(proc_path)
    print(f"Loaded dataset: {len(df):,} rows")
    
    export_dir = os.path.join("powerbi", "exports")
    os.makedirs(export_dir, exist_ok=True)
    
    # --- 1. DIM_INSTITUTE ---
    dim_institute = df[[
        "institute", "institute_type", "iit_generation", "nit_region", "is_top_tier_college"
    ]].drop_duplicates().reset_index(drop=True)
    
    dim_institute["institute_id"] = range(1, len(dim_institute) + 1)
    
    def get_short_name(name):
        return (name
                .replace("Indian Institute of Technology", "IIT")
                .replace("National Institute of Technology", "NIT")
                .replace("Indian Institute of Information Technology", "IIIT"))
                
    dim_institute["institute_short_name"] = dim_institute["institute"].apply(get_short_name)
    
    dim_institute = dim_institute[[
        "institute_id", "institute", "institute_short_name", "institute_type", 
        "iit_generation", "nit_region", "is_top_tier_college"
    ]]
    dim_institute.to_csv(os.path.join(export_dir, "Dim_Institute.csv"), index=False)
    print(f"Exported Dim_Institute.csv ({len(dim_institute)} rows)")
    
    # --- 2. DIM_PROGRAM ---
    dim_program = df[[
        "program", "program_category", "is_new_age_program"
    ]].drop_duplicates().reset_index(drop=True)
    
    dim_program["program_id"] = range(1, len(dim_program) + 1)
    dim_program = dim_program[[
        "program_id", "program", "program_category", "is_new_age_program"
    ]]
    dim_program.to_csv(os.path.join(export_dir, "Dim_Program.csv"), index=False)
    print(f"Exported Dim_Program.csv ({len(dim_program)} rows)")
    
    # --- 3. DIM_CATEGORY ---
    dim_category = df[[
        "category_base", "gender_short", "seat_type", "gender", "quota"
    ]].drop_duplicates().reset_index(drop=True)
    
    dim_category["category_id"] = range(1, len(dim_category) + 1)
    dim_category = dim_category[[
        "category_id", "category_base", "gender_short", "seat_type", "gender", "quota"
    ]]
    dim_category.to_csv(os.path.join(export_dir, "Dim_Category.csv"), index=False)
    print(f"Exported Dim_Category.csv ({len(dim_category)} rows)")
    
    # --- 4. FACT_ADMISSIONS ---
    # Merge keys to create Fact Table
    fact = df.merge(dim_institute, on=["institute", "institute_type", "iit_generation", "nit_region", "is_top_tier_college"], how="left")
    fact = fact.merge(dim_program, on=["program", "program_category", "is_new_age_program"], how="left")
    fact = fact.merge(dim_category, on=["category_base", "gender_short", "seat_type", "gender", "quota"], how="left")
    
    fact["admission_id"] = range(1, len(fact) + 1)
    
    fact_admissions = fact[[
        "admission_id", "institute_id", "program_id", "category_id",
        "year", "round", "opening_rank", "closing_rank", "rank_window",
        "competitiveness_score", "is_special_round", "is_pwd", "accessibility_label"
    ]]
    
    fact_admissions.to_csv(os.path.join(export_dir, "Fact_Admissions.csv"), index=False)
    print(f"Exported Fact_Admissions.csv ({len(fact_admissions):,} rows)")
    print("All Power BI Star Schema datasets generated successfully in powerbi/exports/")

if __name__ == "__main__":
    generate_powerbi_star_schema()
