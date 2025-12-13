# FOURSQUARE POI: Custom Country-Specific Basemap

## Introduction

This repository enables the creation of a tailored basemap for a designated country—exemplified here by India—derived from OpenStreetMap (OSM) data. 

- **Custom Basemap Creation**: Tailors basemaps for specific countries (e.g., India) using OpenStreetMap (OSM) data.
- **Focused Layers**: Targets only `place` elements like cities, towns, villages, and administrative boundaries for precise, territory-aligned place names.
- **Neutrality Filter**: Excludes disputed areas (e.g., border regions) to maintain geopolitical neutrality and data integrity.
- **Enterprise Suitability**: Ideal for industrial applications in logistics, real-time navigation, real estate, and geospatial intelligence, prioritizing accuracy and compliance.

The foundational dataset is the official OSM extract: [india-latest.osm.pbf](https://download.geofabrik.de/asia/india-latest.osm.pbf). Processing yields optimized PMTiles files for the `place` layers, facilitating efficient, high-performance map rendering without extraneous global clutter.

Here is a demo of the pmtile generated: 
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