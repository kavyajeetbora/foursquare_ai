## FOURSQUARE POI

### Introduction

Generate Custom Basemap for specific country, in this repository we will create for India. All the openstreetmaps is available in this link: [india-latest.osm.pbf](https://download.geofabrik.de/asia/india-latest.osm.pbf). Using this data we will generate the pmtiles for the `place` layers only. Here is the demo of what we will be building:

<img src="docs/Custom Indian Places Basemap.gif"/>


### Setup the Project

Run:
```shell
python setup.py setup
```

### Data Engineering

1. First create the pmtiles, using this notebook [13_tilemaker_india_pbf.ipynb](notebooks/13_tilemaker_india_pbf.ipynb), Run this on google colab notebook
2. Store the exported pmtile file in local, then serve the tiles using the flask application. 

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

open the html page: `india_places.html`