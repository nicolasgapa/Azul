"""

Azul Brazilian Airlines
Author: Nicolas Gachancipa

"""
# Imports.
import datetime
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go


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
    dest_count = \
        df.groupby('Destination').count().rename(columns={'TaxiIn': 'ct'}).sort_values('ct', ascending=False)[
            'ct']
    ax2.bar(dest_count.index[:15], dest_count[:15])
    ax2.set_xlabel('Airport')
    ax2.set_ylabel('Number of Arriving Flights')
    plt.show()


def flights_map(df, df_airports, year=None, month=None, airline=None):
    """
    Display a map with the flights.

    :param df: Dataframe containing the flight info.
    :param df_airports: Dataframe contining airport info (airport_list.json).
    :param year: E.g. 20 for Azul data, 2020 for ANAC data.
    :param month: E.g. 7 for July.
    :param airline: Airline code. E.g. 'AD' for Azul.
    :return:
    """
    # Filter per date.
    title = 'Azul Brazilian Airlines Flight Network <br> (Hover for airport names)'
    if year is not None:
        df = df[df['DepartureYear'] == year]
        title += ' <br> Year: {}'.format(year)
    if month is not None:
        df = df[df['DepartureMonth'] == month]
        title += ' <br> Month: {}'.format(month)

    # Filter per airline.
    if airline is not None:
        df = df[df['Airline'] == airline]
        airline = airline if airline is not None else 'All'
        title += ' <br> Airline: {}.'.format(airline)

    # Obtain airport data.
    azul_airports = list(set(list(df['Origin']) + list(df['Destination'])))
    df_airports.columns = ['Airport', 'City', 'Country', 'IATA', 'ICAO', 'Latitude', 'Longitude', 'Elevation', 'TZ',
                           'DST', 'TZDB']
    airports = df_airports[df_airports['IATA'].isin(azul_airports)]
    not_found = [a for a in azul_airports if a not in list(airports['IATA'])]

    # Filter out the airports that aren't in the database.
    df = df[~df['Origin'].isin(not_found)]
    df = df[~df['Destination'].isin(not_found)]

    # Create figure.
    fig = go.Figure()
    fig.update_layout(title_text=title, showlegend=False,
                      geo=dict(scope='world', projection_type='mercator', showland=True, landcolor='rgb(243, 243, 243)',
                               countrycolor='rgb(204, 204, 204)', showcountries=True, lataxis=dict(range=[-34, 6]),
                               lonaxis=dict(range=[-75, -30])), height=800, width=1500)

    # Compute the count of each flight.
    flights = df.groupby('FlightIATAs').count()['Origin']

    # Plot the lines.
    max_count = max(flights)
    for count, codes in zip(flights, flights.index):
        # Obtain latitude and longitude.
        origin_info = airports[airports['IATA'] == codes[:3]]
        destination_info = airports[airports['IATA'] == codes[3:]]
        slat, slon = float(origin_info['Latitude']), float(origin_info['Longitude'])
        elat, elon = float(destination_info['Latitude']), float(destination_info['Longitude'])

        # Trace flight.
        fig.add_trace(go.Scattergeo(locationmode='country names', lon=[slon, elon], lat=[slat, elat], mode='lines',
                                    line=dict(width=1, color='red'), opacity=float(count / max_count)))

    # Add airport locations.
    fig.add_trace(go.Scattergeo(locationmode='country names', lon=airports['Longitude'], lat=airports['Latitude'],
                                hoverinfo='text', text=[name + ' ({}) - {}'.format(code, city) for name, code, city in
                                                        zip(airports['Airport'], airports['IATA'],
                                                            airports['City'])], mode='markers',
                                marker=dict(size=3, color='rgb(70,130,180)',
                                            line=dict(width=3, color='rgba(68, 68, 68, 0)'))))

    # Show fig.
    fig.show()

    # Return the figure.
    return fig


