import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import numpy as np

# Constants
time_to_money_conversion = 25
uber_cost_per_mile = 2  # Cost per mile for the connection ride
latitude_miles_per_degree = 69  # Approximation for latitude to miles conversion
longitude_miles_per_degree = 55.2  # Approximation for longitude to miles at ~37 degrees latitude

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
neighborhoods['distance_to_berryessa_miles'] = neighborhoods['distance_to_berryessa_deg'] * np.sqrt(latitude_miles_per_degree**2 + longitude_miles_per_degree**2)

# Set a default population density if it's not present in the dataset
if 'population_density' not in neighborhoods.columns:
    neighborhoods['population_density'] = 1000  # Replace with actual data if available

# Calculate weighted metric: population density * distance to Berryessa in miles
neighborhoods['population_distance_weighted'] = neighborhoods['population_density'] * neighborhoods['distance_to_berryessa_miles']

# Calculate costs for each transport option in miles
neighborhoods['cost_uber_all'] = neighborhoods['distance_to_berryessa_miles'] * uber_cost_per_mile + uber_all.get_cost()
neighborhoods['cost_bart_uber_mix'] = neighborhoods['distance_to_berryessa_miles'] * uber_cost_per_mile + bart_uber_mix.get_cost()

# Estimate the percentage of people choosing bart_uber_mix based on cost difference
neighborhoods['percent_choosing_bart_uber_mix'] = 100 * (neighborhoods['cost_uber_all'] - neighborhoods['cost_bart_uber_mix']) / neighborhoods['cost_uber_all']
neighborhoods['percent_choosing_bart_uber_mix'] = neighborhoods['percent_choosing_bart_uber_mix'].clip(lower=0, upper=100)  # Cap values between 0 and 100%
# Calculate the average percentage choosing BART + Uber mix among San Jose neighborhoods
average_percent_sj_bart = neighborhoods['percent_choosing_bart_uber_mix'].mean()

# Display the result
print("Average percentage of San Jose population choosing BART + Uber mix:", average_percent_sj_bart)

# Plot the neighborhoods with percentage choosing bart_uber_mix
fig, ax = plt.subplots(1, 1, figsize=(12, 8))
neighborhoods.plot(column='percent_choosing_bart_uber_mix', cmap='coolwarm', linewidth=0.8, ax=ax, edgecolor='0.8', legend=True)
ax.set_title("Percentage of Population Choosing BART + Uber Mix Over Uber Only")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
plt.show()
# Filter neighborhoods for San Jose
SJ_neighborhoods = neighborhoods[neighborhoods['city'] == 'San Jose']

