#!/usr/bin/env python3
# coding=utf-8

import argparse
import xml.etree.ElementTree as ET
import os
import sys
import shutil


class PreProcessForYolo(object):
    possible_image_suffix = [".jpg", ".png", ".jpeg", ".JPG", ".PNG", ".JPEG"]

    def __init__(self, img_set_file, categories_file, append_id=False):
        assert os.path.isfile(img_set_file), "%s does not exist" % img_set_file

        self._image_set_file = img_set_file
        self._append_id = append_id
        self._image_id = 1
        with open(categories_file, "r") as f:
            self._category_list = [line.strip() for line in f]

        self._valid_images = []
        self._valid_xml_annotations = []

    def process(self):
        with open(self._image_set_file, "r") as f:
            for line in f:
                self.process_image_path(line.strip())

        num = len(self._valid_images)
        if num > 0:
            splits = self._image_set_file.rsplit(".", 1)

            yolo_img_set_file = "%s_yolo_%d.%s" % (splits[0], num, splits[1])
            with open(yolo_img_set_file, "w") as f:
                for p in self._valid_images:
                    f.write(p + "\n")

            yolo_xml_anns_file = "%s_yolo_%d.xml" % (splits[0], num)
            with open(yolo_xml_anns_file, "w") as f:
                for p in self._valid_xml_annotations:
                    f.write(p + "\n")

    def process_image_path(self, img_path):
        xml_annotation_path = img_path.rsplit(".", 1)[0] + ".xml"
        # both the image and xml annotation files must exist
        if not os.path.isfile(img_path) or not os.path.isfile(xml_annotation_path):
            return

        yolo_annotations = self.get_yolo_annotation(xml_annotation_path)
        # ignore those have no valid annotations
        if len(yolo_annotations) < 1:
            return

        fixed_image_path = PreProcessForYolo.fix_image_name(img_path)

        if self._append_id:
            fixed_image_path = PreProcessForYolo.append_image_id(fixed_image_path, self._image_id)
            self._image_id += 1

        path_no_suffix = fixed_image_path.rsplit(".", 1)[0]

        self._valid_images.append(fixed_image_path)
        self._valid_xml_annotations.append(path_no_suffix + ".xml")

        yolo_label_path = path_no_suffix.replace("/images/", "/labels/") + ".txt"
        label_dir = yolo_label_path.rsplit("/", 1)[0]
        if not os.path.isdir(label_dir):
            os.makedirs(label_dir)

        with open(yolo_label_path, "w") as f:
            for ann in yolo_annotations:
                f.write(str(ann["class_id"]) + " " + " ".join([str(a) for a in ann["box"]]) + "\n")

    def get_yolo_annotation(self, xml_ann_path):
        assert os.path.isfile(xml_ann_path), "xml annotation file %s does not exist" % xml_ann_path

        yolo_annotations = []
        with open(xml_ann_path, "r") as f:
            tree = ET.parse(f)
            root = tree.getroot()

            size = root.find('size')
            image_w = int(size.find('width').text)
            image_h = int(size.find('height').text)

            # sometimes the width and height was 0 in the annotation file
            if image_w < 1 or image_h < 1:
                print("%s has invalid image size: width %d, height %d" % (xml_ann_path, image_w, image_h))
                return yolo_annotations

            for obj in root.iter('object'):
                difficult_node = obj.find('difficult')
                if difficult_node is not None and difficult_node.text is not None and int(difficult_node.text) == 1:
                    continue

                name_node = obj.find('name')
                # in case there's no <name> tag or the tag has empty content
                if name_node is None or name_node.text is None:
                    continue

                lower_case_class_name = name_node.text.lower()
                if lower_case_class_name not in self._category_list:
                    # print("non-listed class name %s in %s" % (lower_case_class_name, xml_ann_path))
                    continue

                cls_id = self._category_list.index(lower_case_class_name)

                xmlbox = obj.find('bndbox')
                if xmlbox is not None:
                    b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text),
                         float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
                    bb = PreProcessForYolo.convert_to_yolo_box((image_w, image_h), b)

                    yolo_annotations.append({"class_id": cls_id, "box": bb})

            return yolo_annotations

    @staticmethod
    def append_image_id(img_path, img_id):
        assert os.path.isfile(img_path), "image %s does not exist" % img_path

        img_path_splits = img_path.rsplit(".", 1)
        path_no_suffix = img_path_splits[0]
        img_suffix = "." + img_path_splits[1]

        new_path_no_suffix = "%s_%d" % (path_no_suffix, img_id)
        # rename the image
        os.rename(img_path, new_path_no_suffix + img_suffix)

        # rename the xml annotation file
        os.rename(path_no_suffix + ".xml", new_path_no_suffix + ".xml")

        return new_path_no_suffix + img_suffix

    @staticmethod
    def fix_image_name(img_path):
        assert os.path.isfile(img_path), "image %s does not exist" % img_path

        img_path_splits = img_path.rsplit(".", 1)
        path_no_suffix = img_path_splits[0]
        img_suffix = "." + img_path_splits[1]

        fixed_path = path_no_suffix
        for suffix in PreProcessForYolo.possible_image_suffix:
            fixed_path = fixed_path.replace(suffix, suffix[1:])

        if fixed_path != path_no_suffix:
            # rename the image
            os.rename(img_path, fixed_path + img_suffix)
            print("rename %s to %s" % (img_path, fixed_path + img_suffix))

            # rename the xml annotation name
            os.rename(path_no_suffix + ".xml", fixed_path + ".xml")
            print("rename %s to %s" % (path_no_suffix + ".xml", fixed_path + ".xml"))

        return fixed_path + img_suffix

    @staticmethod
    def convert_to_yolo_box(size, box):
        box_center_x = (box[0] + box[1]) / 2.0 - 1.0
        box_center_y = (box[2] + box[3]) / 2.0 - 1.0
        box_w = box[1] - box[0]
        box_h = box[3] - box[2]

        image_w = float(size[0])
        image_h = float(size[1])

        box_center_x /= image_w
        box_w /= image_w
        box_center_y /= image_h
        box_h /= image_h

        return (box_center_x, box_center_y, box_w, box_h)