def month_bar_plot(df, year, airport=None, airline=None):
    """
    Create a bar plot showing the # of departures and arrivals per month.

    :param df: Dataset (from ANAC website).
    :param year: E.g. 2020
    :param airport: IATA code (optional).
    :param airline: Code. E.g. AD for azul.
    :return: Plot.
    """

    # Filter for airline.
    if airline is not None:
        df = df[df['Airline'] == airline]

    # Filter for year.
    if year is not None:
        df = df[df['DepartureYear'] == year]

    # Filter for airport.
    if airport is not None:
        df_origin = df[df['Origin'] == airport]
        df_destination = df[df['Destination'] == airport]
    else:
        df_origin, df_destination = df.copy(), df.copy()

    # Count how many flights per month.
    origin_count = df_origin.groupby('DepartureMonth').count().iloc[:, 0]
    destination_count = df_destination.groupby('DepartureMonth').count().iloc[:, 0]

    # Plot.
    fig = plt.figure()  # Create matplotlib figure.
    ax = fig.add_subplot(111)  # Create matplotlib axes.
    origin_count.plot(kind='bar', color='#70C5C6', ax=ax, width=0.4, position=0, label='Departures')
    destination_count.plot(kind='bar', color='#13729E', ax=ax, width=0.4, position=1, label='Arrivals')
    ax.set_xlabel('Month')
    ax.set_ylabel('Number of Flights')
    ax.set_xlim([-1, 12])
    ax.legend()
    plt.suptitle('Number of flights per month (Source: ANAC)')
    plt.title('Airport: {}. Airline: {}. Year: {}.'.format('All' if airport is None else airport,
                                                           'All' if airline is None else airline, year))
    plt.show()


def day_bar_plot(df, year, month, airport=None, airline=None):
    """
    Create a bar plot showing the # of departures and arrivals per month.

    :param df: Dataset (from ANAC website).
    :param year: E.g. 2020
    :param airport: IATA code (optional).
    :param airline: Code. E.g. AD for azul.
    :return: Plot.
    """
    # Filter for airline.
    if airline is not None:
        df = df[df['Airline'] == airline]

    # Filter for year and month.
    if year is not None:
        df = df[df['DepartureYear'] == year]
    if month is not None:
        df = df[df['DepartureMonth'] == month]

    # Filter for airport.
    if airport is not None:
        df_origin = df[df['Origin'] == airport]
        df_destination = df[df['Destination'] == airport]
    else:
        df_origin, df_destination = df.copy(), df.copy()

    # Count how many flights per month.
    origin_count = df_origin.groupby('DepartureDay').count().iloc[:, 0]
    destination_count = df_destination.groupby('DepartureDay').count().iloc[:, 0]

    # Plot.
    fig = plt.figure()  # Create matplotlib figure.
    ax = fig.add_subplot(111)  # Create matplotlib axes.
    origin_count.plot(kind='bar', color='#70C5C6', ax=ax, width=0.4, position=0, label='Departures')
    destination_count.plot(kind='bar', color='#13729E', ax=ax, width=0.4, position=1, label='Arrivals')
    ax.set_xlabel('Day')
    ax.set_ylabel('Number of Flights')
    weekdays = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
    no_days = len(origin_count)
    x_labels = [weekdays[datetime.datetime(year, month, d).weekday()] + ' {}'.format(str(d)) for d in
                range(1, no_days + 1)]
    ax.set_xticklabels(x_labels)
    ax.legend()
    plt.suptitle('Number of flights per day (Source: ANAC)')
    plt.title('Airport: {}. Airline: {}. Year: {}. Month: {}.'.format('All' if airport is None else airport,
                                                                      'All' if airline is None else airline, year,
                                                                      month))
    plt.show()


# od_bar_plot(pd.read_csv('data\\azul_data.csv', low_memory=False))
# fig = flights_map(pd.read_csv('data\\2020\\ANAC_2020.csv', low_memory=False),
#                  pd.read_json('data\\airport_list.json'),
#                  year=None, month=None, airline='AD')
# month_bar_plot(pd.read_csv('data\\2020\\ANAC_2020.csv'), year=2020)
# day_bar_plot(pd.read_csv('data\\2020\\ANAC_2020.csv'), 2020, 5, airline='AD', airport='CNF')
