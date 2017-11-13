"""Main file to handle input"""

import argparse
import ctf_analysis as ctf

parser = argparse.ArgumentParser()
parser.add_argument('input',
                    help="path to input e.g. Microgrpahs/*ctffind3.log",
                    nargs='*')

args = parser.parse_args()
files = args.input

ctf.main(files)
