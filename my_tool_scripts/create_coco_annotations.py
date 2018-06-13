#!/usr/bin/env python3
# coding=utf-8

import argparse
import json
import xml.etree.ElementTree as ET
import os
import sys


def create_categories(category_list):
    return [{"id": index + 1, "name": class_name, "supercategory": class_name}
            for index, class_name in enumerate(category_list)]


def get_dataset_info():
    return {
        "description": "object detection dataset created by tencent wuhan vision team",
        "url": "http://www.tar.qq.com",
        "version": "1.0",
        "year": 2018,
        "contributor": "tencent wuhan vision team",
        "date_created": "2018-04-16·15:05:30.357475"
    }


def get_licenses():
    return [{
        "id": 0,
        "name": "xxx",
        "url": "xxx_url"
    }, ]


class ImageInfoLoader(object):
    def __init__(self, category_list):
        self._annotation_id = 0
        self._category_list = category_list

    def load_image_info(self, image_path):
        assert os.path.isfile(image_path), "%s does not exist" % image_path

        path_without_suffix = image_path.rsplit(".", 1)[0]
        image_id = int(path_without_suffix.rsplit("_", 1)[1])

        image = {
            "id": image_id,
            "filename": image_path,
            "license": 0,
            "flickr_url": "unknown",
            "coco_url": "unknown",
            "data_captured": "2018-04-16·15:05:30.357475"
        }

        xml_annotation_path = path_without_suffix + ".xml"
        assert os.path.isfile(xml_annotation_path), "%s does not exist" % xml_annotation_path

        annotation_list = []
        with open(xml_annotation_path, "r") as annotation_file:
            tree = ET.parse(annotation_file)
            root = tree.getroot()

            size = root.find("size")
            image["width"] = int(size.find("width").text)
            image["height"] = int(size.find("height").text)

            for obj in root.iter('object'):
                difficult_node = obj.find('difficult')
                if difficult_node is not None and difficult_node.text is not None and int(difficult_node.text) == 1:
                    continue

                name_node = obj.find('name')
                if name_node is None or name_node.text is None:
                    continue
                cls_lower_case = name_node.text.lower()
                if cls_lower_case not in self._category_list:
                    continue

                self._annotation_id += 1
                cls_id = self._category_list.index(cls_lower_case)
                annotation = {
                    "id": self._annotation_id,
                    "image_id": image_id,
                    "category_id": cls_id + 1,
                    "iscrowd": 0,
                }
                xmlbox = obj.find('bndbox')
                if xmlbox is not None:
                    x1 = float(xmlbox.find('xmin').text)
                    y1 = float(xmlbox.find('ymin').text)
                    x2 = float(xmlbox.find('xmax').text)
                    y2 = float(xmlbox.find('ymax').text)
                    box_w = x2 - x1
                    box_h = y2 - y1
                    annotation["bbox"] = [x1, y1, box_w, box_h]
                    annotation["area"] = box_w * box_h
                    if annotation["area"] < 32 ** 2:
                        print("image %s has small gt box" % image_path)
                    annotation["segmentation"] = [[x1, y1, x1, y2, x2, y2, x2, y1]]
                    annotation_list.append(annotation)

        return image, annotation_list


def process_image_set(image_set_path, category_list, output_path):
    coco_annotations = {
        "info": get_dataset_info(),
        "licenses": get_licenses(),
        "images": [],
        "annotations": [],
        "categories": create_categories(category_list)
    }

    img_info_loader = ImageInfoLoader(category_list)
    with open(image_set_path, "r") as image_set_file:
        for item in image_set_file:
            # strip the ending '\n'
            image_path = item.strip()
            img, anns = img_info_loader.load_image_info(image_path)
            coco_annotations["images"].append(img)
            if len(anns) > 0:
                coco_annotations["annotations"].extend(anns)

    with open(output_path, "w") as output_file:
        json.dump(coco_annotations, output_file, ensure_ascii=False, indent=2)


def load_categories(categories_file):
    with open(categories_file, "r") as f:
        return [category.strip() for category in f]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="create coco style annotation file to use COCO-api for evaluation")
    parser.add_argument("--image_set", "-i", help="path to a text file containing all image paths for the image set",
                        required=True)
    parser.add_argument("--categories_file", dest="categories_file", required=True,
                        help="a text file contains all the object categories, one category per-line")
    parser.add_argument("--output", "-o", help="the output file path", default="annotations.json")
    args = parser.parse_args()

    if not os.path.isfile(args.image_set):
        print("%s does not exist" % args.image_set)
        sys.exit(-1)

    if not os.path.isfile(args.categories_file):
        print("%s does not exist" % args.categories_file)
        sys.exit(-1)

    all_categories = load_categories(args.categories_file)

    process_image_set(args.image_set, all_categories, args.output)
