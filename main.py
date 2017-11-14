"""Main file to handle input"""
import argparse
import ctf_analysis as ctf
from helper.ctf_log_extraction import build_df

def main():
    """Run app"""
    parser = argparse.ArgumentParser()
    parser.add_argument('input',
                        help="path to input e.g. Microgrpahs/*ctffind3.log",
                        nargs='*')

    args = parser.parse_args()
    files = args.input
    data = build_df(files)

    ctf.main(data)

main()
