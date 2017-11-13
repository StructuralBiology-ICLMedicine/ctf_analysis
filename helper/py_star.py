"""Convert between star file and pandas dataframe"""
import pandas as pd

def star_to_pandas(star_in):
    """Convert from star file to pandas dataframe"""
    star_cols = []
    star_data = []
    with open(star_in, 'r') as f:
        for line in f:
            if len(line.split()) <= 1:
                continue
            elif line.startswith('_rln'):
                col = line.split()[0].replace('_rln', '')
                star_cols.append(col)
            else:
                star_data.append(line.split())
    dataframe = pd.DataFrame(star_data, columns=star_cols)
    type_df = pd.DataFrame()
    for col in dataframe.columns:
        try:
            type_df[col] = pd.to_numeric(dataframe[col])
        except ValueError:
            type_df[col] = dataframe[col]
    return type_df

def pandas_to_star(dataframe, out_file):
    """Convert from pandas dataframe to star file"""
    out = open(out_file, 'w')
    out.write("data_\n\nloop_\n")
    col_index = 1
    for col in dataframe.columns:
        out.write("_rln{0} #{1}\n".format(col, col_index))
        col_index += 1
    out.close()
    dataframe.to_csv(out_file, sep="\t", index=False, header=False, mode='a')
