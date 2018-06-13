#!/usr/bin/env python3
# coding=utf-8

import argparse
import json
import os
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="fix category id of the darknet generated coco-style validation result")
    parser.add_argument("--input_path", "-i", required=True,
                        help="path to the darknet generated result file, \
the file contains a json list of which each element was a detected box")
    parser.add_argument("--output_path", "-o", required=False, help="path to the output result file")
    args = parser.parse_args()

    if not os.path.isfile(args.input_path):
        print("%s does not exist" % args.input_path)
        sys.exit(-1)

    # the darknet used coco-ids, see definition of 'static int coco_ids[]' at the top of
    # https://github.com/pjreddie/darknet/blob/master/examples/detector.c
    darknet_coco_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 27, 28,
                        31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55,
                        56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 67, 70, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 84,
                        85, 86, 87, 88, 89, 90]

    fixed_id_map = {v: i+1 for i, v in enumerate(darknet_coco_ids)}

    output_path = args.output_path
    if output_path is None:
        input_path_splits = args.input_path.rsplit(".", 1)
        output_path = input_path_splits[0] + "_fixed" + "." + input_path_splits[1]

    with open(args.input_path, "r") as input_file:
        detection_list = json.load(input_file)
        for detection in detection_list:
            c_id = detection["category_id"]
            detection["category_id"] = fixed_id_map[c_id]

    with open(output_path, "w") as output_file:
        json.dump(detection_list, output_file, ensure_ascii=False, indent=2)