def parse_args():
    description_msg = '''\
preprocess the dataset for yolo training and validation:
(1) create a yolo-format annotation text file for each image, the annotation text files are grouped into a directory
    named 'labels' which contains a subdirectory for each category:
        dataset_root
             |
             |__images
             |
             |__labels
             |     |__cat
             |     |   |___cat_1.txt
             |     |   |___cat_2.txt
             |     |   |___... ...
             |     |
             |     |__dog
             |     |   |___dog_1.txt
             |     |   |___dog_2.txt
             |     |
             |     |___... ...
             |
             |__... ...
(2) rename images have sub-string ".jpg", ".JPG", ".JPEG" or ".png" in there names, since darknet depends on these
    image suffix to guess the annotation file name;
(3) append an unique integer to the name of each image in the validation set, so that darknet can guess the id of
    an image during validataion;
(4) exclude images with invalid class name or have no bounding box annotation;
'''

    data_dir_help = '''\
the dataset root directory which has a sub-directory named 'images' holding all images and xml annotation files,
the structure of the 'images' sub-directory doesn't make sense, as long as each xml annotation file stays in the same
directory as it's corresponding image.
'''
    parser = argparse.ArgumentParser(description=description_msg, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data_dir", "-d", required=True, help=data_dir_help)
    parser.add_argument("--train_set", "-t",
                        help="path to a text file contains all training image paths, one path per-line")
    parser.add_argument("--val_set", "-v",
                        help="path to a text file contains all validation image paths, one path per-line")
    parser.add_argument("--categories_file", "-c", required=True,
                        help="path to a text file contains all the object categories, one category per-line")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if not os.path.isdir(args.data_dir):
        print("the dataset root directory %s does not exist" % args.data_dir)
        sys.exit(-1)

    if not os.path.isdir(os.path.join(args.data_dir, "images")):
        print("the dataset root directory %s must contain a sub-directory named 'images'" % args.data_dir)
        sys.exit(-1)

    if args.train_set is None and args.val_set is None:
        print("at least specify one dataset to process by using option --train_set or --val_set")
        sys.exit(-1)

    if args.train_set is not None and not os.path.isfile(args.train_set):
        print("%s does not exist" % args.train_set)
        sys.exit(-1)

    if args.val_set is not None and not os.path.isfile(args.val_set):
        print("%s does not exist" % args.val_set)
        sys.exit(-1)

    if not os.path.isfile(args.categories_file):
        print("%s does not exist" % args.categories_file)
        sys.exit(-1)

    labels_dir = os.path.join(args.data_dir, "labels")
    if os.path.isdir(labels_dir):
        shutil.rmtree(labels_dir)
    os.mkdir(labels_dir)

    if args.train_set is not None:
        train_preprocessor = PreProcessForYolo(args.train_set, args.categories_file)
        train_preprocessor.process()

    if args.val_set is not None:
        val_preprocessor = PreProcessForYolo(args.val_set, args.categories_file, append_id=True)
        val_preprocessor.process()
