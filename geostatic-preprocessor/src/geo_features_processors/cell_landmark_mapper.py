import h3
import pandas as pd
import geopandas as gpd
import shapely.geometry
from pyproj import Geod

# Geodesic calculator for accurate line length in kilometers (WGS84 ellipsoid)
geod = Geod(ellps="WGS84")

def cell_landmark_mapper(
    h3_index: str,
    osm_data: dict,
    admin_gdf: gpd.GeoDataFrame
) -> dict:
    
    # -------------------------------------------------------------------------
    # 0. H3 GEOMETRY & BOUNDS PREPARATION
    # -------------------------------------------------------------------------
    boundary = h3.cell_to_boundary(h3_index)
    cell_poly = shapely.geometry.Polygon([(lon, lat) for lat, lon in boundary])
    cell_area_km2 = h3.cell_area(h3_index, unit='km^2')
    minx, miny, maxx, maxy = cell_poly.bounds

    # Helper function for rapid spatial intersection
    def spatial_intersect(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        if gdf is None or gdf.empty:
            return gpd.GeoDataFrame()
        # Fast bounding box filtering using spatial index
        possible_idx = list(gdf.sindex.intersection((minx, miny, maxx, maxy)))
        if not possible_idx:
            return gpd.GeoDataFrame()
        possible = gdf.iloc[possible_idx]
        return possible[possible.intersects(cell_poly)]

    # Helper function to extract feature IDs from spatial layers
    # Helper function to extract feature IDs from spatial layers with dynamic column resolution
    def extract_line_ids(gdf_matches: gpd.GeoDataFrame, fallback_col: str = None) -> list:
        if gdf_matches is None or gdf_matches.empty:
            return []
        
        # Priority order for standard OSM feature ID column names
        target_col = None
        for col in ['osm_id', 'id', fallback_col]:
            if col and col in gdf_matches.columns:
                target_col = col
                break

        if not target_col:
            return []

        # Convert to native int types for PostgreSQL BIGINT[] compatibility
        return [int(x) for x in gdf_matches[target_col].dropna().unique().tolist()]
# Helper function to compute exact geodesic intersection length in KM
    def calculate_length_km(gdf_matches: gpd.GeoDataFrame) -> float:
        if gdf_matches.empty:
            return 0.0
        total_len_meters = 0.0
        for _, row in gdf_matches.iterrows():
            clipped_geom = row.geometry.intersection(cell_poly)
            if not clipped_geom.is_empty:
                total_len_meters += geod.geometry_length(clipped_geom)
        return total_len_meters / 1000.0

    # -------------------------------------------------------------------------
    # 1. ADMINISTRATIVE BOUNDARIES
    # -------------------------------------------------------------------------
    intersected_admin = spatial_intersect(admin_gdf)
    state_names = list(intersected_admin['state_name'].dropna().unique()) if 'state_name' in intersected_admin else []
    district_names = list(intersected_admin['dist_name'].dropna().unique()) if 'dist_name' in intersected_admin else []
    sub_districts = list(intersected_admin['sub_dist'].dropna().unique()) if 'sub_dist' in intersected_admin else []

    # -------------------------------------------------------------------------
    # 2. CITIES, TOWNS, VILLAGES (Geofabrik Places)
    # -------------------------------------------------------------------------
    places_matches = spatial_intersect(osm_data.get('places_point'))
    cities_towns = []
    localities_villages = []
    explicit_place_pop = 0

    if not places_matches.empty:
        for _, row in places_matches.iterrows():
            fclass = str(row.get('fclass', '')).lower()
            name = row.get('name')

            pop_val = row.get('population')
            if pd.notna(pop_val) and str(pop_val).isdigit():
                explicit_place_pop += int(pop_val)

            if pd.notna(name):
                if fclass in ['city', 'town']:
                    cities_towns.append(name)
                elif fclass in ['village', 'hamlet', 'suburb', 'locality']:
                    localities_villages.append(name)

    # -------------------------------------------------------------------------
    # 3. INFRASTRUCTURE LINE STRINGS & ID EXTRACTION
    # -------------------------------------------------------------------------

    # A. Roads
    road_matches = spatial_intersect(osm_data.get('roads'))
    road_ids = extract_line_ids(road_matches, 'road_id')
    road_len_km = calculate_length_km(road_matches)
    road_density = round(road_len_km / cell_area_km2, 4)

    # B. Railways
    rail_matches = spatial_intersect(osm_data.get('railways'))
    railway_ids = extract_line_ids(rail_matches, 'railway_id')
    rail_len_km = calculate_length_km(rail_matches)
    railway_density = round(rail_len_km / cell_area_km2, 4)

    # C. Rivers & Hydrography
    river_matches = spatial_intersect(osm_data.get('waterways'))
    river_ids = extract_line_ids(river_matches, 'river_id')

    # D. Power Lines
    power_matches = spatial_intersect(osm_data.get('powerlines'))
    powerline_ids = extract_line_ids(power_matches, 'powerline_id')

    # E. Water Supply Lines
    water_matches = spatial_intersect(osm_data.get('waterlines'))
    waterline_ids = extract_line_ids(water_matches, 'waterline_id')

    # F. Telecom Lines
    telecom_matches = spatial_intersect(osm_data.get('telecom'))
    telecom_ids = extract_line_ids(telecom_matches, 'telecom_id')

    # G. Oil & Gas Pipelines
    oil_matches = spatial_intersect(osm_data.get('oillines'))
    oilline_ids = extract_line_ids(oil_matches, 'oilline_id')

    # -------------------------------------------------------------------------
    # 4. FARMLAND & AGRICULTURAL CENTROIDS
    # -------------------------------------------------------------------------
    landuse_matches = spatial_intersect(osm_data.get('landuse'))
    farmland_polys = []
    if not landuse_matches.empty and 'fclass' in landuse_matches.columns:
        agri_rows = landuse_matches[landuse_matches['fclass'].isin(['farmland', 'farmyard', 'allotments', 'orchard'])]
        for _, row in agri_rows.iterrows():
            geom = row.geometry.intersection(cell_poly)
            if not geom.is_empty:
                farmland_polys.append(geom)

    is_farmland = len(farmland_polys) > 0
    agricultural_centroids = shapely.geometry.MultiPoint([p.centroid for p in farmland_polys]).wkt if is_farmland else None

    # -------------------------------------------------------------------------
    # 5. DENSITY & POPULATION ESTIMATION
    # -------------------------------------------------------------------------
    bldg_matches = spatial_intersect(osm_data.get('buildings'))
    num_buildings = len(bldg_matches)
    building_density = round(num_buildings / cell_area_km2, 2)

    estimated_pop = 0
    if explicit_place_pop > 0:
        estimated_pop = explicit_place_pop
    else:
        if not bldg_matches.empty and bldg_matches.geometry.iloc[0].geom_type in ['Polygon', 'MultiPolygon']:
            # Calculate total footprint area in m² using geodesic projection
            total_bldg_area_m2 = sum([
                geod.geometry_area_perimeter(row.geometry.intersection(cell_poly))[0]
                for _, row in bldg_matches.iterrows()
            ])
            estimated_pop = int(abs(total_bldg_area_m2) / 25.0)
        else:
            estimated_pop = int(num_buildings * 4.5)

    population_density = round(estimated_pop / cell_area_km2, 2)

    # -------------------------------------------------------------------------
    # 6. LANDMARK NAMES (POIs + Places of Worship + Natural Landmarks)
    # -------------------------------------------------------------------------
    poi_matches = spatial_intersect(osm_data.get('pois'))
    pofw_matches = spatial_intersect(osm_data.get('pofw'))
    nat_matches = spatial_intersect(osm_data.get('natural'))

    landmark_names = set()
    for df in [poi_matches, pofw_matches, nat_matches]:
        if not df.empty and 'name' in df.columns:
            landmark_names.update(df['name'].dropna().tolist())

    # -------------------------------------------------------------------------
    # 7. FINAL RETURN OBJECT MATCHING POSTGIS TABLE COLUMNS
    # -------------------------------------------------------------------------
    return {
        "h3_index": h3_index,
        
        # Administrative Arrays
        "state_names": list(set(state_names)),
        "district_names": list(set(district_names)),
        "sub_districts": list(set(sub_districts)),
        "cities_towns": list(set(cities_towns)),
        "localities_villages": list(set(localities_villages)),
        
        # Infrastructure ID Arrays
        "road_ids": road_ids,
        "railway_ids": railway_ids,
        "river_ids": river_ids,
        "powerline_ids": powerline_ids,
        "waterline_ids": waterline_ids,
        "telecom_ids": telecom_ids,
        "oilline_ids": oilline_ids,
        
        # Metrics & Land Use
        "is_farmland": is_farmland,
        "agricultural_centroids": agricultural_centroids,  # WKT representation
        "population_density": population_density,
        "estimated_population": estimated_pop,
        "building_density": building_density,
        "road_density": road_density,
        "railway_density": railway_density,
        "landmark_names": sorted(list(landmark_names))
    }