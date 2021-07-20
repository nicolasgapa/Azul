"""
Author: Nicolas Gachancipa
ANAC data processing

"""
# Imports.
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




# for i in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']:
#    raw_to_csv('Data\\2020\\basica2020-{}.txt'.format(i),
#               'Data\\2020\\basica2020-{}.csv'.format(i),
#               pd.read_json('data\\airport_list.json'))
