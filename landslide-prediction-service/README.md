## Landslide Prediction Service  
  
**This service contains the main landslide predicting model.**
*It continuosly listens for new rainfall, eartquake,soil moisture updates and makes prediction based on it , syncs the new metrics and probability to db and pushes to other event queues to be further processed by other engines and dashboard/public server.*