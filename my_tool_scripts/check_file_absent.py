#!/usr/bin/env python3
# coding=utf-8

import argparse
import os
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="check if there's any file missing in a file list")
    parser.add_argument("--input_list", "-i", required=True,
                        help="path to a text file contains the file paths to be checked")
    args = parser.parse_args()

    if not os.path.isfile(args.input_list):
        print("%s does not exist" % args.input_list)
        sys.exit(-1)

    total_non_exist = 0
    with open(args.input_list, "r") as f:
        for line in f:
            file_path = line.strip()
            if not os.path.isfile(file_path):
                print("%s does not exist" % file_path)
                total_non_exist += 1

    if total_non_exist > 0:
        print("there're %d files missing" % total_non_exist)
    else:
        print("all files are there")
