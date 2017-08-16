#!/usr/bin/env python
"""
Parse loggile and store statistic
"""

__version__ = "1.0.0"
__author__ = "Alexander Kamyanskiy"


import argparse
from utils import calc_statistic, save_report

# logname = '003.in'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Parse log file into statistic file.")

    parser.add_argument("input_file",
                        help="Filename to read from and parse.")
    parser.add_argument("output_file",
                        help="Filename to write result.")

    args = parser.parse_args()

    log_filename = args.input_file
    out_filename = args.output_file

    save_report(calc_statistic(log_filename), out_filename)
