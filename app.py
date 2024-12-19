# libraries
import streamlit as st
import geopandas as gpd
from shapely.geometry import Point
import folium
from streamlit_folium import st_folium
import branca.colormap as cm 
import pandas as pd
import numpy as np

# class
from utilities import TimePrioritizer, MoneyPrioritizer, SafetyPrioritizer, Population, TransportCost, UberAllCost, UberBartMixCost
# constants 
latitude_miles_per_degree = 69  
longitude_miles_per_degree = 55.2

# css
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 3.5rem !important; /* Ensure no padding at the top */
    }
    .stSlider {
        margin: 0rem; /* Reduce space between sliders */
        padding: 0rem;
    }
    .stVerticalBlock{
    gap: 0rem;
    }
    h1 {
        font-size: 1.75rem;
         margin: 0rem; /* Reduce title size */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# average incidents by hour
try:
    incidents = pd.read_csv("incidents.csv")
except FileNotFoundError:
    st.error("Incidents CSV file not found.")
incidents.set_index('Hour', inplace=True)
incidents = incidents.T
incidents_mean = incidents.mean()
scaling_factor = 1 + (incidents_mean - incidents_mean.min()) / (incidents_mean.max() - incidents_mean.min())

# population = Population(1/3,1/3,1/3)
# get the cost of uber all way 
def average_uber_all_cost(population, uber_all, time_to_money_conversion):
    uber_all = uber_all
    time_pc = population.time_prioritizer_percentage
    money_pc = population.money_prioritizer_percentage
    safe_pc = population.safety_prioritizer_percentage
    return time_pc * TimePrioritizer(uber_all).get_cost(time_to_money_conversion) + money_pc * MoneyPrioritizer(uber_all).get_cost() +  safe_pc * SafetyPrioritizer(uber_all).get_cost() 
# get the cost of uber to bart station, then bart
def average_uber_bart_mix_cost(population, uber_bart_mix, time_to_money_conversion):
    uber_bart_mix = uber_bart_mix
    time_pc = population.time_prioritizer_percentage
    money_pc = population.money_prioritizer_percentage
    safe_pc = population.safety_prioritizer_percentage
    return time_pc * TimePrioritizer(uber_bart_mix).get_cost(time_to_money_conversion) + money_pc * MoneyPrioritizer(uber_bart_mix).get_cost() +  safe_pc * SafetyPrioritizer(uber_bart_mix).get_cost() 

# map things
try:
    neighborhoods = gpd.read_file("Demographics_By_Census_Tract.geojson")
except FileNotFoundError:
    st.error("GeoJSON file not found.")
berryessa_station = Point(-121.8746, 37.3684)  # Berryessa coordinates (lon, lat)
neighborhoods['centroid'] = neighborhoods.geometry.centroid
neighborhoods['distance_to_berryessa_deg'] = neighborhoods['centroid'].distance(berryessa_station)
neighborhoods['distance_to_berryessa_miles'] = neighborhoods['distance_to_berryessa_deg'] * (latitude_miles_per_degree**2 + longitude_miles_per_degree**2)**0.5
if 'population_density' not in neighborhoods.columns:
    neighborhoods['population_density'] = 1000  # Replace with actual data if available
with st.container():
    st.title("BART Choice Map with Uber connection ride subsidy")

    # user adjustable parameters


    # Arrange sliders in multiple columns
    col1, col2 = st.columns(2)
    with col1:
        # keep in mind that the fare from BE to BK is only $7.2, no point going beyond 8
        subsidy = st.slider("Subsidy Amount ($)", 0, 8, 0)
        time_to_money_conversion = st.slider("Time to Money Conversion ($/hour)", 10, 50, 25)
        # uber_cost_per_mile = st.slider("Uber Cost Per Mile ($)", 1, 5, 2)
        time_pc = st.slider("Time Prioritizer (%)", 0.0, 1.0, 1 / 3, step=0.01)

    with col2:
        safety_cost = st.slider("Safety Cost ($)", 10, 50, 20)
        hour_of_day = st.slider("Hour of Day (0-23)", 0, 23, 17, step=1)
        money_pc = st.slider("Money Prioritizer (%)", 0.0, 1.0, 1 / 3, step=0.01)

    # Calculate safety prioritizer percentage
    safe_pc = 1.0 - time_pc - money_pc
    if safe_pc < 0 or safe_pc > 1:
        st.error("Invalid combination. Adjust Time and Money prioritizers so their sum is ≤ 1.")
        safe_pc = 0
    st.write(f"Time Prioritizer: {time_pc:.2f}, Money Prioritizer: {money_pc:.2f}, Safety Prioritizer: {safe_pc:.2f}")

# Streamlit map things (as in your code)
# ...

# example instantiation
# population = Population(time_pc, money_pc, safe_pc)
# uac = UberAllCost(time, distance, traffic_time)
# ubmc = UberBartMixCost(time, safety_cost, distance=0, bart_cost=7.2, traffic_time=0)
# populate neighborhoods table
time_scaling_factor = scaling_factor[hour_of_day]
# did instantiation in line because im not sure whether streamlit would live update slider variables if instantiated prior. should try
neighborhoods['cost_uber_all'] = average_uber_all_cost(Population(time_pc,money_pc,safe_pc), UberAllCost(1.25*scaling_factor[hour_of_day], 43+neighborhoods['distance_to_berryessa_miles'], 0.25*scaling_factor[hour_of_day]), time_to_money_conversion)
# assume no traffic for uber_bart_mix yet, should fix
neighborhoods['cost_bart_uber_mix'] = average_uber_bart_mix_cost(Population(time_pc,money_pc,safe_pc), UberBartMixCost(2, safety_cost, neighborhoods['distance_to_berryessa_miles'], bart_cost=7.2, traffic_time=0), time_to_money_conversion) - subsidy
neighborhoods['cost_bart_uber_mix_baseline'] = neighborhoods['cost_bart_uber_mix'] + subsidy
beta = 0.25 # emperically chosen it produces a reasonable logistic function
exp_bart_uber_mix = np.exp(-beta * neighborhoods['cost_bart_uber_mix'])
exp_uber_all = np.exp(-beta * neighborhoods['cost_uber_all'])
total_exp = exp_bart_uber_mix + exp_uber_all

neighborhoods['percent_choosing_bart_uber_mix'] = exp_bart_uber_mix / total_exp
# neighborhoods['percent_choosing_bart_uber_mix'] = neighborhoods['percent_choosing_bart_uber_mix'].clip(lower=0, upper=100)  # Cap values between 0 and 100%
st.write("### Neighborhood Probabilities")
st.dataframe(neighborhoods[['cost_bart_uber_mix', 'cost_uber_all', 'percent_choosing_bart_uber_mix']])
# streamlit map things
m = folium.Map(location=[37.3684, -121.8746], zoom_start=11)
colormap = cm.LinearColormap(['red', 'yellow', 'green'], vmin=0, vmax=1)
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