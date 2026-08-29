import os
import h3
import pandas as pd
import geopandas as gpd
import shapely.geometry
from pyproj import Geod
from typing import Tuple, Dict, Any

from src.static_features_extractors.raster_file_config import (
    VECTOR_PATHS,
    BASE_DIR
)

geod = Geod(ellps="WGS84")

def cell_landmark_mapper(
    bbox: Tuple[float, float, float, float],
    h3_resolution: int
) -> Dict[str, Any]:
    min_lat, min_lon, max_lat, max_lon = bbox
    bbox_tuple = (min_lon, min_lat, max_lon, max_lat)

    osm_shape_dir = os.path.join(BASE_DIR, "openstreet-shapefile", "data")

    layer_files = {
        "places": "gis_osm_places_free_1.shp",
        "places_a": "gis_osm_places_a_free_1.shp",
        "roads": "gis_osm_roads_free_1.shp",
        "railways": "gis_osm_railways_free_1.shp",
        "landuse": "gis_osm_landuse_a_free_1.shp",
        "buildings": "gis_osm_buildings_a_free_1.shp",
        "pois": "gis_osm_pois_free_1.shp",
        "pofw": "gis_osm_pofw_free_1.shp",
        "natural": "gis_osm_natural_free_1.shp",
        "waterways": "gis_osm_waterways_free_1.shp",
        "powerlines": "powerlines.geojson",
        "waterlines": "waterlines.geojson",
        "telecom": "telecom.geojson",
        "oillines": "oillines.geojson",
        "admin": "gis_osm_adminareas_a_free_1.shp",
        "states": "india_states.shp"
    }

    osm_data = {}

    for layer, default_filename in layer_files.items():
        path = VECTOR_PATHS.get(layer, os.path.join(osm_shape_dir, default_filename))
        print(f"[PATH] {layer}: {path}")

        if not os.path.exists(path):
            print(f"[-] Missing {layer}: {path}")
            osm_data[layer] = gpd.GeoDataFrame()
            continue

        try:
            print(f"[+] Loading {layer}")
            if layer == "states":
                gdf = gpd.read_file(path)
            else:
                gdf = gpd.read_file(path, bbox=bbox_tuple)

            if not gdf.empty:
                if gdf.crs is None:
                    gdf = gdf.set_crs(epsg=4326)
                elif gdf.crs.to_epsg() != 4326:
                    gdf = gdf.to_crs(epsg=4326)

                try:
                    gdf["geometry"] = gdf.geometry.make_valid()
                except Exception:
                    gdf["geometry"] = gdf.geometry.buffer(0)

            osm_data[layer] = gdf
            print(f"    {layer}: {len(gdf)} features")

        except Exception as e:
            print(f"[-] Error loading {layer} from {path}: {e}")
            osm_data[layer] = gpd.GeoDataFrame()

    admin_gdf = osm_data["admin"]
    state_gdf = osm_data["states"]
    places_a_gdf = osm_data["places_a"]
    places_gdf = osm_data["places"]

    # ========================================================
    # DYNAMIC CITY/TOWN BOUNDARY POLYGON EXTRACTION
    # Cross-reference city point names against administrative polygons
    # ========================================================
    city_polys_list = []

    # 1. Collect all explicit city & town point names from places_gdf
    city_town_names = set()
    if not places_gdf.empty:
        type_col = next((c for c in ["fclass", "place", "type"] if c in places_gdf.columns), None)
        name_col = next((c for c in ["name", "NAME", "place_name"] if c in places_gdf.columns), None)
        if type_col and name_col:
            city_nodes = places_gdf[places_gdf[type_col].astype(str).str.lower().isin(["city", "town"])]
            city_town_names = set(city_nodes[name_col].dropna().astype(str).str.strip().tolist())

    # 2. Extract city/town polygon boundaries from places_a_gdf
    if not places_a_gdf.empty:
        type_col = next((c for c in ["fclass", "place", "type"] if c in places_a_gdf.columns), None)
        name_col = next((c for c in ["name", "NAME", "place_name"] if c in places_a_gdf.columns), None)
        if type_col and name_col:
            poly_matches = places_a_gdf[
                places_a_gdf[type_col].astype(str).str.lower().isin(["city", "town", "capital", "municipality", "borough"])
            ].copy()
            if not poly_matches.empty:
                poly_matches["city_name"] = poly_matches[name_col].astype(str).str.strip()
                city_polys_list.append(poly_matches[["city_name", "geometry"]])

    # 3. Extract exact administrative polygons matching city names or municipal levels
    if not admin_gdf.empty:
        for _, row in admin_gdf.iterrows():
            name = row.get("name")
            if pd.isna(name):
                continue
            name_str = str(name).strip()
            if not name_str:
                continue

            fclass = str(row.get("fclass", "")).strip().lower()
            admin_level = str(row.get("admin_level", "")).strip()

            is_city_level = (fclass in {"admin_level7", "admin_level8"} or admin_level in {"7", "8"})
            
            # Match polygon name against known city/town node names (e.g., "Guwahati", "Guwahati Circle")
            matched_city_name = None
            for c_name in city_town_names:
                if c_name.lower() in name_str.lower():
                    matched_city_name = c_name
                    break

            if is_city_level or matched_city_name:
                final_name = matched_city_name if matched_city_name else name_str
                single_gdf = gpd.GeoDataFrame([{"city_name": final_name, "geometry": row.geometry}], crs=admin_gdf.crs)
                city_polys_list.append(single_gdf)

    if city_polys_list:
        city_boundaries_gdf = pd.concat(city_polys_list, ignore_index=True)
        city_boundaries_gdf = gpd.GeoDataFrame(city_boundaries_gdf, crs=admin_gdf.crs if not admin_gdf.empty else "EPSG:4326")
    else:
        city_boundaries_gdf = gpd.GeoDataFrame(columns=["city_name", "geometry"], crs="EPSG:4326")

    poly = h3.LatLngPoly(
        [
            (min_lat, min_lon),
            (min_lat, max_lon),
            (max_lat, max_lon),
            (max_lat, min_lon),
            (min_lat, min_lon)
        ]
    )

    h3_cells = list(h3.polygon_to_cells(poly, res=h3_resolution))
    print(f"\n[+] Generated {len(h3_cells)} H3 cells")

    records = []

    for cell_number, h3_index in enumerate(h3_cells, start=1):
        boundary = h3.cell_to_boundary(h3_index)
        cell_poly = shapely.geometry.Polygon([(lon, lat) for lat, lon in boundary])
        cell_area_km2 = h3.cell_area(h3_index, unit="km^2")
        minx, miny, maxx, maxy = cell_poly.bounds

        def spatial_intersect(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
            if gdf is None or gdf.empty:
                return gpd.GeoDataFrame()
            try:
                possible_idx = list(gdf.sindex.intersection((minx, miny, maxx, maxy)))
                if not possible_idx:
                    return gpd.GeoDataFrame()
                possible = gdf.iloc[possible_idx]
                return possible[possible.geometry.intersects(cell_poly)]
            except Exception:
                valid_indices = []
                for idx, row in gdf.iterrows():
                    try:
                        if row.geometry.buffer(0).intersects(cell_poly):
                            valid_indices.append(idx)
                    except Exception:
                        continue
                return gdf.loc[valid_indices] if valid_indices else gpd.GeoDataFrame()

        def extract_line_ids(gdf_matches: gpd.GeoDataFrame, fallback_col: str = None) -> list:
            if gdf_matches is None or gdf_matches.empty:
                return []
            columns_lower = {col.lower(): col for col in gdf_matches.columns}
            target_col = None
            for candidate in ["osm_id", "id", fallback_col]:
                if candidate and candidate.lower() in columns_lower:
                    target_col = columns_lower[candidate.lower()]
                    break

            if not target_col:
                for col_lower, actual_col in columns_lower.items():
                    if "id" in col_lower:
                        target_col = actual_col
                        break

            if not target_col:
                return []

            result = []
            for value in gdf_matches[target_col].dropna().unique().tolist():
                try:
                    result.append(int(value))
                except (ValueError, TypeError):
                    continue
            return result

        def calculate_length_km(gdf_matches: gpd.GeoDataFrame) -> float:
            if gdf_matches is None or gdf_matches.empty:
                return 0.0
            total_len_meters = 0.0
            for _, row in gdf_matches.iterrows():
                try:
                    clipped_geom = row.geometry.intersection(cell_poly)
                    if not clipped_geom.is_empty:
                        total_len_meters += geod.geometry_length(clipped_geom)
                except Exception:
                    continue
            return total_len_meters / 1000.0

        # ========================================================
        # ADMINISTRATIVE (State, District, Sub-district, Cities)
        # ========================================================
        state_names = []
        district_names = []
        sub_districts = []
        cities_towns = []
        localities_villages = []

        # 1. State Shapefile Check
        state_matches = spatial_intersect(state_gdf)
        if not state_matches.empty:
            for col in ["name", "NAME", "state", "STATE", "st_nm", "stname"]:
                if col in state_matches.columns:
                    state_names.extend(
                        state_matches[col].dropna().astype(str).str.strip().tolist()
                    )
                    break

        # 2. Primary Administrative Polygons (State, District, Sub-district)
        admin_matches = spatial_intersect(admin_gdf)
        if not admin_matches.empty:
            for _, row in admin_matches.iterrows():
                name = row.get("name")
                if pd.isna(name):
                    continue
                name = str(name).strip()
                if not name:
                    continue

                fclass = str(row.get("fclass", "")).strip().lower()
                admin_level = str(row.get("admin_level", "")).strip()

                if fclass == "admin_level4" or admin_level == "4":
                    state_names.append(name)
                elif fclass == "admin_level5" or admin_level == "5":
                    district_names.append(name)
                elif fclass == "admin_level6" or admin_level == "6":
                    sub_districts.append(name)

        # 3. Dynamic Boundary Polygons Intersections (Cities & Towns)
        city_bnd_matches = spatial_intersect(city_boundaries_gdf)
        if not city_bnd_matches.empty:
            cities_towns.extend(
                city_bnd_matches["city_name"].dropna().astype(str).str.strip().tolist()
            )

        # 4. Point Places Intersections (Direct cell hits & village/locality categorization)
        places_matches = spatial_intersect(places_gdf)
        explicit_place_pop = 0

        if not places_matches.empty:
            type_col = next((c for c in ["fclass", "place", "type"] if c in places_matches.columns), None)
            name_col = next((c for c in ["name", "NAME", "place_name"] if c in places_matches.columns), None)

            for _, row in places_matches.iterrows():
                if not name_col or pd.isna(row.get(name_col)):
                    continue
                name = str(row.get(name_col)).strip()
                if not name:
                    continue

                fclass = str(row.get(type_col, "")).strip().lower() if type_col else ""
                pop_val = row.get("population")

                if pd.notna(pop_val):
                    try:
                        explicit_place_pop += int(float(pop_val))
                    except (ValueError, TypeError):
                        pass

                if fclass in {"city", "town"}:
                    cities_towns.append(name)
                elif fclass in {"village", "hamlet", "suburb", "locality", "isolated_dwelling", "neighbourhood"}:
                    localities_villages.append(name)

        # Deduplicate names
        state_names = sorted(set(state_names))
        district_names = sorted(set(district_names))
        sub_districts = sorted(set(sub_districts))
        cities_towns = sorted(set(cities_towns))
        localities_villages = sorted(set(localities_villages))

        # ========================================================
        # ROADS & RAILWAYS
        # ========================================================
        road_matches = spatial_intersect(osm_data["roads"])
        road_density = round(calculate_length_km(road_matches) / cell_area_km2, 4)

        rail_matches = spatial_intersect(osm_data["railways"])
        railway_density = round(calculate_length_km(rail_matches) / cell_area_km2, 4)

        # ========================================================
        # LANDUSE
        # ========================================================
        landuse_matches = spatial_intersect(osm_data["landuse"])
        farmland_polys = []

        if not landuse_matches.empty and "fclass" in landuse_matches.columns:
            agri_rows = landuse_matches[
                landuse_matches["fclass"].astype(str).str.lower().isin(
                    ["farmland", "farmyard", "allotments", "orchard"]
                )
            ]
            for _, row in agri_rows.iterrows():
                try:
                    geom = row.geometry.intersection(cell_poly)
                    if not geom.is_empty:
                        farmland_polys.append(geom)
                except Exception:
                    continue

        is_farmland = len(farmland_polys) > 0
        agricultural_centroids = (
            shapely.geometry.MultiPoint([p.centroid for p in farmland_polys if not p.is_empty]).wkt
            if is_farmland else None
        )

        # ========================================================
        # BUILDINGS & POPULATION ESTIMATION
        # ========================================================
        bldg_matches = spatial_intersect(osm_data["buildings"])
        building_density = round(len(bldg_matches) / cell_area_km2, 2)
        estimated_pop = explicit_place_pop

        if estimated_pop == 0:
            if not bldg_matches.empty:
                first_geom = bldg_matches.geometry.iloc[0]
                if first_geom.geom_type in ["Polygon", "MultiPolygon"]:
                    total_bldg_area_m2 = 0.0
                    for _, row in bldg_matches.iterrows():
                        try:
                            clipped = row.geometry.intersection(cell_poly)
                            if not clipped.is_empty:
                                area, _ = geod.geometry_area_perimeter(clipped)
                                total_bldg_area_m2 += abs(area)
                        except Exception:
                            continue
                    estimated_pop = int(total_bldg_area_m2 / 25.0)
                else:
                    estimated_pop = int(len(bldg_matches) * 4.5)
            else:
                estimated_pop = 0

        # ========================================================
        # LANDMARKS
        # ========================================================
        landmark_names = set()
        for layer in ["pois", "pofw", "natural"]:
            df = spatial_intersect(osm_data[layer])
            if not df.empty and "name" in df.columns:
                landmark_names.update(df["name"].dropna().astype(str).str.strip().tolist())

        # ========================================================
        # INFRASTRUCTURE LINE IDS
        # ========================================================
        river_matches = spatial_intersect(osm_data["waterways"])
        powerline_matches = spatial_intersect(osm_data["powerlines"])
        waterline_matches = spatial_intersect(osm_data["waterlines"])
        telecom_matches = spatial_intersect(osm_data["telecom"])
        oilline_matches = spatial_intersect(osm_data["oillines"])

        records.append({
            "h3_index": h3_index,
            "state_names": state_names,
            "district_names": district_names,
            "sub_districts": sub_districts,
            "cities_towns": cities_towns,
            "localities_villages": localities_villages,
            "road_ids": extract_line_ids(road_matches, "road_id"),
            "railway_ids": extract_line_ids(rail_matches, "railway_id"),
            "river_ids": extract_line_ids(river_matches, "river_id"),
            "powerline_ids": extract_line_ids(powerline_matches, "powerline_id"),
            "waterline_ids": extract_line_ids(waterline_matches, "waterline_id"),
            "telecom_ids": extract_line_ids(telecom_matches, "telecom_id"),
            "oilline_ids": extract_line_ids(oilline_matches, "oilline_id"),
            "is_farmland": is_farmland,
            "agricultural_centroids": agricultural_centroids,
            "population_density": round(estimated_pop / cell_area_km2, 2),
            "estimated_population": estimated_pop,
            "building_density": building_density,
            "road_density": road_density,
            "railway_density": railway_density,
            "landmark_names": sorted(list(landmark_names))
        })

        if cell_number % 1000 == 0 or cell_number == len(h3_cells):
            print(f"[+] Processed {cell_number}/{len(h3_cells)} cells")

    sql_tuples = [
        (
            r["h3_index"], r["state_names"], r["district_names"], r["sub_districts"],
            r["cities_towns"], r["localities_villages"], r["road_ids"],
            r["railway_ids"], r["river_ids"], r["powerline_ids"],
            r["waterline_ids"], r["telecom_ids"], r["oilline_ids"],
            r["is_farmland"], r["agricultural_centroids"], float(r["population_density"]),
            int(r["estimated_population"]), float(r["building_density"]),
            float(r["road_density"]), float(r["railway_density"]), r["landmark_names"]
        )
        for r in records
    ]

    sql_query = """
        INSERT INTO cell_landmark_mapping (
            h3_index, state_names, district_names, sub_districts,
            cities_towns, localities_villages, road_ids, railway_ids,
            river_ids, powerline_ids, waterline_ids, telecom_ids,
            oilline_ids, is_farmland, agricultural_centroids,
            population_density, estimated_population, building_density,
            road_density, railway_density, landmark_names
        )
        VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14,
            CASE
                WHEN $15::text IS NULL THEN NULL
                ELSE ST_GeomFromText($15, 4326)
            END,
            $16, $17, $18, $19, $20, $21
        )
        ON CONFLICT (h3_index) DO UPDATE SET
            state_names = EXCLUDED.state_names,
            district_names = EXCLUDED.district_names,
            sub_districts = EXCLUDED.sub_districts,
            cities_towns = EXCLUDED.cities_towns,
            localities_villages = EXCLUDED.localities_villages,
            road_ids = EXCLUDED.road_ids,
            railway_ids = EXCLUDED.railway_ids,
            river_ids = EXCLUDED.river_ids,
            powerline_ids = EXCLUDED.powerline_ids,
            waterline_ids = EXCLUDED.waterline_ids,
            telecom_ids = EXCLUDED.telecom_ids,
            oilline_ids = EXCLUDED.oilline_ids,
            is_farmland = EXCLUDED.is_farmland,
            agricultural_centroids = EXCLUDED.agricultural_centroids,
            population_density = EXCLUDED.population_density,
            estimated_population = EXCLUDED.estimated_population,
            building_density = EXCLUDED.building_density,
            road_density = EXCLUDED.road_density,
            railway_density = EXCLUDED.railway_density,
            landmark_names = EXCLUDED.landmark_names;
    """.strip()

    return {
        "records": records,
        "query": sql_query,
        "values": sql_tuples
    }