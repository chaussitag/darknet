#!/usr/bin/env bash

darknet="${HOME}/code/darknet.git/build/darknet"
DATA_FILE="${HOME}/dataset/od_tencent_wh/od_45cls_data/yolov3/yolov3-45cls-train-stage2.data"
CFG_FILE="${HOME}/dataset/od_tencent_wh/od_45cls_data/yolov3/yolov3-45cls-train-stage2.cfg"
#START_WEIGHTS="${HOME}/code/darknet.git/pretrained_models/darknet53.conv.74"
START_WEIGHTS="${HOME}/dataset/od_tencent_wh/od_45cls_data/yolov3/dagz_45cls_yolov3_saved_weights/yolov3-45cls-train_final.weights"

echo "darknet detector train ${DATA_FILE} ${CFG_FILE} ${START_WEIGHTS}"
${darknet} detector train ${DATA_FILE} ${CFG_FILE} ${START_WEIGHTS}

