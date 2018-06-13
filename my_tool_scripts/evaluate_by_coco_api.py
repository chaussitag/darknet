#!/usr/bin/env python
# coding=utf-8

import argparse
import os
import sys


if __name__ == "__main__":
    description_msg = '''\
generate·coco-style·object detection evaluation·results·for a test dataset using·COCO·evaluation·api,
based on the coco-style annotations and coco-style detection results.
'''

    parser = argparse.ArgumentParser(description=description_msg,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    help_msg = '''\
a json file contains coco-style annotations for the evaluation dataset, please refer to
http://cocodataset.org/#download for details of the annotations format (refer to '4. Annotation format')
'''
    parser.add_argument("--annotations", "-a", required=True, help=help_msg)

    result_help_msg = '''\
a json file contains the coco-style detection results for the evaluation dataset, please refer to
    http://cocodataset.org/#format for details of the result format
'''
    parser.add_argument("--results", "-r", required=True, help=result_help_msg)

    args = parser.parse_args()

    assert os.path.isfile(args.annotations), "%s does not exist" % args.annotations

    assert os.path.isfile(args.results), "%s does not exist" % args.results

    coco_api_path = "/home/daiguozhou/code/coco.git/PythonAPI"
    assert os.path.isdir(coco_api_path), "please change 'coco_api_path' in line 36 to the coco api folder in your PC"
    # sys.path.append(coco_api_path)
    sys.path.insert(0, coco_api_path)
    print(sys.path)
    import pycocotools
    from pycocotools.coco import COCO
    from pycocotools.cocoeval import COCOeval
    print(pycocotools.__file__)

    # load the ground truth for the dataset
    cocoGt = COCO(args.annotations)

    # load the detection result for the dataset
    cocoDt = cocoGt.loadRes(args.results)

    cocoEval = COCOeval(cocoGt, cocoDt, 'bbox')
    # cocoEval.params.imgIds = sorted(cocoGt.getImgIds())
    cocoEval.evaluate()
    cocoEval.accumulate()
    cocoEval.summarize()
