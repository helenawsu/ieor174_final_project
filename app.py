import streamlit as st
import geopandas as gpd
from shapely.geometry import Point
import folium
from streamlit_folium import st_folium
import branca.colormap as cm  # For color map

# Constants
time_to_money_conversion = 25
uber_cost_per_mile = 2  # Assume shorter distance, around 15 miles for connection rides
latitude_miles_per_degree = 69  # Approximate for latitude
longitude_miles_per_degree = 55.2  # Approximate for longitude at ~37 degrees latitude

# Transport Cost class
class Transport_Cost:
    def __init__(self, time_cost, monetary_cost, distance_to_bart=None):
        self.time_cost = time_cost
        self.monetary_cost = monetary_cost
        self.dis_to_bart = distance_to_bart

    def get_cost(self):
        return self.monetary_cost + self.time_cost * time_to_money_conversion

# Define transport options
uber_all = Transport_Cost(1.25, 80)
bart_uber_mix = Transport_Cost(2, 30)

# Load neighborhoods data
neighborhoods = gpd.read_file("Demographics_By_Census_Tract.geojson")

# Berryessa Station location
berryessa_station = Point(-121.8746, 37.3684)  # Berryessa coordinates (lon, lat)

# Calculate centroids of each neighborhood
neighborhoods['centroid'] = neighborhoods.geometry.centroid

# Calculate distance from each neighborhood centroid to Berryessa Station in degrees
neighborhoods['distance_to_berryessa_deg'] = neighborhoods['centroid'].distance(berryessa_station)

# Convert distance to miles
neighborhoods['distance_to_berryessa_miles'] = neighborhoods['distance_to_berryessa_deg'] * (latitude_miles_per_degree**2 + longitude_miles_per_degree**2)**0.5

# Set a default population density if it's not present in the dataset
if 'population_density' not in neighborhoods.columns:
    neighborhoods['population_density'] = 1000  # Replace with actual data if available

# Interactive Subsidy Slider
st.title("BART Choice Map with Uber connection ride subsidy")
subsidy = st.slider("Subsidy Amount ($)", 0, 50, 0)

# Adjust cost based on subsidy
neighborhoods['cost_uber_all'] = neighborhoods['distance_to_berryessa_miles'] * uber_cost_per_mile + uber_all.get_cost()
neighborhoods['cost_bart_uber_mix'] = neighborhoods['distance_to_berryessa_miles'] * uber_cost_per_mile + bart_uber_mix.get_cost() - subsidy

# Calculate the percentage of people choosing bart_uber_mix based on subsidy
neighborhoods['percent_choosing_bart_uber_mix'] = 100 * (neighborhoods['cost_uber_all'] - neighborhoods['cost_bart_uber_mix']) / neighborhoods['cost_uber_all']
neighborhoods['percent_choosing_bart_uber_mix'] = neighborhoods['percent_choosing_bart_uber_mix'].clip(lower=0, upper=100)  # Cap values between 0 and 100%

# Define a color map for the percentage values

# Plot map
m = folium.Map(location=[37.3684, -121.8746], zoom_start=11)

# Define a color map for the percentage values from red to green
colormap = cm.LinearColormap(['red', 'yellow', 'green'], vmin=0, vmax=100)
colormap.caption = "Percentage Choosing BART with Uber connection ride subsidy"  # Set a caption for the legend

# Plot map
m = folium.Map(location=[37.3684, -121.8746], zoom_start=11)

# Add neighborhoods with updated percentage colors
for _, row in neighborhoods.iterrows():
    folium.Circle(
        location=[row['centroid'].y, row['centroid'].x],
        radius=500,
        color=colormap(row['percent_choosing_bart_uber_mix']),
        fill=True,
        fill_color=colormap(row['percent_choosing_bart_uber_mix']),
        fill_opacity=0.7
    ).add_to(m)

# Add the color map (legend) to the map
colormap.add_to(m)

# Display map in Streamlit
st_folium(m, width=700, height=500)