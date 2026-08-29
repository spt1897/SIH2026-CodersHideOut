import os
import requests
import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import polygonize, unary_union

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

OUTPUT_DIR = "D:/File-Storage/static_features/openstreet-shapefile/data/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

OUTPUT_SHP = os.path.join(OUTPUT_DIR, "india_states.shp")

# Northeast India states
NE_STATES = {
    "Arunachal Pradesh",
    "Assam",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Sikkim",
    "Tripura",
}


def download_osm_states():

    print("[+] Querying OSM for Northeast state boundaries...")

    query = r"""
    [out:json][timeout:180];

    (
      relation
        ["boundary"="administrative"]
        ["admin_level"="4"]
        ["name"="Arunachal Pradesh"];

      relation
        ["boundary"="administrative"]
        ["admin_level"="4"]
        ["name"="Assam"];

      relation
        ["boundary"="administrative"]
        ["admin_level"="4"]
        ["name"="Manipur"];

      relation
        ["boundary"="administrative"]
        ["admin_level"="4"]
        ["name"="Meghalaya"];

      relation
        ["boundary"="administrative"]
        ["admin_level"="4"]
        ["name"="Mizoram"];

      relation
        ["boundary"="administrative"]
        ["admin_level"="4"]
        ["name"="Nagaland"];

      relation
        ["boundary"="administrative"]
        ["admin_level"="4"]
        ["name"="Sikkim"];

      relation
        ["boundary"="administrative"]
        ["admin_level"="4"]
        ["name"="Tripura"];
    );

    out body;
    >;
    out skel qt;
    """

    # Try multiple Overpass servers
    servers = [
        "https://overpass.kumi.systems/api/interpreter",
        "https://overpass.private.coffee/api/interpreter",
        "https://overpass-api.de/api/interpreter",
    ]

    last_error = None

    for url in servers:

        try:

            print(f"[+] Trying: {url}")

            response = requests.post(
                url,
                data={"data": query},
                headers={
                    "User-Agent": "SIH2026-Geostatic-Preprocessor/1.0",
                    "Accept": "application/json",
                },
                timeout=240
            )

            response.raise_for_status()

            print("[+] OSM query successful")

            return response.json()

        except requests.RequestException as e:

            print(f"[-] Failed: {e}")
            last_error = e

    raise RuntimeError(
        f"All Overpass servers failed. Last error: {last_error}"
    )

def build_state_polygons(data):
    elements = data["elements"]

    nodes = {}
    ways = {}
    relations = []

    for element in elements:

        if element["type"] == "node":
            nodes[element["id"]] = (
                element["lon"],
                element["lat"]
            )

        elif element["type"] == "way":
            ways[element["id"]] = element.get("nodes", [])

        elif element["type"] == "relation":
            relations.append(element)

    records = []

    for relation in relations:

        tags = relation.get("tags", {})

        name = tags.get("name")
        admin_level = tags.get("admin_level")

        if admin_level != "4":
            continue

        if name not in NE_STATES:
            continue

        print(f"[+] Processing {name}")

        outer_lines = []
        inner_lines = []

        for member in relation.get("members", []):

            if member["type"] != "way":
                continue

            way_id = member["ref"]
            role = member.get("role", "")

            if way_id not in ways:
                continue

            coords = []

            for node_id in ways[way_id]:

                if node_id in nodes:
                    coords.append(nodes[node_id])

            if len(coords) < 2:
                continue

            if role == "inner":
                inner_lines.append(coords)

            else:
                outer_lines.append(coords)

        # Build polygons from connected outer lines
        outer_geoms = []

        for coords in outer_lines:

            try:
                poly = Polygon(coords)

                if not poly.is_valid:
                    poly = poly.buffer(0)

                if not poly.is_empty:
                    outer_geoms.append(poly)

            except Exception:
                continue

        if not outer_geoms:
            print(f"[-] Could not build geometry for {name}")
            continue

        geometry = unary_union(outer_geoms)

        if geometry.is_empty:
            continue

        records.append({
            "osm_id": relation["id"],
            "name": name,
            "admin_level": 4,
            "geometry": geometry
        })

    return records


def main():

    print("[+] Downloading state boundaries...")

    data = download_osm_states()

    print(f"[+] Downloaded {len(data['elements'])} OSM elements")

    records = build_state_polygons(data)

    if not records:
        raise RuntimeError(
            "No state polygons were created."
        )

    gdf = gpd.GeoDataFrame(
        records,
        crs="EPSG:4326"
    )

    # Keep only required fields
    gdf = gdf[
        [
            "osm_id",
            "name",
            "admin_level",
            "geometry"
        ]
    ]

    print("\n========== STATES ==========")

    print(
        gdf[
            ["osm_id", "name", "admin_level"]
        ].to_string(index=False)
    )

    print("\n[+] Saving:", OUTPUT_SHP)

    gdf.to_file(
        OUTPUT_SHP,
        driver="ESRI Shapefile",
        encoding="UTF-8"
    )

    print("\n[+] DONE")
    print("[+] Files created:")
    print(f"    {OUTPUT_SHP}")
    print(f"    {OUTPUT_SHP.replace('.shp', '.shx')}")
    print(f"    {OUTPUT_SHP.replace('.shp', '.dbf')}")
    print(f"    {OUTPUT_SHP.replace('.shp', '.prj')}")


if __name__ == "__main__":
    main()