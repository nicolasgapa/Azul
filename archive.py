"""

Azul Brazilian Airlines
Author: Jose Nicolas Gachancipa
Archive

"""

# Code to add date and time columns to the df.
date_times = pd.DataFrame([[int(i) for i in re.split('/| |:', ft)] for ft in df_azul_data['ScheduledDepartureLCL']])
date_times.columns = ['DepartureDay', 'DepartureMonth', 'DepartureYear', 'DepartureHour', 'DepartureMinute']
df_azul_data = pd.concat([df_azul_data, date_times], axis=1)

# Code to add latitudes and longitudes to the df.
slat, elat, slon, elon, flight_IATAs = [], [], [], [], []
e = 1
for o, d in zip(df_azul_data['Origin'], df_azul_data['Destination']):
    origin, destination = airports[airports['IATA'] == o], airports[airports['IATA'] == d]
    flight_IATAs.append(o + d)
    if len(origin) > 0:
        slat.append(float(origin['Latitude']))
        slon.append(float(origin['Longitude']))
    else:
        slat.append('Null')
        slon.append('Null')
    if len(destination) > 0:
        elat.append(float(destination['Latitude']))
        elon.append(float(destination['Longitude']))
    else:
        elat.append('Null')
        elon.append('Null')
    if e % 100 == 0:
        print(e)
    e += 1
df_azul_data['StartLatitude'] = slat
df_azul_data['StartLongitude'] = slon
df_azul_data['EndLatitude'] = elat
df_azul_data['EndLongitude'] = elon
df_azul_data['FlightIATAs'] = flight_IATAs

# Code to merge files.
df = pd.read_csv('Data\\2020\\basica2020-01.csv', low_memory=False)
for i in ['02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']:
    df_new = pd.read_csv('Data\\2020\\basica2020-{}.csv'.format(i), low_memory=False)
    df = pd.concat([df, df_new])
df.to_csv('ANAC_2020.csv')
