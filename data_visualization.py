"""

Azul Brazilian Airlines
Author: Nicolas Gachancipa

"""
# Imports.
# from pyairports.pyairports.airports import Airports
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go

df_airports = pd.read_csv(
    'https://raw.githubusercontent.com/plotly/datasets/master/2011_february_us_airport_traffic.csv')
df_airports.head()

azul_data = 'data\\FirstDataSet.csv'
azul_df = pd.read_csv(azul_data, low_memory=False)
azul_airports = list(set(list(azul_df['Origin']) + list(azul_df['Destination'])))
df_airports = pd.read_json('airport_list.json')
df_airports.columns = ['Airport', 'City', 'Country', 'IATA', 'ICAO', 'Latitude', 'Longitude', 'Elevation', 'TZ', 'DST',
                       'TZDB']
brazilian_airports = df_airports[df_airports['IATA'].isin(azul_airports)]
fig = go.Figure()

print(df_airports)
fig.add_trace(go.Scattergeo(locationmode='country names', lon=brazilian_airports['Longitude'],
                            lat=brazilian_airports['Latitude'],
                            hoverinfo='text',
                            text=[name + ' ({})'.format(code) for name, code in
                                  zip(brazilian_airports['Airport'], brazilian_airports['IATA'])],
                            mode='markers',
                            marker=dict(
                                size=2,
                                color='rgb(255, 0, 0)',
                                line=dict(
                                    width=3,
                                    color='rgba(68, 68, 68, 0)'
                                )
                            )))

df_flight_paths = pd.read_csv(
    'https://raw.githubusercontent.com/plotly/datasets/master/2011_february_aa_flight_paths.csv')
df_flight_paths.head()
# flight_paths = []
# for i in range(len(df_flight_paths)):
#     fig.add_trace(
#         go.Scattergeo(
#             locationmode='USA-states',
#             lon=[df_flight_paths['start_lon'][i], df_flight_paths['end_lon'][i]],
#             lat=[df_flight_paths['start_lat'][i], df_flight_paths['end_lat'][i]],
#             mode='lines',
#             line=dict(width=1, color='red'),
#             opacity=float(df_flight_paths['cnt'][i]) / float(df_flight_paths['cnt'].max()),
#         )
#     )

fig.update_layout(
    title_text='Azul Brazilian Airlines Flight Network <br> (Hover for airport names)',
    showlegend=False,
    geo=dict(scope='south america', projection_type='mercator', showland=True, landcolor='rgb(243, 243, 243)',
             countrycolor='rgb(204, 204, 204)'))

fig.show()

# Inputs.
data = 'data\\FirstDataSet.csv'


# Functions.
def od_bar_plot(df):
    """
    Create bar plots with the count of origin and destination flights.

    :param df: Data (pandas df).
    :return: Displays the plot.
    """

    # Create plots.
    fig = plt.figure(constrained_layout=True)
    gs = fig.add_gridspec(1, 2)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])

    # Origin.
    origin_count = df.groupby('Origin').count().rename(columns={'TaxiIn': 'ct'}).sort_values('ct', ascending=False)[
        'ct']
    ax1.bar(origin_count.index[:15], origin_count[:15])
    ax1.set_xlabel('Airport')
    ax1.set_ylabel('Number of Departing Flights')

    # Destination
    dest_count = df.groupby('Destination').count().rename(columns={'TaxiIn': 'ct'}).sort_values('ct', ascending=False)[
        'ct']
    ax2.bar(dest_count.index[:15], dest_count[:15])
    ax2.set_xlabel('Airport')
    ax2.set_ylabel('Number of Arriving Flights')
    plt.show()


dataframe = pd.read_csv(data, low_memory=False)
print(dataframe)
# od_bar_plot(dataframe)
