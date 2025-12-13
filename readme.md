# FOURSQUARE POI: Custom Country-Specific Basemap

## Introduction

This repository enables the creation of a tailored basemap for a designated country—exemplified here by India—derived from OpenStreetMap (OSM) data. By concentrating exclusively on `place` layers, such as cities, towns, villages, and administrative boundaries, it delivers precise place names strictly aligned with the country's recognized territories. Deliberately omitting features from disputed or contested areas (e.g., border regions) ensures geopolitical neutrality and data integrity, making it a dependable solution for enterprise applications in sectors like logistics, real-time navigation, real estate, and geospatial intelligence—where accuracy and compliance are paramount for industrial-scale operations.

The foundational dataset is the official OSM extract: [india-latest.osm.pbf](https://download.geofabrik.de/asia/india-latest.osm.pbf). Processing yields optimized PMTiles files for the `place` layers, facilitating efficient, high-performance map rendering without extraneous global clutter.

Source: [india-latest.osm.pbf](https://download.geofabrik.de/asia/india-latest.osm.pbf). Output: Lightweight PMTiles for efficient serving.

<img src="docs/Custom Indian Places Basemap.gif"/>


### Setup the Project

Run:
```shell
python setup.py setup
```

### Data Engineering

1. First generated the pmtiles with filtered disputed areas, using this notebook [13_tilemaker_india_pbf.ipynb](notebooks/13_tilemaker_india_pbf.ipynb), Run this on google colab notebook
2. Serve Tiles: Store PMTiles locally and use Flask for HTTP serving.

### Run the application

1. First Activate the virtual env

```shell
vevn/Scripts/Activate
```
2. Then run the flask application
```shell
python run.py
```

### View the map 

Open `india_places.html` in a browser for interactive viewing with the custom basemap. Easily extend for other countries or integrate with Foursquare POI APIs