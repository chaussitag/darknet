#!/usr/bin/env bash

darknet="${HOME}/code/darknet.git/build/darknet"

DATASET_DIR=${HOME}/dataset
DATA_FILE="${DATASET_DIR}/od_tencent_wh/od_45cls_data/yolov3/yolov3-45cls-validation.data"
CFG_FILE="${DATASET_DIR}/od_tencent_wh/od_45cls_data/yolov3/yolov3-45cls-test.cfg"
START_WEIGHTS="${DATASET_DIR}/od_tencent_wh/od_45cls_data/yolov3/dagz_45cls_yolov3_saved_weights/yolov3-45cls-train_final.weights"

# run yolo validation
echo "darknet detector -out yolov3_validataion_coco_results_45cls valid ${DATA_FILE} ${CFG_FILE} ${START_WEIGHTS}"
${darknet} detector -out yolov3_validataion_coco_results_45cls valid ${DATA_FILE} ${CFG_FILE} ${START_WEIGHTS}

TOOLS_DIR=${DATASET_DIR}/od_tencent_wh/my_tool_scripts

OD_45CLS_DIR=${DATASET_DIR}/od_tencent_wh/od_45cls_data
# fix the category id of the validation result
${TOOLS_DIR}/tools_for_yolo/fix_yolo_coco_result.py -i ${OD_45CLS_DIR}/yolov3/yolov3_validataion_coco_results_45cls.json

# output mAP and mAR using coco-api
${TOOLS_DIR}/evaluate_by_coco_api.py -a ${OD_45CLS_DIR}/val_set_coco_annotations_2653.json -r ${OD_45CLS_DIR}/yolov3/yolov3_validataion_coco_results_45cls_fixed.json

