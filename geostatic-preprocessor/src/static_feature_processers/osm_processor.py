import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from pyrosm import OSM

def _extract_single_layer(layer_name, custom_filter, pbf_path, output_dir):
    """Worker function to extract a single layer using an isolated OSM instance with correct pyrosm API arguments."""
    try:
        osm = OSM(pbf_path, engine="out_of_core", workers=1)
        
        if layer_name == "roads":
            gdf = osm.get_network(network_type="all")
        else:
            # Fixed: removed unexpected 'keep_columns' argument, using correct 'custom_filter'
            gdf = osm.get_data_by_custom_criteria(custom_filter=custom_filter)
            
        out_path = os.path.join(output_dir, f"{layer_name}.geojson")
        if gdf is not None and not gdf.empty:
            gdf.to_file(out_path, driver="GeoJSON")
            return f"[✓] Saved {len(gdf)} features -> {layer_name}.geojson"
        else:
            return f"[!] No features found for layer: {layer_name}"
    except Exception as e:
        return f"[✗] Skipped layer {layer_name}: {e}"

def extract_pbf_to_geojson():
    """Extracts all infrastructure layers concurrently via ProcessPoolExecutor for maximum speed."""
    pbf_path = r"D:\File-Storage\static_features\openstreet-shapefile\data\north-eastern-zone-latest.osm.pbf"
    output_dir = r"D:\File-Storage\static_features\openstreet-shapefile\data"
    
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(pbf_path):
        print(f"[-] PBF file not found at: {pbf_path}")
        return

    filters = {
        "roads": {"highway": ["motorway", "trunk", "primary", "secondary", "tertiary", "unclassified", "residential", "motorway_link", "trunk_link", "primary_link"]},
        "waterways": {"waterway": ["river", "stream", "canal", "drain"]},
        "railways": {"railway": ["rail", "light_rail", "subway", "narrow_gauge"]},
        "powerlines": {"power": ["line", "minor_line", "cable"]},
        "waterlines": {"man_made": ["pipeline"], "substance": ["water", "sewage", "rainwater"]},
        "oillines": {"man_made": ["pipeline"], "substance": ["oil", "gas", "petrol", "fuel", "crude"]},
        "telecom": {"telecom": ["line"], "communication": ["line"]}
    }

    print(f"[+] Launching parallel multi-process extraction for: {pbf_path}")

    with ProcessPoolExecutor() as executor:
        futures = {
            executor.submit(_extract_single_layer, name, filt, pbf_path, output_dir): name 
            for name, filt in filters.items()
        }
        
        for future in as_completed(futures):
            print(future.result())

if __name__ == "__main__":
    extract_pbf_to_geojson()