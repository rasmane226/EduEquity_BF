
import pandas as pd
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]

SOURCE_FILE = (
    ROOT_DIR / "data" / "01_raw_data" /
    "donnees_education_bf.xlsx"
)

feuilles = ["Feuil2", "Feuil4", "Feuil5"]

excel = pd.ExcelFile(SOURCE_FILE)

for feuille in feuilles:

    df = pd.read_excel(excel, sheet_name=feuille)

    print("\n" + "=" * 65)
    print(f"ANALYSE DE {feuille}")
    print("=" * 65)

    print("\nDimensions :", df.shape)

    print("\nColonnes :")
    for colonne in df.columns:
        print("-", colonne)

    print("\nPremières observations :")
    print(df.head(10).to_string(index=False))

    print("\nDernières observations :")
    print(df.tail(5).to_string(index=False))
