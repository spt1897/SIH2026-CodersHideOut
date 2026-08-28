import geopandas as gpd
import pandas as pd
import shapely.geometry
import h3

def cell_landmark_mapper(
    h3_index: str,
    osm_data: dict,
    admin_gdf: gpd.GeoDataFrame  # Custom State/District Boundary Shapefile
) -> dict:
    
    # Convert H3 to Shapely Polygon
    boundary = h3.cell_to_boundary(h3_index)
    cell_poly = shapely.geometry.Polygon([(lon, lat) for lat, lon in boundary])
    cell_area_km2 = h3.cell_area(h3_index, unit='km^2')
    minx, miny, maxx, maxy = cell_poly.bounds

    def spatial_intersect(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        if gdf is None or gdf.empty:
            return gpd.GeoDataFrame()
        possible = gdf.iloc[list(gdf.sindex.intersection((minx, miny, maxx, maxy)))]
        return possible[possible.intersects(cell_poly)]

    # --- 1. ADMINISTRATIVE BOUNDARIES ---
    intersected_admin = spatial_intersect(admin_gdf)
    state_names = list(intersected_admin['state_name'].unique()) if 'state_name' in intersected_admin else []
    district_names = list(intersected_admin['dist_name'].unique()) if 'dist_name' in intersected_admin else []
    sub_districts = list(intersected_admin['sub_dist'].unique()) if 'sub_dist' in intersected_admin else []

    # --- 2. CITIES, TOWNS, VILLAGES (Geofabrik Places) ---
    places_matches = spatial_intersect(osm_data.get('places_point'))
    cities_towns = []
    localities_villages = []
    explicit_place_pop = 0
    
    if not places_matches.empty:
        for _, row in places_matches.iterrows():
            fclass = str(row.get('fclass', '')).lower()
            name = row.get('name')
            
            # Extract explicit population if tagged in OSM places
            pop_val = row.get('population')
            if pd.notna(pop_val) and str(pop_val).isdigit():
                explicit_place_pop += int(pop_val)

            if pd.notna(name):
                if fclass in ['city', 'town']:
                    cities_towns.append(name)
                elif fclass in ['village', 'hamlet', 'suburb', 'locality']:
                    localities_villages.append(name)

    # --- 3. ROADS & DENSITY ---
    road_matches = spatial_intersect(osm_data.get('roads'))
    road_names = list(road_matches['name'].dropna().unique()) if not road_matches.empty else []
    road_len = sum([row.geometry.intersection(cell_poly).length * 111.0 for _, row in road_matches.iterrows()]) if not road_matches.empty else 0.0
    road_density = round(road_len / cell_area_km2, 4)

    # --- 4. RAILWAYS & DENSITY ---
    rail_matches = spatial_intersect(osm_data.get('railways'))
    railway_names = list(rail_matches['name'].dropna().unique()) if not rail_matches.empty else []
    rail_len = sum([row.geometry.intersection(cell_poly).length * 111.0 for _, row in rail_matches.iterrows()]) if not rail_matches.empty else 0.0
    railway_density = round(rail_len / cell_area_km2, 4)

    # --- 5. RIVERS & WATERWAYS ---
    river_matches = spatial_intersect(osm_data.get('waterways'))
    river_names = list(river_matches['name'].dropna().unique()) if not river_matches.empty else []

    # --- 6. FARMLAND & AGRICULTURAL CENTROIDS ---
    landuse_matches = spatial_intersect(osm_data.get('landuse'))
    farmland_polys = []
    if not landuse_matches.empty:
        agri_rows = landuse_matches[landuse_matches['fclass'].isin(['farmland', 'farmyard', 'allotments', 'orchard'])]
        for _, row in agri_rows.iterrows():
            geom = row.geometry.intersection(cell_poly)
            if not geom.is_empty:
                farmland_polys.append(geom)

    is_farmland = len(farmland_polys) > 0
    agri_centroids = shapely.geometry.MultiPoint([p.centroid for p in farmland_polys]).wkt if is_farmland else None

    # --- 7. BUILDING DENSITY & POPULATION DENSITY ESTIMATION ---
    bldg_matches = spatial_intersect(osm_data.get('buildings'))
    num_buildings = len(bldg_matches)
    building_density = round(num_buildings / cell_area_km2, 2)

    # Calculate Population Density (Dual Method Approach)
    estimated_pop = 0
    if explicit_place_pop > 0:
        estimated_pop = explicit_place_pop
    else:
        if not bldg_matches.empty and bldg_matches.geometry.iloc[0].geom_type in ['Polygon', 'MultiPolygon']:
            total_bldg_area_m2 = sum([
                row.geometry.intersection(cell_poly).area * (111000 ** 2) 
                for _, row in bldg_matches.iterrows()
            ])
            estimated_pop = int(total_bldg_area_m2 / 25.0)
        else:
            estimated_pop = int(num_buildings * 4.5)

    population_density = round(estimated_pop / cell_area_km2, 2)

    # --- 8. CRITICAL LIFELINES TRACKING ---
    # Map raw OSM tags to clean human-readable categories
    lifeline_mapping = {
        # Power Infrastructure
        'substation': 'Substation',
        'sub_station': 'Substation',
        'power_station': 'Power Plant',
        'power_plant': 'Power Plant',
        'generator': 'Power Generator',
        'transformer': 'Transformer Unit',
        
        # Healthcare & Emergency
        'hospital': 'Hospital',
        'clinic': 'Clinic',
        'doctors': 'Medical Center',
        'ambulance_station': 'Ambulance Station',
        
        # Water & Fuel Storage
        'water_works': 'Water Treatment Facility',
        'water_tower': 'Water Tower',
        'reservoir': 'Water Reservoir',
        'oil_reservoir': 'Oil / Fuel Reservoir',
        'petroleum_well': 'Oil / Gas Rig',
        'storage_tank': 'Fuel / Utility Storage Tank',
        
        # Telecom & Command
        'communications_tower': 'Telecom Tower',
        'telecom': 'Telecom Station',
        'tower': 'Communication Tower',
        'mast': 'Radio / Telecom Mast'
    }

    critical_lifelines_found = set()

    # Search through relevant OSM layers for matched lifelines
    for layer_name in ['pois', 'buildings', 'landuse', 'power', 'utility']:
        if layer_name in osm_data:
            matches = spatial_intersect(osm_data[layer_name])
            if not matches.empty:
                for col in ['fclass', 'type', 'amenity', 'power', 'building', 'man_made', 'industrial']:
                    if col in matches.columns:
                        tags = matches[col].dropna().astype(str).str.lower().tolist()
                        for tag in tags:
                            if tag in lifeline_mapping:
                                critical_lifelines_found.add(lifeline_mapping[tag])

    critical_lifelines_list = sorted(list(critical_lifelines_found))
    has_critical_power = 1 if len(critical_lifelines_list) > 0 else 0

    # --- 9. LANDMARK NAMES (POIs + Places of Worship + Natural Landmarks) ---
    poi_matches = spatial_intersect(osm_data.get('pois'))
    pofw_matches = spatial_intersect(osm_data.get('pofw'))
    nat_matches = spatial_intersect(osm_data.get('natural'))
    
    landmark_names = set()
    for df in [poi_matches, pofw_matches, nat_matches]:
        if not df.empty and 'name' in df:
            landmark_names.update(df['name'].dropna().tolist())

    return {
        "h3_index": h3_index,
        "state_names": state_names,
        "district_names": district_names,
        "sub_districts": sub_districts,
        "cities_towns": list(set(cities_towns)),
        "localities_villages": list(set(localities_villages)),
        "road_names": road_names,
        "road_density": road_density,
        "railway_names": railway_names,
        "railway_density": railway_density,
        "river_names": river_names,
        "is_farmland": is_farmland,
        "agricultural_centroids": agri_centroids,
        "building_density": building_density,
        "estimated_population": estimated_pop,
        "population_density": population_density,
        "has_critical_power": has_critical_power,
        "critical_lifelines_present": critical_lifelines_list,  # List of identified lifelines
        "landmark_names": list(landmark_names)
    }