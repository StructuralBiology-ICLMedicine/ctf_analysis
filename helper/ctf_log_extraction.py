"""Functionality to extract relevant information from gctf or CTFFIND4 logfiles"""
from math import fabs
import pandas as pd

from helper.py_star import star_to_pandas


def gctf_extract(log):
    """If gctf logfile extract correct information."""
    with open(log, 'r') as f:
        for line in f:
            if "Final Values" in line:
                param = line.split()
                defocus = round(((float(param[0]) + float(param[1])) / 2), 2)
                defocus_dif = round(fabs(float(param[1]) - float(param[0])), 3)
                score = float(param[3])
            elif "Resolution limit" in line:
                resolution = float(line.split()[6])
            elif "Reading file" in line:
                micrograph = line.split()[2]
    return (micrograph, resolution, defocus, defocus_dif, score)


def ctffind_extract(log):
    """If CTFFIND logfile extract correct information."""
    with open(log, 'r') as f:
        for line in f:
            if "Final Values" in line:
                param = line.split()
                defocus = (float(param[0]) + float(param[1])) / 2
                defocus_dif = round(fabs(float(param[1]) - float(param[0])), 3)
                score = float(param[3])
            elif "Thon rings" in line:
                resolution = float(line.split()[8])
            elif "Summary information for file" in line:
                micrograph = line.split()[4]
    return (micrograph, resolution, defocus, defocus_dif, score)


def check_source(log):
    """Check if gctf or CTFFIND was used."""
    with open(log, 'r') as f:
        for line in f:
            if "GCTF" in line:
                return "gctf"
    return "ctffind"


def logs_build_df(logs):
    """Build a dataframe from the original log files"""
    all_values = []
    if check_source(logs[0]) == "gctf":
        for log in logs:
            all_values.append(gctf_extract(log))
    else:
        for log in logs:
            all_values.append(ctffind_extract(log))
    df_values = pd.DataFrame(all_values,
                             columns=['Micrograph_name',
                                      'Resolution_limit',
                                      'Defocus',
                                      'Defocus_difference',
                                      'CC_score'])
    return df_values


def write_subset_star(in_star, out_star, good_list):
    """Write star file with user subset"""
    out = open(out_star, 'w')
    with open(in_star, 'r') as f:
        for line in f:
            if (len(line.split())) <= 3:
                out.write(line)
                if "_rlnMicrographName" in line:
                    mic_col = int(line.split()[1].translate(None, '#'))
            else:
                if any((line.split()[mic_col - 1]) in entry for entry in good_list):
                    out.write(line)
                else:
                    continue
    out.close()


def star_build_df(file):
    """Build a dataframe from a star file"""
    data = star_to_pandas(file)
    
    defocus_UV = data[['DefocusU', 'DefocusV']]
    data['Defocus'] = defocus_UV.mean(axis=1)
    data['Defocus_difference'] = defocus_UV.apply(lambda x: fabs(x[0] - x[1]), axis=1)
    df_values = data[['MicrographName',
                      'FinalResolution',
                      'Defocus',
                      'Defocus_difference',
                      'CtfFigureOfMerit']]
    df_values.columns = ['Micrograph_name',
                         'Resolution_limit',
                         'Defocus',
                         'Defocus_difference',
                         'CC_score']
    return df_values