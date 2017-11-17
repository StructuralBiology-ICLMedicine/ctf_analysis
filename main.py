"""Main file to handle input"""
import argparse
import ctf_analysis as ctf
from helper.ctf_log_extraction import logs_build_df, star_build_df

def main():
    """Run"""
    parser = argparse.ArgumentParser()
    parser.add_argument('input',
                        help="path to input e.g. Microgrpahs/*ctffind3.log",
                        nargs='*')

    args = parser.parse_args()
    files = args.input
    if files[0].endswith("star"):
        data = star_build_df(files[0])
        star_name = str(files[0])
        ctf.main(data, star_name)
    else:
        data = logs_build_df(files)
        ctf.main(data)

main()
