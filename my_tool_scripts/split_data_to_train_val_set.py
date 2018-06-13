#!/usr/bin/env python3
# coding=utf-8

######################################
# History:
#    20180403, daguozhou created
######################################

r"""Split the whole dataset into training and validation set.

    The absolute path for all image and annotation files of the training set are collected into two seperate text files,
    and the same for the validataion set.

Example usage:
    ./split_data_to_train_val_set.py --data_dir path_to_data_dir
    ./split_data_to_train_val_set.py --help
"""

import argparse
import os
import sys
import glob
import random

def parse_args():
  description_msg = """\
split the whole dataset into training and validation set.
the absolute path for all image and annotation files of the training set are collected into two seperate text files,
and the same for the validataion set.
"""
  parser = argparse.ArgumentParser(description=description_msg, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument("--data_dir", "-d", dest="data_dir", required=True,
                      help="a directory containing all image and label files, one sub-dir with the category name per category, and one label file of xml format per image")
  parser.add_argument("--enhanced_data_dir", "-e", dest="enhanced_data_dir", required=False, default=None,
                      help="optional, a directory containing the enhanced training image and label files, no image in this directory is used for validation")
  parser.add_argument("--validation_ratio", "-r", dest="validation_ratio", required=False, default="0.1", type=float,
                      help="optional, the ratio for the validation set, default to 0.1, must be a float number between 0.0 and 1.0")

  return parser.parse_args()


possible_image_suffix = [".jpg", ".png", ".jpeg", ".JPG", ".PNG", ".JPEG"]


def find_corresponding_image(xml_ann_path):
  path_without_suffix = xml_ann_path.rsplit(".", 1)[0]
  for suffix in possible_image_suffix:
    if os.path.isfile(path_without_suffix + suffix):
      return path_without_suffix + suffix

  return None


if __name__ == "__main__":
  args = parse_args()

  if not os.path.isdir(args.data_dir):
    print("the directory %s does not exist" % (args.data_dir,))
    sys.exit(-1)

  if args.validation_ratio < 0 or args.validation_ratio > 1:
    print("the ratio for the validataion set must between [0.0, 1.0]")
    sys.exit(-1)

  train_files = []
  validation_files = []

  data_dir = os.path.abspath(args.data_dir)
  for category in os.listdir(data_dir):
    if os.path.isdir(os.path.join(data_dir, category)):
      all_xml_files = glob.glob(os.path.join(data_dir, category, "*.xml"))
      category_valid_files = []
      # loop over the xml annotation file list to exclude those have no corresponding images
      for xml_path in all_xml_files:
        image_path = find_corresponding_image(xml_path)
        if image_path is not None:
          category_valid_files.append((xml_path, image_path))
        else:
          print("%s has no corresponding image" % xml_path)
      total = len(category_valid_files)
      if total > 0:
        random.shuffle(category_valid_files)
        num_val = int(total * args.validation_ratio)
        train_files.extend(category_valid_files[num_val:])
        validation_files.extend(category_valid_files[:num_val])

  if args.enhanced_data_dir is not None:
    if not os.path.isdir(args.enhanced_data_dir):
      print("the enhanced training data directory %s does not exist, ignore it" % (args.enhanced_data_dir,))
    else:
      enhanced_data_dir = os.path.abspath(args.enhanced_data_dir)
      for category in os.listdir(enhanced_data_dir):
        if os.path.isdir(os.path.join(enhanced_data_dir, category)):
          all_xml_files = glob.glob(os.path.join(enhanced_data_dir, category, "*.xml"))
          # loop over the xml annotation file list to exclude those have no corresponding images
          for xml_path in all_xml_files:
            image_path = find_corresponding_image(xml_path)
            if image_path is not None:
              train_files.append((xml_path, image_path))
      random.shuffle(train_files)

  num_train = len(train_files)
  num_val = len(validation_files)

  train_annotations_path = "train_xml_paths_%d.txt" % num_train
  train_images_path = "train_image_paths_%d.txt" % num_train
  with open(train_annotations_path, "w") as f_annotations, open(train_images_path, "w") as f_images:
    for item in train_files:
      f_annotations.write(item[0] + "\n")
      f_images.write(item[1] + "\n")

  val_annotations_path = "val_xml_paths_%d.txt" % num_val
  val_images_path = "val_image_paths_%d.txt" % num_val
  with open(val_annotations_path, "w") as f_annotations, open(val_images_path, "w") as f_images:
    for item in validation_files:
      f_annotations.write(item[0] + "\n")
      f_images.write(item[1] + "\n")
