import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import numpy as np

time_to_money_conversion = 25
uber_cost_per_mile = 2  
latitude_miles_per_degree = 69 
longitude_miles_per_degree = 55.2 
class Transport_Cost:
    def __init__(self, time_cost, monetary_cost, distance_to_bart=None):
        self.time_cost = time_cost
        self.monetary_cost = monetary_cost
        self.dis_to_bart = distance_to_bart

    def get_cost(self):
        return self.monetary_cost + self.time_cost * time_to_money_conversion

uber_all = Transport_Cost(1.25, 80)
bart_uber_mix = Transport_Cost(2, 30)

neighborhoods = gpd.read_file("Demographics_By_Census_Tract.geojson")

berryessa_station = Point(-121.8746, 37.3684)  # Berryessa coordinates (lon, lat)

neighborhoods['centroid'] = neighborhoods.geometry.centroid

neighborhoods['distance_to_berryessa_deg'] = neighborhoods['centroid'].distance(berryessa_station)

neighborhoods['distance_to_berryessa_miles'] = neighborhoods['distance_to_berryessa_deg'] * np.sqrt(latitude_miles_per_degree**2 + longitude_miles_per_degree**2)

if 'population_density' not in neighborhoods.columns:
    neighborhoods['population_density'] = 1000 

neighborhoods['population_distance_weighted'] = neighborhoods['population_density'] * neighborhoods['distance_to_berryessa_miles']

neighborhoods['cost_uber_all'] = neighborhoods['distance_to_berryessa_miles'] * uber_cost_per_mile + uber_all.get_cost()
neighborhoods['cost_bart_uber_mix'] = neighborhoods['distance_to_berryessa_miles'] * uber_cost_per_mile + bart_uber_mix.get_cost()

neighborhoods['percent_choosing_bart_uber_mix'] = 100 * (neighborhoods['cost_uber_all'] - neighborhoods['cost_bart_uber_mix']) / neighborhoods['cost_uber_all']
neighborhoods['percent_choosing_bart_uber_mix'] = neighborhoods['percent_choosing_bart_uber_mix'].clip(lower=0, upper=100) 
average_percent_sj_bart = neighborhoods['percent_choosing_bart_uber_mix'].mean()

print("Average percentage of San Jose population choosing BART + Uber mix:", average_percent_sj_bart)

fig, ax = plt.subplots(1, 1, figsize=(12, 8))
neighborhoods.plot(column='percent_choosing_bart_uber_mix', cmap='coolwarm', linewidth=0.8, ax=ax, edgecolor='0.8', legend=True)
ax.set_title("Percentage of Population Choosing BART + Uber Mix Over Uber Only")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
plt.show()
SJ_neighborhoods = neighborhoods[neighborhoods['city'] == 'San Jose']

