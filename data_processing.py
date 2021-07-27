"""
Author: Nicolas Gachancipa
ANAC data processing

"""
# Imports.
import datetime
import pandas as pd


# Functions.
def raw_to_csv(input_file, output_file, airport_data):
    # Print.
    print('\nProcessing file: {}.'.format(input_file))

    # Parse data.
    array = []
    with open(input_file) as f:
        mylist = list(f)
        for line in mylist:
            cells = line[:-1].split(';')
            cells = [w.replace("\"", "") for w in cells]
            array.append(cells)

    # Build dataframe.
    df = pd.DataFrame(array)
    df.columns = df.iloc[0]
    df = df[1:]

    # Obtain airport data.
    azul_airports = list(set(list(df['sg_iata_origem']) + list(df['sg_iata_destino'])))
    airport_data.columns = ['Airport', 'City', 'Country', 'IATA', 'ICAO', 'Latitude', 'Longitude', 'Elevation', 'TZ',
                            'DST', 'TZDB']
    airports = airport_data[airport_data['IATA'].isin(azul_airports)]
    not_found = [a for a in azul_airports if a not in list(airports['IATA'])]
    print('The following {} airports were not found: {}.'.format(len(not_found), not_found))

    # Filter out the airports that aren't in the database.
    df = df[~df['sg_iata_origem'].isin(not_found)]
    df = df[~df['sg_iata_destino'].isin(not_found)]

    # Add latitude, longitude to each flight's origin and destination.
    e = 1
    slat, elat, slon, elon, flight_IATAs = [], [], [], [], []
    for o, d in zip(df['sg_iata_origem'], df['sg_iata_destino']):
        origin, destination = airports[airports['IATA'] == o], airports[airports['IATA'] == d]
        flight_IATAs.append(o + d)
        if len(origin) == 1:
            slat.append(float(origin['Latitude']))
            slon.append(float(origin['Longitude']))
        else:
            slat.append('Null')
            slon.append('Null')
        if len(destination) == 1:
            elat.append(float(destination['Latitude']))
            elon.append(float(destination['Longitude']))
        else:
            elat.append('Null')
            elon.append('Null')
        if e % 1000 == 0:
            print('Lines processed: {} out if {} ({}%)'.format(e, len(df), round(e * 100 / len(df), 1)))
        e += 1
    print('Lines processed: 100%')
    df['StartLatitude'] = slat
    df['StartLongitude'] = slon
    df['EndLatitude'] = elat
    df['EndLongitude'] = elon
    df['FlightIATAs'] = flight_IATAs

    # Save csv file.
    df = df.rename(columns={'sg_iata_origem': 'Origin',
                            'sg_iata_destino': 'Destination',
                            'nr_ano_referencia': 'DepartureYear',
                            'nr_mes_referencia': 'DepartureMonth',
                            'nr_dia_referencia': 'DepartureDay',
                            'sg_empresa_iata': 'Airline'})
    df.to_csv(output_file, header=df.columns, encoding="utf-8-sig")
    print('File saved: {}.'.format(output_file))


def anac_to_siros(anac_data, siros_data, new_df):
    """
    Code to merge add the scheduled flight time (found in the SIROS datasets) to the ANAC data.

    :param anac_data:
    :param siros_data:
    :param new_df:
    :return:
    """
    ct = 0

    # Remove Nans and create a new column with the airline.
    siros_data = siros_data.drop('tx_codeshare', axis=1)
    siros_data = siros_data.dropna()
    siros_data['Date'] = [[str(int(i)) for i in d.split('/')] for d in siros_data['Date']]
    siros_data['Date'] = ['{}/{}/{}'.format(d, m, y) for d, m, y in siros_data['Date']]

    # Create empy column in the anac data, which will be filled with the scheduled departure times.
    anac_data['ScheduledDeparture'] = ['0' for _ in anac_data['nr_voo']]

    # Fill the 'ScheduledDeparture' column.
    for index, row in anac_data.iterrows():
        origin, destination, flight = row['sg_icao_origem'], row['sg_icao_destino'], str(row['nr_voo'])
        date = '{}/{}/{}'.format(str(row['DepartureDay']), str(row['DepartureMonth']), str(row['DepartureYear']))
        filtered = siros_data[siros_data['Origem'] == origin]
        filtered = filtered[filtered['Destino'] == destination]
        filtered = filtered[filtered['Voo'] == flight]
        filtered = filtered[filtered['Date'] == date]
        ct += 1
        if len(filtered) != 1:
            continue
        time = list(filtered['Partida Prevista'])[0].split(' ')[-1]
        anac_data.at[index, 'ScheduledDeparture'] = time
        if ct % 100 == 0:
            print(ct)
        if ct % 10000 == 0:
            print('Updating ANAC...')
            anac_data.to_csv(new_df)
    anac_data.to_csv(new_df, index=False)


