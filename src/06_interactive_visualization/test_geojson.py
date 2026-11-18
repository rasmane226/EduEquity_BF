
import json
from pathlib import Path

GEOJSON_FILE = (
    Path(__file__).resolve().parent
    / "assets"
    / "geojson"
    / "burkina_faso_regions.geojson"
)

with open(GEOJSON_FILE, "r", encoding="utf-8-sig") as file:
    geojson = json.load(file)

features = geojson["features"]

print("=" * 65)
print("VALIDATION DU GEOJSON - EDUEQUITY BF")
print("=" * 65)

print("Type :", geojson["type"])
print("Nombre de régions :", len(features))

print("\nIDENTIFICATION DES REGIONS")

for feature in features:

    properties = feature["properties"]

    print(
        properties["admin1Pcod"],
        "-",
        properties["admin1Name"]
    )

assert geojson["type"] == "FeatureCollection"
assert len(features) == 13

region_names = [
    feature["properties"]["admin1Name"]
    for feature in features
]

assert len(set(region_names)) == 13

print("\nVALIDATION REUSSIE")
print("13 régions identifiées.")
print("=" * 65)
