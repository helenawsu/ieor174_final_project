# libraries
import streamlit as st
import geopandas as gpd
from shapely.geometry import Point
import folium
from streamlit_folium import st_folium
import branca.colormap as cm 
import pandas as pd
import numpy as np
import scipy
# class
from utilities import Population, UberAll, UberBartMix, Drive
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
        font-size: 1.75rem !important;
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

# get the cost of uber all way 
def average_uber_all_cost(car_pc, uber_all):
    return uber_all.get_cost(hour_of_day, is_weekday)
# get the cost of uber to bart station, then bart
def average_uber_bart_mix_cost(car_pc, uber_bart):
    return uber_bart.get_cost(hour_of_day, is_weekday)

# map things
try:
    neighborhoods = gpd.read_file("Demographics_By_Census_Tract.geojson")
except FileNotFoundError:
    st.error("GeoJSON file not found.")
berryessa_station = Point(-121.8746, 37.3684)  # Berryessa coordinates (lon, lat)
neighborhoods['centroid'] = neighborhoods.geometry.centroid
neighborhoods['distance_to_berryessa_deg'] = neighborhoods['centroid'].distance(berryessa_station)
neighborhoods['distance_to_berryessa_miles'] = neighborhoods['distance_to_berryessa_deg'] * (latitude_miles_per_degree**2 + longitude_miles_per_degree**2)**0.5
if 'POPDENSITY' not in neighborhoods.columns:
    neighborhoods['population_density'] = 1000  # Replace with actual data if available
else:
    neighborhoods['population_density'] = neighborhoods.POPDENSITY
with st.container():
    st.title("Effect of Uber Subsidy on Bart Ridership")
    col1, col2 = st.columns(2)
    with col1:
        # keep in mind that the fare from BE to BK is only $7.2, no point going beyond 8
        subsidy = st.slider("Subsidy Amount ($)", 0, 8, 0)
        time_to_money_conversion = st.slider("Time to Money Conversion ($/hour)", 0, 50, 25)
        car_pc = st.slider("Percentage of Population who own car (%)", 0.0, 1.0, 1 / 2, step=0.01)

    with col2:
        safety_cost = st.slider("Safety Cost ($)", 0, 50, 20)
        hour_of_day = st.slider("Hour of Day (5AM-21PM)", 5, 21, 17, step=1)
        inconvenience_fee = st.slider("Driving Inconvenience Cost ($)", 0, 100, 20, step=1)
    is_weekday = st.checkbox("Is Weekday?", value=True)
    if hour_of_day in [7, 8, 9, 16, 17, 18]:  # Highlight rush hours
        st.write(f"Selected Hour is Rush Hour 🚦")


time_scaling_factor = scaling_factor[hour_of_day]
# did instantiation in line because im not sure whether streamlit would live update slider variables if instantiated prior. should try
ua = UberAll(time_to_money_conversion, neighborhoods['distance_to_berryessa_miles'])
ub = UberBartMix(time_to_money_conversion, neighborhoods['distance_to_berryessa_miles'], safety_cost)
neighborhoods['cost_uber_all'] = ua.get_cost(hour_of_day, is_weekday)
neighborhoods['cost_bart_uber'] = ub.get_cost() - subsidy
neighborhoods['cost_bart_uber_baseline'] = neighborhoods['cost_bart_uber'] + subsidy
neighborhoods['cost_drive'] = Drive(time_to_money_conversion, inconvenience_fee).get_cost(hour_of_day, is_weekday)

beta = 0.25 # emperically chosen it produces a reasonable logistic function
exp_bart_uber_mix = np.exp(-beta * neighborhoods['cost_bart_uber'])
exp_uber_all = np.exp(-beta * neighborhoods['cost_uber_all'])
# for people without car
total_exp_without_car = exp_bart_uber_mix + exp_uber_all
# for people with car
exp_drive = np.exp(-beta * neighborhoods['cost_drive'])
total_exp_with_car = exp_bart_uber_mix + exp_uber_all + exp_drive
neighborhoods['percent_choosing_bart'] = (exp_bart_uber_mix / total_exp_without_car) 
neighborhoods['percent_choosing_bart'] = (exp_bart_uber_mix / total_exp_without_car) * (1-car_pc) + (exp_bart_uber_mix / total_exp_with_car) * car_pc
# neighborhoods['percent_choosing_bart'] = neighborhoods['percent_choosing_bart'].clip(lower=0, upper=100)  # Cap values between 0 and 100%

# streamlit map things
m = folium.Map(location=[37.3684, -121.8746], zoom_start=11, height="80%")
colormap = cm.LinearColormap(['red', 'yellow', 'green'], vmin=0, vmax=1)
colormap.caption = "Percentage Choosing BART with Uber connection ride subsidy"  # Set a caption for the legend
# Ensure population_density column is used to scale circle size
# Normalize the population size for reasonable circle radii
population_max = neighborhoods['population_density'].max()
neighborhoods['circle_radius'] = neighborhoods['population_density'] / population_max * 2000  # Scale factor for visibility

# Add circles to the map with size proportional to the population
for _, row in neighborhoods.iterrows():
    folium.Circle(
        location=[row['centroid'].y, row['centroid'].x],
        radius=row['circle_radius'],  # Proportional radius
        color=colormap(row['percent_choosing_bart']),
        fill=True,
        fill_color=colormap(row['percent_choosing_bart']),
        fill_opacity=0.7
    ).add_to(m)
colormap.add_to(m)


st_folium(m, width=700, height=500)
st.write("### Neighborhood Probabilities")
st.dataframe(neighborhoods[['cost_bart_uber', 'cost_uber_all', 'cost_drive', 'percent_choosing_bart']])