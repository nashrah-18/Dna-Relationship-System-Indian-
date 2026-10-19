import pandas as pd
import sys
import os

sys.path.append(os.getcwd())
from app.database import SessionLocal, DNAProfile

csv_path = "data/clean_dna_dataset.csv"

if not os.path.exists(csv_path):
    print(f"Error: CSV file not found at {csv_path}")
    sys.exit(1)

df = pd.read_csv(csv_path)
session = SessionLocal()

session.query(DNAProfile).delete()
session.commit()

def clean_val(x):
    if pd.isna(x) or x == '-':
        return 0
    return float(x) if '.' in str(x) else int(x)

for _, row in df.iterrows():
    profile = DNAProfile(
        sample_id=str(row["Sample_ID"]),
        sex=str(row["Sex"]),
        amel=clean_val(row["AMEL"]),
        d3s1358=clean_val(row["D3S1358"]),
        vwa=clean_val(row["VWA"]),
        d16s539=clean_val(row["D16S539"]),
        csf1po=clean_val(row["CSF1PO"]),
        tpox=clean_val(row["TPOX"]),
        d8s1179=clean_val(row["D8S1179"]),
        d21s11=clean_val(row["D21S11"]),
        d18s51=clean_val(row["D18S51"]),
        dys391=clean_val(row["DYS391"]),
        d2s441=clean_val(row["D2S441"]),
        d19s433=clean_val(row["D19S433"]),
        tho1=clean_val(row["THO1"]),
        fga=clean_val(row["FGA"]),
        d22s1045=clean_val(row["D22S1045"]),
        d5s818=clean_val(row["D5S818"]),
        d13s317=clean_val(row["D13S317"]),
        d7s820=clean_val(row["D7S820"]),
        se33=clean_val(row["SE33"]),
        d10s1248=clean_val(row["D10S1248"]),
        d1s1656=clean_val(row["D1S1656"]),
        d12s391=clean_val(row["D12S391"]),
        d2s1338=clean_val(row["D2S1338"])
    )
    session.add(profile)

session.commit()
session.close()
print(f"Successfully loaded {len(df)} DNA profiles into database.")