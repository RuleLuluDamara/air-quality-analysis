import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import numpy as np
import altair as alt

from babel.numbers import format_currency

sns.set_theme(style="darkgrid")


def visualisasi_korelasi(df):
    correlation = df['TEMP'].corr(df['O3'])

    st.title(
        f"Korelasi antara suhu (TEMP) dan tingkat ozon (O3): {correlation}")

    scatter_plot = alt.Chart(df).mark_circle().encode(
        x='TEMP:Q',
        y='O3:Q',
        tooltip=['TEMP', 'O3']
    ).properties(
        width=600,
        height=400
    )

    st.altair_chart(scatter_plot, use_container_width=True)


def create_pollutant_plot(frame, pollutant, color):
    df = frame.pivot_table(index='year', values=pollutant, aggfunc='median').reset_index(
    ).sort_values(by='year', ascending=False)

    st.subheader('Median ' + pollutant + ' Levels Over the Years')

    chart = alt.Chart(df).mark_line(point=True).encode(
        x='year:O',
        y=alt.Y(pollutant, title=pollutant + ' Median Level'),
        color=alt.value(color),
        tooltip=['year', alt.Y(pollutant, title=pollutant + ' Median Level')]
    ).properties(
        width=600,
        height=300
    )

    st.altair_chart(chart, use_container_width=True)


def create_monthly_plot(frame, pollutant):
    frame['month'].replace([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], [
                           'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], inplace=True)

    custom_dict = {'Jan': 0, 'Feb': 1, 'Mar': 2, 'Apr': 3, 'May': 4,
                   'Jun': 5, 'Jul': 6, 'Aug': 7, 'Sep': 8, 'Oct': 9, 'Nov': 10, 'Dec': 11}

    frame[pollutant] = pd.to_numeric(frame[pollutant], errors='coerce')

    grouped_df = frame.groupby(["month"])[pollutant].agg(
        ['median', 'count']).reset_index()

    # Sort the months using the custom_dict
    grouped_df['month'] = pd.Categorical(grouped_df['month'], categories=sorted(
        custom_dict, key=custom_dict.get), ordered=True)
    grouped_df = grouped_df.sort_values('month')

    chart = alt.Chart(grouped_df).mark_point().encode(
        x=alt.X('month:N', sort=alt.SortField('month:N', order='ascending')),
        y='median:Q',
        color='month:N',
        tooltip=['month:N', alt.Y('median:Q', title='SO2 Median Level')]
    ).properties(
        width=600,
        height=300
    )

    st.altair_chart(chart, use_container_width=True)


# Load cleaned data
air_df = pd.read_csv("/dashboard/main_data.csv")

# Sidebar
with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")

# ------------------Header------------------------#
st.header('Dicoding Air Quality Explorer :cloud:')
st.subheader('Dashboard Interaktif untuk Memahami Polusi Udara')

# Sidebar filter for selecting year and station
selected_year = st.sidebar.selectbox(
    'Pilih Tahun', sorted(air_df['year'].unique()))
selected_station = st.sidebar.selectbox(
    'Pilih Stasiun', sorted(air_df['station'].unique()))

# Filter data based on user selection
filtered_data = air_df[(air_df['year'] == selected_year)
                       & (air_df['station'] == selected_station)]

# Line chart for pollution levels over time
st.line_chart(filtered_data[['PM2.5', 'PM10', 'SO2',
              'NO2', 'CO', 'O3']].set_index(filtered_data['month']))

# Display the filtered data
st.write(f"Data untuk Tahun {selected_year} dan Stasiun {selected_station}")
st.write(filtered_data)

# ----------------------------#
visualisasi_korelasi(air_df)

air_df['SO2'] = pd.to_numeric(air_df['SO2'], errors='coerce')
air_df['NO2'] = pd.to_numeric(air_df['NO2'], errors='coerce')
air_df['CO'] = pd.to_numeric(air_df['CO'], errors='coerce')
air_df['O3'] = pd.to_numeric(air_df['O3'], errors='coerce')

st.header('Analisis Trend Polutan')
col1, col2 = st.columns(2)
with col1:
    create_pollutant_plot(air_df, 'NO2', 'red')
    create_pollutant_plot(air_df, 'SO2', 'red')

with col2:
    create_pollutant_plot(air_df, 'CO', 'olive')
    create_pollutant_plot(air_df, 'O3', 'blue')

st.title('Monthly Pollutan Levels')
create_monthly_plot(air_df, 'SO2')
create_monthly_plot(air_df, 'NO2')
create_monthly_plot(air_df, 'CO')
create_monthly_plot(air_df, 'O3')

# Visualize the maximum and minimum pollution levels
st.subheader('Analisis Polutan Tertinggi dan Terendah')
polutan_columns = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']
max_polutan = [filtered_data[polutan].max() for polutan in polutan_columns]
min_polutan = [filtered_data[polutan].min() for polutan in polutan_columns]

# Create a DataFrame
data = pd.DataFrame({'Polutant': polutan_columns,
                    'Max Value': max_polutan, 'Min Value': min_polutan})

# Plot using Streamlit
st.bar_chart(data.set_index('Polutant'))


st.caption('Copyright © Dicoding 2023')
