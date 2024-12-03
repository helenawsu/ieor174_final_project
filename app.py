# libraries
import streamlit as st
import geopandas as gpd
from shapely.geometry import Point
import folium
from streamlit_folium import st_folium
import branca.colormap as cm 
import pandas as pd

# class
from utilities import TimePrioritizer, MoneyPrioritizer, SafetyPrioritizer, Population, TransportCost
# constants 
latitude_miles_per_degree = 69  
longitude_miles_per_degree = 55.2

# average incidents by hour
incidents = pd.read_csv("./incidents.csv")
incidents.set_index('Hour', inplace=True)
incidents = incidents.T
incidents_mean = incidents.mean()
scaling_factor = 1 + (incidents_mean - incidents_mean.min()) / (incidents_mean.max() - incidents_mean.min())

# population = Population(1/3,1/3,1/3)
# get the cost of uber all way 
def average_uber_all_cost(population, transportation_cost, time_to_money_conversion):
    tc = transportation_cost
    time_pc = population.time_prioritizer_percentage
    money_pc = population.money_prioritizer_percentage
    safe_pc = population.safety_prioritizer_percentage
    return time_pc * TimePrioritizer(tc).uber_all_cost(time_to_money_conversion) + money_pc * MoneyPrioritizer(tc).uber_all_cost() +  safe_pc * SafetyPrioritizer(tc).uber_all_cost()
# get the cost of uber to bart station, then bart
def average_uber_bart_mix_cost(population, transportation_cost, time_to_money_conversion):
    tc = transportation_cost
    time_pc = population.time_prioritizer_percentage
    money_pc = population.money_prioritizer_percentage
    safe_pc = population.safety_prioritizer_percentage
    return time_pc * TimePrioritizer(tc).uber_bart_mix_cost(time_to_money_conversion) + money_pc * MoneyPrioritizer(tc).uber_bart_mix_cost() +  safe_pc * SafetyPrioritizer(tc).uber_bart_mix_cost()

# map things
neighborhoods = gpd.read_file("Demographics_By_Census_Tract.geojson")
berryessa_station = Point(-121.8746, 37.3684)  # Berryessa coordinates (lon, lat)
neighborhoods['centroid'] = neighborhoods.geometry.centroid
neighborhoods['distance_to_berryessa_deg'] = neighborhoods['centroid'].distance(berryessa_station)
neighborhoods['distance_to_berryessa_miles'] = neighborhoods['distance_to_berryessa_deg'] * (latitude_miles_per_degree**2 + longitude_miles_per_degree**2)**0.5
if 'population_density' not in neighborhoods.columns:
    neighborhoods['population_density'] = 1000  # Replace with actual data if available
st.title("BART Choice Map with Uber connection ride subsidy")

# user adjustable parameters

subsidy = st.slider("Subsidy Amount ($)", 0, 50, 0)
time_to_money_conversion = st.slider("Time to Money Conversion ($/hour)", 10, 50, 25)
uber_cost_per_mile = st.slider("Uber Cost Per Mile ($)", 1, 5, 2)
safety_cost = st.slider("Safety Cost ($)", 10, 50, 20)
st.write("### Adjust Population Percentages")
time_pc = st.slider("Time Prioritizer (%)", 0.0, 1.0, 1 / 3, step=0.01)
money_pc = st.slider("Money Prioritizer (%)", 0.0, 1.0, 1 / 3, step=0.01)
hour_of_day = st.slider("Hour of Day (0-23)", 0, 23, 17, step=1)

# Safety prioritizer is calculated to ensure the sum of percentages in population equals 1
safe_pc = 1.0 - time_pc - money_pc
if safe_pc < 0 or safe_pc > 1:
    st.error("Invalid combination. Adjust Time and Money prioritizers so their sum is ≤ 1.")
    safe_pc = 0
st.write(f"Time Prioritizer: {time_pc:.2f}, Money Prioritizer: {money_pc:.2f}, Safety Prioritizer: {safe_pc:.2f}")

# Population object
population = Population(time_pc, money_pc, safe_pc)

# populate neighborhoods table
time_scaling_factor = scaling_factor[hour_of_day]
neighborhoods['cost_uber_all'] = average_uber_all_cost(Population(time_pc,money_pc,safe_pc), TransportCost(uber_all_time=1.25*time_scaling_factor, uber_bart_mix_time=2*time_scaling_factor, safety_cost=safety_cost, uber_cost_per_mile=uber_cost_per_mile, uber_distance=neighborhoods['distance_to_berryessa_miles']), time_to_money_conversion)
neighborhoods['cost_bart_uber_mix'] = average_uber_bart_mix_cost(Population(time_pc,money_pc,safe_pc), TransportCost(uber_all_time=1.25*time_scaling_factor, uber_bart_mix_time=2*time_scaling_factor, safety_cost=safety_cost, uber_cost_per_mile=uber_cost_per_mile, uber_distance=neighborhoods['distance_to_berryessa_miles']), time_to_money_conversion) - subsidy
neighborhoods['percent_choosing_bart_uber_mix'] = 100 * (neighborhoods['cost_uber_all'] - neighborhoods['cost_bart_uber_mix']) / neighborhoods['cost_uber_all']
neighborhoods['percent_choosing_bart_uber_mix'] = neighborhoods['percent_choosing_bart_uber_mix'].clip(lower=0, upper=100)  # Cap values between 0 and 100%

# streamlit map things
m = folium.Map(location=[37.3684, -121.8746], zoom_start=11)
colormap = cm.LinearColormap(['red', 'yellow', 'green'], vmin=0, vmax=100)
colormap.caption = "Percentage Choosing BART with Uber connection ride subsidy"  # Set a caption for the legend
m = folium.Map(location=[37.3684, -121.8746], zoom_start=11)
for _, row in neighborhoods.iterrows():
    folium.Circle(
        location=[row['centroid'].y, row['centroid'].x],
        radius=500,
        color=colormap(row['percent_choosing_bart_uber_mix']),
        fill=True,
        fill_color=colormap(row['percent_choosing_bart_uber_mix']),
        fill_opacity=0.7
    ).add_to(m)
colormap.add_to(m)

st_folium(m, width=700, height=500)