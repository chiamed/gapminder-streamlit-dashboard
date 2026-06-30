import streamlit as st
import pandas as pd
import plotly.express as px

# PAGE TITLE
st.set_page_config(page_title="Gapminder Dashboard", page_icon="🌍", layout="wide")

# Load Gapminder dataset using Plotly Express
@st.cache_data
def load_data():
    return px.data.gapminder()

df = load_data()

# Metric labels for clearer chart titles and axes
metric_labels = {
    "lifeExp": "Life Expectancy",
    "gdpPercap": "GDP per Capita",
    "pop": "Population"
}

# SIDEBAR
st.sidebar.title("Navigation")
pages = ["Overview", "Data Explorer", "Visualizations", "Trend Analysis", "World Map", "Download"]
selection = st.sidebar.radio("Go to page:", pages)

# PAGE 1: OVERVIEW
if selection == "Overview":
    st.title("Gapminder Dataset Overview")
    st.write("""
    Welcome to this interactive dashboard based on the **Gapminder** dataset. 
    This dataset tracks global indicators such as life expectancy, GDP per capita, and population of numerous countries over the decades.
    """)

    st.subheader("Key Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Number of Countries", df["country"].nunique())
    col2.metric("Years Covered", f"{df['year'].min()} - {df['year'].max()}")
    col3.metric(
        "Maximum World Population",
        f"{df.loc[df['year'] == df['year'].max(), 'pop'].sum():,.0f}"
    )

    st.write("### A preview of the data")
    st.dataframe(df.head(10))

# PAGE 2: DATA EXPLORER
elif selection == "Data Explorer":
    st.title("Data Explorer")
    st.write("Filter the dataset by continent, country, and year range.")

    col1, col2 = st.columns(2)
    continents = col1.multiselect(
        "Select Continent:",
        options=df["continent"].unique(),
        default=df["continent"].unique()
    )

    filtered_countries = df[df["continent"].isin(continents)]["country"].unique()
    countries = col2.multiselect(
        "Select Country:",
        options=filtered_countries,
        default=filtered_countries[:5]
    )

    years = st.slider(
        "Select year range:",
        int(df["year"].min()),
        int(df["year"].max()),
        (1952, 2007),
        step=5
    )

    filtered_df = df[
        (df["continent"].isin(continents)) &
        (df["country"].isin(countries)) &
        (df["year"] >= years[0]) &
        (df["year"] <= years[1])
    ]

    st.write(f"Found **{len(filtered_df)}** rows matching your criteria.")
    st.dataframe(filtered_df, width='stretch')

# PAGE 3: VISUALIZATIONS
elif selection == "Visualizations":
    st.title("Interactive Visualizations")
    st.write("Explore the bubble chart to compare GDP per capita vs life expectancy.")

    view_type = st.radio("Choose visualization mode:", ["Over time", "Single year"])

    if view_type == "Single year":
        selected_year = st.selectbox("Select year:", sorted(df["year"].unique()))
        plot_df = df[df["year"] == selected_year]

        fig = px.scatter(
            plot_df,
            x="gdpPercap",
            y="lifeExp",
            size="pop",
            color="continent",
            hover_name="country",
            log_x=True,
            size_max=60,
            title=f"GDP per capita vs life expectancy ({selected_year})",
            labels={
                "gdpPercap": "GDP per Capita",
                "lifeExp": "Life Expectancy",
                "pop": "Population",
                "continent": "Continent"
            }
        )

        st.plotly_chart(fig, width='stretch')

        st.info("""
        This chart shows the relationship between wealth and health in a selected year. 
        Countries with higher GDP per capita usually have higher life expectancy, while bubble size highlights population differences.
        """)

    else:
        fig = px.scatter(
            df,
            x="gdpPercap",
            y="lifeExp",
            animation_frame="year",
            animation_group="country",
            size="pop",
            color="continent",
            hover_name="country",
            log_x=True,
            size_max=60,
            range_x=[100, 100000],
            range_y=[20, 90],
            title="Evolution: GDP per Capita vs Life Expectancy (1952 - 2007)",
            labels={
                "gdpPercap": "GDP per Capita",
                "lifeExp": "Life Expectancy",
                "pop": "Population",
                "continent": "Continent"
            }
        )

        st.plotly_chart(fig, width='stretch')

        st.info("""
        Over time, many countries move upward and to the right, showing improvements in both life expectancy and GDP per capita. 
        The animation helps reveal long-term global development patterns.
        """)