def delay(df, new_df):
    """
    Compute the delay and add column to ANAC data.

    :param df: Processed ANAC data (output of the anac_to_siros function).
    :param new_df: Name of the new dataframe.
    :return:
    """

    # Drop Nans.
    df = df[df['nr_ano_partida_real'].notna()]
    df = df[df['nr_mes_partida_real'].notna()]
    df = df[df['nr_dia_partida_real'].notna()]

    # Convert the real and departure times to datetime format.
    real_departures = []
    scheduled_departures = []
    delays = []
    ct = 0
    total_rows = len(df)
    for index, row in df.iterrows():

        # Real.
        hr, mn, sc = row['hr_partida_real'].split(':')
        year, month, day = row['nr_ano_partida_real'], row['nr_mes_partida_real'], row['nr_dia_partida_real']
        real_time = datetime.datetime(int(year), int(month), int(day), int(hr), int(mn), int(sc))
        real_departures.append(real_time)

        # Scheduled.
        t = row['ScheduledDeparture'].split(':')
        if len(t) == 1:
            scheduled_time = '0'
            scheduled_departures.append(scheduled_time)
        else:
            if len(t) == 2:
                hr, mn = t
                sc = 0
            else:
                hr, mn, sc = t
            year, month, day = row['DepartureYear'], row['DepartureMonth'], row['DepartureDay']
            scheduled_time = datetime.datetime(int(year), int(month), int(day), int(hr), int(mn), int(sc))
            scheduled_departures.append(scheduled_time)

        # Delay.
        if scheduled_time == '0':
            delays.append('0')
        else:
            delays.append((real_time - scheduled_time).seconds / 60 + (real_time - scheduled_time).days * 1440)

        # Print progress.
        ct += 1
        if ct % 10000 == 0:
            print('Progress: {}%'.format(round(ct * 100 / total_rows, 2)))

    # Update/add columns.
    df['hr_partida_real'] = real_departures
    df['ScheduledDeparture'] = scheduled_departures
    df['Delay'] = delays
    df = df[df['Delay'] != '0']

    # Save new df.
    df.to_csv(new_df, index=False)


def add_airport_type(df, airport_types, new_df):
    """

    :param df: ANAC data.
    :param airport_types: Dataframe with list of airports (IATA codes) and their respective type.
    :param new_df: New dataframe.
    :return: Updated df.
    """
    # Build columns.
    list_of_airports = list(airport_types.index)
    types = airport_types.to_dict()['Type']
    origin_type, destination_type = [], []
    ct = 0
    max_len = len(df)
    for i, row in df.iterrows():
        if row['Origin'] in list_of_airports:
            origin_type.append(types[row['Origin']])
        else:
            origin_type.append(0)
        if row['Destination'] in list_of_airports:
            destination_type.append(types[row['Destination']])
        else:
            destination_type.append(0)
        ct += 1
        if ct % 1000 == 0:
            print('Progress: {}%.'.format(round(ct * 100 / max_len, 2)))

    # Add columns.
    df['OriginType'] = origin_type
    df['DestinationType'] = destination_type

    # Output new csv.
    df.to_csv(new_df, index=False)


# for i in ['01', '02', '03', '04', '05', '06']:
#   raw_to_csv('Data\\2021\\basica2021-{}.txt'.format(i),
#              'Data\\2021\\basica2021-{}.csv'.format(i),
#              pd.read_json('data\\airport_list.json'))

# To Processed.csv
# anac_to_siros(pd.read_csv('data\\2021\\ANAC_2021.csv'), pd.read_csv('data\\2021\\scheduled_2021.csv'),
# 'Processed_ANAC_2021.csv')

# To Delays.csv
# delay(pd.read_csv('data\\2021\\Processed_ANAC_2021.csv'), 'Delays_ANAC_2021.csv')

# To Final.csv
add_airport_type(pd.read_csv('data\\2021\\Delays_ANAC_2021.csv'),
                 pd.read_csv('data\\airport_types.csv', index_col=0), 'data\\2021\\Final_ANAC_2021.csv')
