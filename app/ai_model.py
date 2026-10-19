import os
import numpy as np
import pandas as pd
from app.database import SessionLocal, DNAProfile

NUMERIC_COLUMNS = [
    'D3S1358', 'VWA', 'D16S539', 'CSF1PO', 'TPOX', 'D8S1179', 'D21S11',
    'D18S51', 'DYS391', 'D2S441', 'D19S433', 'THO1', 'FGA', 'D22S1045',
    'D5S818', 'D13S317', 'D7S820', 'SE33', 'D10S1248', 'D1S1656',
    'D12S391', 'D2S1338'
]

def get_relationship_from_percentage(percent):
    if percent >= 99:
        return "Identical Twin / Same person", "High"
    elif 85 <= percent <= 98:
        return "Parent-Child", "High"
    elif 75 <= percent <= 84:
        return "Siblings", "Medium"
    elif 60 <= percent <= 74:
        return "Cousins", "Medium"
    elif 40 <= percent <= 59:
        return "Close Relative", "Low"
    else:
        return "Unrelated", "Unknown"

def get_all_profiles_as_dataframe():
    session = SessionLocal()
    profiles = session.query(DNAProfile).all()
    session.close()
    if profiles:
        data = []
        for p in profiles:
            row = {'Sample_ID': p.sample_id, 'Sex': p.sex}
            for col in NUMERIC_COLUMNS:
                row[col] = getattr(p, col.lower())
            data.append(row)
        df = pd.DataFrame(data)
        print(f"[INFO] Loaded {len(df)} profiles from database.")
    else:
        csv_path = "data/clean_dna_dataset.csv"
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            keep = ['Sample_ID', 'Sex'] + NUMERIC_COLUMNS
            df = df[keep]
            print(f"[INFO] Loaded {len(df)} profiles from CSV.")
        else:
            raise FileNotFoundError("No data source found.")
    df[NUMERIC_COLUMNS] = df[NUMERIC_COLUMNS].apply(pd.to_numeric, errors='coerce').fillna(0)
    return df

_df_cache = None

def predict_match(df, id1, id2):
    id1, id2 = str(id1).strip(), str(id2).strip()
    mask1 = df['Sample_ID'].astype(str).str.strip() == id1
    mask2 = df['Sample_ID'].astype(str).str.strip() == id2
    row1 = df[mask1]
    row2 = df[mask2]
    if row1.empty or row2.empty:
        return 0.0, "ID not found", "Low"
    p1 = row1[NUMERIC_COLUMNS].values[0].astype(float)
    p2 = row2[NUMERIC_COLUMNS].values[0].astype(float)
    diff = np.abs(p1 - p2)
    matched = diff <= 1
    percent = (matched.sum() / len(matched)) * 100
    relationship, confidence = get_relationship_from_percentage(percent)
    return round(percent, 2), relationship, confidence

def get_relationship(profile1, profile2):
    global _df_cache
    if _df_cache is None:
        _df_cache = get_all_profiles_as_dataframe()
    percent, relationship, confidence = predict_match(_df_cache, profile1.sample_id, profile2.sample_id)
    print(f"[PREDICT] {profile1.sample_id} vs {profile2.sample_id}: {percent}% → {relationship} ({confidence})")
    return relationship, confidence, percent