# PAGE 4: TREND ANALYSIS
elif selection == "Trend Analysis":
    st.title("Trend Analysis")
    st.write("Compare the evolution of different countries and continents over time.")

    metric = st.selectbox(
        "Select metric to analyze:",
        options=list(metric_labels.keys()),
        format_func=lambda x: metric_labels[x]
    )

    countries_to_compare = st.multiselect(
        "Select Countries to compare:",
        options=df["country"].unique(),
        default=["Italy", "Germany", "France"]
    )

    if countries_to_compare:
        trend_df = df[df["country"].isin(countries_to_compare)]

        fig = px.line(
            trend_df,
            x="year",
            y=metric,
            color="country",
            markers=True,
            title=f"Trend of {metric_labels[metric]} Over Time",
            labels={
                "year": "Year",
                metric: metric_labels[metric],
                "country": "Country"
            }
        )

        st.plotly_chart(fig, width='stretch')

        st.info(f"""
        This chart compares how {metric_labels[metric].lower()} changed over time for the selected countries. 
        It is useful for identifying differences in growth, decline, or stability between countries.
        """)
    else:
        st.warning("Select at least one country to display the chart.")

    st.subheader("Continent Comparison")

    continent_trend_df = df.groupby(["year", "continent"], as_index=False)[metric].mean()

    fig_continent = px.line(
        continent_trend_df,
        x="year",
        y=metric,
        color="continent",
        markers=True,
        title=f"Average {metric_labels[metric]} by Continent",
        labels={
            "year": "Year",
            metric: f"Average {metric_labels[metric]}",
            "continent": "Continent"
        }
    )

    st.plotly_chart(fig_continent, width='stretch')

    st.info(f"""
    This continent-level comparison shows broader regional trends in {metric_labels[metric].lower()}. 
    It helps connect individual country patterns with larger continental differences.
    """)

# PAGE 5: WORLD MAP
elif selection == "World Map":
    st.title("World Map")
    st.write("Explore how life expectancy, GDP per capita, and population vary across countries.")

    map_metric = st.selectbox(
        "Select metric to display:",
        options=list(metric_labels.keys()),
        format_func=lambda x: metric_labels[x]
    )

    map_year = st.selectbox(
        "Select year:",
        options=sorted(df["year"].unique())
    )

    map_df = df[df["year"] == map_year]

    fig = px.choropleth(
        map_df,
        locations="iso_alpha",
        color=map_metric,
        hover_name="country",
        hover_data={
            "continent": True,
            "lifeExp": ":.1f",
            "gdpPercap": ":,.0f",
            "pop": ":,"
        },
        color_continuous_scale="Viridis", # colorblind friendly color scale
        title=f"{metric_labels[map_metric]} by country in {map_year}",
        labels={
            map_metric: metric_labels[map_metric],
            "continent": "Continent",
            "lifeExp": "Life Expectancy",
            "gdpPercap": "GDP per Capita",
            "pop": "Population"
        }
    )

    fig.update_layout(
        geo=dict(showframe=False, showcoastlines=True),
        margin=dict(l=0, r=0, t=50, b=0)
    )

    st.plotly_chart(fig, width='stretch')

    st.info(f"""
    This map shows the geographic distribution of {metric_labels[map_metric].lower()} in {map_year}. 
    It helps identify regional differences and compare countries visually.
    """)

# PAGE 5: DOWNLOAD
elif selection == "Download":
    st.title("Download Data")
    st.write("Apply filters and download your personalized dataset in CSV format.")

    continents = st.multiselect(
        "Filter Continent:",
        options=df["continent"].unique(),
        default=df["continent"].unique()
    )

    filtered_countries = df[df["continent"].isin(continents)]["country"].unique()

    countries = st.multiselect(
        "Filter Countries:",
        options=filtered_countries,
        default=filtered_countries
    )

    years = st.slider(
        "Filter Years:",
        int(df["year"].min()),
        int(df["year"].max()),
        (1952, 2007),
        step=5
    )

    download_df = df[
        (df["continent"].isin(continents)) &
        (df["country"].isin(countries)) &
        (df["year"] >= years[0]) &
        (df["year"] <= years[1])
    ]

    st.write(f"The filtered dataset contains **{len(download_df)}** rows.")

    st.write("Preview of data to download:")
    st.dataframe(download_df.head(10), width='stretch')

    @st.cache_data
    def convert_df(data):
        return data.to_csv(index=False).encode("utf-8")

    csv = convert_df(download_df)

    st.download_button(
        label="Download filtered data as CSV",
        data=csv,
        file_name="gapminder_filtered.csv",
        mime="text/csv"
    )