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
st.set_page_config(layout="wide")
# css
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Ubuntu:wght@400;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Ubuntu', sans-serif;
    }
    .block-container {
        padding-top: 1rem !important; /* Ensure no padding at the top */
    }
    h1 {
        font-size: 2rem !important;
        margin: 0rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Effect of Uber Subsidy on Bart Ridership")

left_col, right_col = st.columns([1, 1])

with left_col:
    # Parameters Section
    # st.header("Parameters")
    col1, col2 = st.columns(2)
    with col1:
        subsidy = st.slider("Subsidy Amount ($)", 0.0, 8.0, 4.0, step=0.01)
        time_to_money_conversion = st.slider("Time to Money Conversion ($/hour)", 0, 50, 25)
        car_pc = st.slider("Percent of Population who own car (%)", 0.0, 1.0, 1 / 2, step=0.01)
    with col2:
        hour_of_day = st.slider("Hour of Day (5AM-21PM)", 5, 21, 17, step=1)
        safety_cost = st.slider("Safety Cost ($)", 0, 50, 20)
        inconvenience_fee = st.slider("Driving Inconvenience Cost ($)", 0, 100, 30, step=1)
    is_weekday = st.checkbox("Is Weekday?", value=True)

    # Logic
    try:
        neighborhoods = gpd.read_file("Demographics_By_Census_Tract.geojson")
    except FileNotFoundError:
        st.error("GeoJSON file not found.")
    berryessa_station = Point(-121.8746, 37.3684)

    neighborhoods["centroid"] = neighborhoods.geometry.centroid
    neighborhoods["distance_to_berryessa_deg"] = neighborhoods["centroid"].distance(berryessa_station)
    neighborhoods["distance_to_berryessa_miles"] = (
        neighborhoods["distance_to_berryessa_deg"]
        * (latitude_miles_per_degree**2 + longitude_miles_per_degree**2) ** 0.5
    )

    if "POPTOTAL" not in neighborhoods.columns:
        neighborhoods["population"] = 1000 
    else:
        neighborhoods["population"] = neighborhoods.POPTOTAL

    ua = UberAll(time_to_money_conversion, neighborhoods['distance_to_berryessa_miles'])
    ub = UberBartMix(time_to_money_conversion, neighborhoods['distance_to_berryessa_miles'], safety_cost)
    neighborhoods['cost_uber_all'] = ua.get_cost(hour_of_day, is_weekday)
    neighborhoods['cost_bart_uber'] = ub.get_cost() - subsidy
    neighborhoods['cost_bart_uber_no_subsidy'] = ub.get_cost()
    neighborhoods['cost_drive'] = Drive(time_to_money_conversion, inconvenience_fee).get_cost(hour_of_day, is_weekday)

    beta = 0.3
    exp_bart_uber_mix = np.exp(-beta * neighborhoods['cost_bart_uber'])
    exp_bart_uber_no_subsidy = np.exp(-beta * neighborhoods['cost_bart_uber_no_subsidy'])
    exp_uber_all = np.exp(-beta * neighborhoods['cost_uber_all'])
    total_exp_without_car = exp_bart_uber_mix + exp_uber_all
    total_exp_without_car_nosub = exp_bart_uber_no_subsidy + exp_uber_all
    exp_drive = np.exp(-beta * neighborhoods['cost_drive'])
    total_exp_with_car = exp_bart_uber_mix + exp_uber_all + exp_drive
    total_exp_with_car_nosub = exp_bart_uber_no_subsidy + exp_uber_all + exp_drive

    neighborhoods['percent_choosing_bart'] = (exp_bart_uber_mix / total_exp_without_car) * (1 - car_pc) + (exp_bart_uber_mix / total_exp_with_car) * car_pc
    neighborhoods['percent_choosing_bart_no_subsidy'] = (exp_bart_uber_no_subsidy / total_exp_without_car_nosub) * (1 - car_pc) + (exp_bart_uber_no_subsidy / total_exp_with_car_nosub) * car_pc
    total_population = neighborhoods['population'].sum()

    average_percent_with_subsidy = (
        (neighborhoods['percent_choosing_bart'] * neighborhoods['population']).sum()
        / total_population
        * 100
    )
    average_percent_without_subsidy = (
        (neighborhoods['percent_choosing_bart_no_subsidy'] * neighborhoods['population']).sum()
        / total_population
        * 100
    )

    total_rides_no_sub = 30251
    total_rides = 30251 * (
        1 + average_percent_with_subsidy / 100 - average_percent_without_subsidy / 100
    )

    increased_ridership = total_rides - total_rides_no_sub
    increased_revenue = (7.2 - subsidy) * increased_ridership

    # Results Section
    col1, col2 = st.columns(2)
    with col1:
        st.metric("% Choose BART With Subsidy", f"{average_percent_with_subsidy:.2f}%")
        st.metric("Ridership With Subsidy", f"{int(total_rides)}")
        st.metric("Ridership Increased", f"{int(increased_ridership)}")
    with col2:
        st.metric("% Choose BART Without Subsidy", f"{average_percent_without_subsidy:.2f}%")
        st.metric("Ridership Without Subsidy", f"{total_rides_no_sub}")
        st.metric("Revenue Increased", f"${int(increased_revenue)}")

with right_col:
    # st.header("Map")
    m = folium.Map(location=[37.3684, -121.8746], zoom_start=11)
    colormap = cm.LinearColormap(["red", "yellow", "green"], vmin=0, vmax=1)
    colormap.caption = "Percentage Choosing BART with Uber connection ride subsidy"

    neighborhoods['circle_radius'] = neighborhoods['population'] / 10
    for _, row in neighborhoods.iterrows():
        folium.Circle(
            location=[row["centroid"].y, row["centroid"].x],
            radius=row["circle_radius"],
            color=colormap(row["percent_choosing_bart"]),
            fill=True,
            fill_color=colormap(row["percent_choosing_bart"]),
            fill_opacity=0.7,
        ).add_to(m)
    colormap.add_to(m)
    st.markdown("<br><br>", unsafe_allow_html=True)
    st_folium(m, width=500, height=500)
st.write("### Notes")
st.markdown("- Subsidies at $4 per ride during non-rush hours on weekends maximize BART revenue increased. During rush hours, subsidies have a diminished effect since many users already prefer BART due to high traffic congestion.")
st.markdown("- Ridership with no subsidy is based on past 12 months (12/2023 - 11/2024, inclusive) ridership count with origin Berryessa and destination Downtown Berkeley.")
st.markdown("- Costs are converted to probability with the weighted average of two logistic functions of beta = 0.3, one carless (bart vs uber), one with car(bart vs uber vs drive).")
st.markdown("- Revenue increased is calculated with the difference between the percentage of choosing BART with and without subsidy, where without subsidy is the past 12 months ridership count (Berryessa, Downtown Berkeley) * BART fare.")
st.markdown("- Driving Inconvenience Cost includes parking, toll, and misc. cost such as driving in terms of energy.")


st.write("### Debug")
st.dataframe(
    neighborhoods[
        [
            "cost_bart_uber",
            "cost_uber_all",
            "cost_drive",
            "percent_choosing_bart_no_subsidy",
            "percent_choosing_bart",
        ]
    ]
)
