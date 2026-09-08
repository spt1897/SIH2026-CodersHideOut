import os
from typing import Dict, Tuple, Any
import h3
import shapely.geometry
import geopandas as gpd
import pandas as pd
import numpy as np
from scipy.spatial import cKDTree
from geopy.distance import geodesic

from src.static_features_extractors.raster_file_config import VECTOR_PATHS

# Bounding box encompassing the entire North-Eastern region of India:
# [min_lon, min_lat, max_lon, max_lat] -> (Sikkim/WB border to Arunachal, South Mizoram to North Arunachal)
NORTHEAST_BBOX = (87.8, 21.5, 97.4, 29.5)


def extract_emergency_nodes(
    bbox: Tuple[float, float, float, float],
    h3_resolution: int,
    top_k: int = 5
) -> Dict[str, Any]:

    min_lat, min_lon, max_lat, max_lon = bbox

    # ----------------------------
    # OSM category keywords
    # ----------------------------
    category_patterns = {
        "police": [
            "police", "police_station", "police station"
        ],
        "fire": [
            "fire_station", "fire station", "fire"
        ],
        "hospital": [
            "hospital", "clinic", "health_post",
            "health post", "doctors", "medical"
        ],
        "traffic_booth": [
            "checkpoint", "police_booth",
            "police booth", "traffic_booth",
            "traffic booth", "control_point",
            "control point", "traffic_signals",
            "traffic signals"
        ]
    }

    target_layers = ["pois", "pois_a", "traffic", "buildings"]

    combined_records = {k: [] for k in category_patterns}

    # ----------------------------
    # Load OSM layers across Entire Northeastern Region
    # ----------------------------
    for layer_name in target_layers:

        path = VECTOR_PATHS.get(layer_name)

        if not path or not os.path.exists(path):
            continue

        try:
            # Query entire Northeastern region bounding box
            gdf = gpd.read_file(path, bbox=NORTHEAST_BBOX)

            if gdf.empty:
                continue

            if gdf.crs is None:
                gdf.set_crs(epsg=4326, inplace=True)
            elif gdf.crs.to_epsg() != 4326:
                gdf = gdf.to_crs(epsg=4326)

            # Check every useful OSM classification column
            candidate_columns = [
                "fclass",
                "amenity",
                "highway",
                "type",
                "building"
            ]

            available_cols = [c for c in candidate_columns if c in gdf.columns]

            if not available_cols:
                continue

            print(f"\n[{layer_name}] Total NE Region Features Loaded: {len(gdf)}")

            for category, keywords in category_patterns.items():

                mask = pd.Series(False, index=gdf.index)

                for col in available_cols:

                    values = gdf[col].astype(str).str.lower()

                    pattern = "|".join(
                        k.replace("_", "[ _]?") for k in keywords
                    )

                    mask |= values.str.contains(pattern, regex=True, na=False)

                matched = gdf[mask].copy()

                if matched.empty:
                    continue

                # Convert polygons to centroid
                matched["geometry"] = matched.geometry.apply(
                    lambda geom:
                    geom
                    if isinstance(geom, shapely.geometry.Point)
                    else geom.centroid
                )

                matched = matched.dropna(subset=["geometry"])

                combined_records[category].append(matched)

                print(f"  {category}: {len(matched)}")

        except Exception as e:
            print(f"Error loading {layer_name}: {e}")

    # ----------------------------
    # Build KD Trees across full NE Region
    # ----------------------------
    emergency_trees = {}

    for category, parts in combined_records.items():

        if not parts:
            emergency_trees[category] = (
                None,
                gpd.GeoDataFrame(geometry=[], crs="EPSG:4326")
            )
            continue

        gdf = gpd.GeoDataFrame(
            pd.concat(parts, ignore_index=True),
            crs="EPSG:4326"
        )

        coords = np.array([[p.x, p.y] for p in gdf.geometry])

        tree = cKDTree(coords)

        emergency_trees[category] = (tree, gdf)

        print(f"KDTree -> {category}: {len(gdf)} total NE nodes indexed")

    # ----------------------------
    # Generate H3 cells STRICTLY for passed target BBox
    # ----------------------------
    poly = h3.LatLngPoly([
        (min_lat, min_lon),
        (min_lat, max_lon),
        (max_lat, max_lon),
        (max_lat, min_lon),
        (min_lat, min_lon)
    ])

    h3_cells = list(h3.polygon_to_cells(poly, res=h3_resolution))

    records = []

    # ----------------------------
    # Query nearest facilities across entire NE Tree
    # ----------------------------
    for cell in h3_cells:

        lat, lon = h3.cell_to_latlng(cell)
        cell_point = (lat, lon)

        def nearest(category):

            tree, gdf = emergency_trees[category]

            if tree is None or gdf.empty:
                return [], [], [], []

            k = min(top_k, len(gdf))

            _, idxs = tree.query([lon, lat], k=k)

            if np.isscalar(idxs):
                idxs = [idxs]

            names = []
            points = []
            dists = []
            contacts = []

            for idx in idxs:

                row = gdf.iloc[int(idx)]
                pt = row.geometry

                names.append(
                    str(row.get("name"))
                    if pd.notna(row.get("name"))
                    else "Unknown Facility"
                )

                points.append(
                    f"SRID=4326;POINT({pt.x} {pt.y})"
                )

                dists.append(
                    round(
                        geodesic(cell_point, (pt.y, pt.x)).km,
                        2
                    )
                )

                phone = "N/A"

                for col in [
                    "phone",
                    "contact:phone",
                    "mobile",
                    "contact"
                ]:
                    if col in row and pd.notna(row[col]):
                        phone = str(row[col])
                        break

                contacts.append(phone)

            return names, points, dists, contacts

        pn, pp, pdist, pc = nearest("police")
        fn, fp, fdist, fc = nearest("fire")
        hn, hp, hdist, hc = nearest("hospital")
        tn, tp, tdist, tc = nearest("traffic_booth")

        records.append({
            "h3_index": cell,

            "police_names": pn,
            "police_points": pp,
            "police_distances_km": pdist,
            "police_contacts": pc,

            "fire_names": fn,
            "fire_points": fp,
            "fire_distances_km": fdist,
            "fire_contacts": fc,

            "hospital_names": hn,
            "hospital_points": hp,
            "hospital_distances_km": hdist,
            "hospital_contacts": hc,

            "traffic_booth_names": tn,
            "traffic_booth_points": tp,
            "traffic_booth_distances_km": tdist,
            "traffic_booth_contacts": tc
        })

    # ----------------------------
    # SQL payload
    # ----------------------------
    sql_tuples = [
        (
            r["h3_index"],
            r["police_names"],
            r["police_points"],
            r["police_distances_km"],
            r["police_contacts"],

            r["fire_names"],
            r["fire_points"],
            r["fire_distances_km"],
            r["fire_contacts"],

            r["hospital_names"],
            r["hospital_points"],
            r["hospital_distances_km"],
            r["hospital_contacts"],

            r["traffic_booth_names"],
            r["traffic_booth_points"],
            r["traffic_booth_distances_km"],
            r["traffic_booth_contacts"]
        )
        for r in records
    ]

    sql_query = """
    INSERT INTO cell_emergency_nodes (
        h3_index,
        police_names, police_points, police_distances_km, police_contacts,
        fire_names, fire_points, fire_distances_km, fire_contacts,
        hospital_names, hospital_points, hospital_distances_km, hospital_contacts,
        traffic_booth_names, traffic_booth_points, traffic_booth_distances_km, traffic_booth_contacts
    )
    VALUES (
        $1,
        $2, ARRAY(SELECT ST_GeomFromText(u, 4326) FROM unnest($3::text[]) AS u), $4, $5,
        $6, ARRAY(SELECT ST_GeomFromText(u, 4326) FROM unnest($7::text[]) AS u), $8, $9,
        $10, ARRAY(SELECT ST_GeomFromText(u, 4326) FROM unnest($11::text[]) AS u), $12, $13,
        $14, ARRAY(SELECT ST_GeomFromText(u, 4326) FROM unnest($15::text[]) AS u), $16, $17
    )
    ON CONFLICT (h3_index)
    DO UPDATE SET
        police_names = EXCLUDED.police_names,
        police_points = EXCLUDED.police_points,
        police_distances_km = EXCLUDED.police_distances_km,
        police_contacts = EXCLUDED.police_contacts,

        fire_names = EXCLUDED.fire_names,
        fire_points = EXCLUDED.fire_points,
        fire_distances_km = EXCLUDED.fire_distances_km,
        fire_contacts = EXCLUDED.fire_contacts,

        hospital_names = EXCLUDED.hospital_names,
        hospital_points = EXCLUDED.hospital_points,
        hospital_distances_km = EXCLUDED.hospital_distances_km,
        hospital_contacts = EXCLUDED.hospital_contacts,

        traffic_booth_names = EXCLUDED.traffic_booth_names,
        traffic_booth_points = EXCLUDED.traffic_booth_points,
        traffic_booth_distances_km = EXCLUDED.traffic_booth_distances_km,
        traffic_booth_contacts = EXCLUDED.traffic_booth_contacts;
    """.strip()

    return {
        "records": records,
        "query": sql_query,
        "values": sql_tuples
    }