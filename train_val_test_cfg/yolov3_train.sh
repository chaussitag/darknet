#!/usr/bin/env bash

darknet="${HOME}/code/darknet.git/build/darknet"
DATA_FILE="${HOME}/dataset/od_tencent_wh/od_45cls_data/yolov3/yolov3-45cls-train.data"
CFG_FILE="${HOME}/dataset/od_tencent_wh/od_45cls_data/yolov3/yolov3-45cls-train.cfg"
START_WEIGHTS="${HOME}/code/darknet.git/pretrained_models/darknet53.conv.74"

echo "darknet detector train ${DATA_FILE} ${CFG_FILE} ${START_WEIGHTS}"
${darknet} detector train ${DATA_FILE} ${CFG_FILE} ${START_WEIGHTS}

