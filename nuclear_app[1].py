"""
Name: Khoa Pham
CS230: Section 4
Data:  Nuclear Explosions 1945–1998
URL: [Add your Streamlit Cloud URL if published]

Description:
This interactive Streamlit application explores the nuclear explosions dataset from 1945–1998.
Users can filter by country and year range, analyze explosion magnitude and depth trends, and
view an interactive map of test sites.
"""

import streamlit as st
import pandas as pd
import pydeck as pdk
import matplotlib.pyplot as plt
import seaborn as sns

# [DA1] Data cleaning and loading
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("nuclear_explosions.csv")
        df = df.dropna(subset=["Latitude", "Longitude", "Date", "Country", "Magnitude", "Depth"])
        df["Year"] = pd.to_datetime(df["Date"]).dt.year
        df["Location"] = df["Region"] + ", " + df["Country"]
        return df
    except Exception as err:
        st.error(f"Error loading data: {err}")
        return pd.DataFrame()

data = load_data()

# Sidebar filters
st.sidebar.title("Filters")
countries = st.sidebar.multiselect("Select countries:", options=data["Country"].unique(), default=["USA", "USSR"])
year_range = st.sidebar.slider("Select year range:", int(data["Year"].min()), int(data["Year"].max()), (1960, 1980))

# [DA4] + [DA5] Filtered data
filtered_data = data[(data["Country"].isin(countries)) & (data["Year"].between(year_range[0], year_range[1]))]

st.title("Nuclear Explosions Explorer")
st.write(f"Filtered dataset has **{filtered_data.shape[0]}** explosions from {year_range[0]} to {year_range[1]}.")

# [CHART1] Magnitude over time
st.subheader("Magnitude of Explosions Over Time")
fig1, ax1 = plt.subplots()
for country in countries:
    sub_data = filtered_data[filtered_data["Country"] == country]
    ax1.plot(sub_data["Year"], sub_data["Magnitude"], label=country, marker='o')
ax1.set_xlabel("Year")
ax1.set_ylabel("Magnitude")
ax1.set_title("Explosion Magnitude by Year")
ax1.legend()
st.pyplot(fig1)

# [CHART2] Depth distribution (Seaborn)
st.subheader("Depth Distribution")
fig2, ax2 = plt.subplots()
sns.histplot(data=filtered_data, x="Depth", hue="Country", kde=True, ax=ax2)
ax2.set_title("Explosion Depth Distribution")
st.pyplot(fig2)

# [MAP] PyDeck Map
st.subheader("Map of Nuclear Explosion Sites")
st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state=pdk.ViewState(
        latitude=filtered_data["Latitude"].mean(),
        longitude=filtered_data["Longitude"].mean(),
        zoom=2,
        pitch=0,
    ),
    layers=[
        pdk.Layer(
            "ScatterplotLayer",
            data=filtered_data,
            get_position='[Longitude, Latitude]',
            get_color='[200, 30, 0, 160]',
            get_radius=50000,
            pickable=True,
        )
    ],
    tooltip={"text": "{Country}\n{Location}\nMagnitude: {Magnitude}\nDepth: {Depth}"}
))

# [DA2] + [DA3] Top 5 largest explosions
st.subheader("Top 5 Largest Explosions")
top_magnitude = filtered_data.nlargest(5, "Magnitude")[["Country", "Region", "Year", "Magnitude", "Depth"]]
st.dataframe(top_magnitude)

# [DA6] Pivot Table: Avg Magnitude by Country and Year
st.subheader("Average Magnitude by Country and Year")
pivot = filtered_data.pivot_table(values="Magnitude", index="Year", columns="Country", aggfunc="mean")
st.dataframe(pivot)

# [PY1] Function with default
def explosion_summary(df, show_depth=True):
    avg_mag = df["Magnitude"].mean()
    if show_depth:
        avg_depth = df["Depth"].mean()
        return avg_mag, avg_depth
    return avg_mag, None

# [PY2] Function returning multiple values
average_magnitude, average_depth = explosion_summary(filtered_data)
st.sidebar.markdown(f"**Average Magnitude:** {average_magnitude:.2f}")
if average_depth:
    st.sidebar.markdown(f"**Average Depth:** {average_depth:.2f}m")

# [PY3] Try/except + [PY4] List comprehension
st.subheader("List of Unique Test Locations")
try:
    locations = [loc for loc in filtered_data["Location"].unique() if isinstance(loc, str)]
    st.write(locations[:10])
except Exception as e:
    st.write(f"Error: {e}")

# [PY5] Dictionary usage
st.subheader("Country Color Map (Dict Example)")
color_dict = {country: f"Color #{i+1}" for i, country in enumerate(countries)}
for k, v in color_dict.items():
    st.write(f"{k}: {v}")
