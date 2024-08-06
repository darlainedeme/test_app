import streamlit as st
import ee
import json
import requests
import geopandas as gpd
import geemap.foliumap as geemap
from datetime import datetime

# Initialize Earth Engine
@st.cache_resource
def initialize_earth_engine():
    json_data = st.secrets["json_data"]
    
    if json_data is None:
        raise ValueError("json_data is None")
    
    json_data_dict = dict(json_data)
    json_data_str = json.dumps(json_data_dict)
    
    if not isinstance(json_data_str, str):
        raise TypeError(f"json_data must be str, but got {type(json_data_str)}")
    
    print(f"json_data_str type: {type(json_data_str)}")
    print(f"json_data_str content: {json_data_str[:100]}...")
    
    json_object = json.loads(json_data_str, strict=False)
    service_account = json_object['client_email']
    
    credentials = ee.ServiceAccountCredentials(service_account, key_data=json_data_str)
    ee.Initialize(credentials)

initialize_earth_engine()

# Load study area from GeoJSON file
@st.cache_resource
def load_study_area():
    gdf = gpd.read_file('study_area.geojson')
    return geemap.geopandas_to_ee(gdf)

aoi = load_study_area()

# Date for data retrieval
date = '2021-01-01'
date2 = '2021-01-02'

# Filter Image for desired date
collectionModEvi_terra = ee.ImageCollection('MODIS/006/MOD13Q1').filterDate(date, date2) \
    .filterBounds(aoi)\
    .select('EVI')

collectionModEvi_aqua = ee.ImageCollection('MODIS/061/MYD13Q1').filterDate(date, date2) \
    .filterBounds(aoi)\
    .select('EVI')

collectionModEvi = collectionModEvi_terra.merge(collectionModEvi_aqua)

# Visualize the data
st.title("MODIS EVI Data Visualization")
st.write(f"Displaying MODIS EVI data for {date}")

map_ = geemap.Map()
map_.addLayer(aoi, {}, "Study Area")

# Add each image in the collection to the map
for image in collectionModEvi.toList(collectionModEvi.size()).getInfo():
    img = ee.Image(image['id'])
    map_.addLayer(img, {"min": 0, "max": 8000, "palette": ['red', 'yellow', 'green']}, image['id'])

map_.to_streamlit()
