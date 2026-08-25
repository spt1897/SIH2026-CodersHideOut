## Geo-Static Pre-processor    
  
*This is a preprocessing server that is responsible for the precomputation of the Geo-Spatial indexing, mapping landmarks(cities, road, streets, villages, localities, districts, states) with their respective H3 cells and storing it in the Database.*   
  
*It is also responsible for downloading and updating of static terrain features files(like DEM files, landcover, soiltype,openstreetmaps files etc.) which change very rarely or over years.*  

*It further uses these files to precompute static paramters on which landslide depends on like (elevation, slope, twi,spi, roughness, lithology,soil type, vegetation , building density, road , river density etc.) since such factors remain constant for a huge duration of time.*  

**This server does not run live everytime, but can be thought of as a backend service which runs once a while to update static features since they change after a very very long time.**