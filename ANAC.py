"""
Author: Nicolas Gachancipa
ANAC data processing

"""
# Imports.
import pandas as pd

# Inputs.
data_file = 'Data\\FirstDataSet.csv'


# Functions.
def raw_to_csv(input_file, output_file):
    # Parse data.
    array = []
    with open(input_file) as f:
        mylist = list(f)
        for line in mylist:
            cells = line[:-1].split(';')
            array.append(cells)

    # Build dataframe.
    df = pd.DataFrame(array)

    # Save csv file.
    df.to_csv(output_file, header=None)


raw_to_csv(data_file, 'Data\\Processed.csv')
