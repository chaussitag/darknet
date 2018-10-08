#!/usr/bin/env python3
# coding=utf-8

######################################
# History:
#    20180403, daguozhou created
######################################

r"""Create the label map and label list files for a dataset.

    The label map file contains a dictionary with one item for each category, each item contains id and name for a category.
    The label list file contains all category names.

Example usage:
    ./create_label_files.py --data_dir path_to_data_dir
    ./create_label_files.py --help
"""

import argparse
import os
import sys


def parse_args():
  parser = argparse.ArgumentParser(description="create the lable map file mapping class id to name")
  parser.add_argument("--data_dir", "-d", dest="data_dir", required=True,
                      help="a directory containing all image and label files, one sub-dir with the category name per category, and one label file of xml format per image")
  parser.add_argument("--output_dir", "-o", dest="output_dir", required=False, default="./",
                      help="optional, the output directory where to create the label map and label list file, default to current directory")

  return parser.parse_args()


if __name__ == "__main__":
  args = parse_args()

  if not os.path.isdir(args.data_dir):
    print("the directory %s does not exist" % (args.data_dir,))
    sys.exit(-1)

  output_dir = args.output_dir
  if not os.path.isdir(args.output_dir):
    print("the output directory %s does not exist, please create it" % output_dir)
    sys.exit(-1)

  label_map_path = os.path.join(output_dir, "label_map.txt")
  label_list_path = os.path.join(output_dir, "label_list.txt")

  with open(label_map_path, "w") as label_map_file, open(label_list_path, "w") as label_list_file:
    class_index = 1
    item_template = """\
item {
    id: %d
    name: '%s'
}

"""
    for category in os.listdir(args.data_dir):
      if os.path.isdir(os.path.join(args.data_dir, category)):
        label_list_file.write(category + "\n")
        label_map_file.write(item_template % (class_index, category))
        class_index = class_index + 1
