CMAKE_MINIMUM_REQUIRED(VERSION 2.8)

PROJECT(darnet)

SET(CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/cmake ${CMAKE_MODULE_PATH})

if (NOT CMAKE_BUILD_TYPE)
    message(STATUS "CMAKE_BUILD_TYPE not set, default to Release")
    set(CMAKE_BUILD_TYPE Release)
endif ()

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall -Wno-unused-result -Wno-unknown-pragmas -Wfatal-errors -fPIC")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -Wall -Wno-unused-result -Wno-unknown-pragmas -Wfatal-errors -fPIC")

string(TOLOWER "${CMAKE_BUILD_TYPE}" CMAKE_BUILD_TYPE_LOWER)
if ("${CMAKE_BUILD_TYPE_LOWER}" STREQUAL "debug")
    #set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -O0 -g")
    #set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O0 -g")

    ################################################################################
    ### NOTE: must set -O4, or it will complain about error with 'cvRound' etc.
    ################################################################################
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -O4 -g")
    set(CMAKE_C_FLAGS "${CMAKE_CXX_FLAGS} -O4 -g")
else ()
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Ofast")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Ofast")
endif ()

include_directories(include src)

set(DARKNET_LIB_SRC src/gemm.c src/utils.c src/cuda.c src/deconvolutional_layer.c
                src/convolutional_layer.c src/list.c src/image.c src/activations.c
                src/im2col.c src/col2im.c src/blas.c src/crop_layer.c
                src/dropout_layer.c src/maxpool_layer.c src/softmax_layer.c src/data.c
                src/matrix.c src/network.c src/connected_layer.c src/cost_layer.c
                src/parser.c src/option_list.c src/detection_layer.c src/route_layer.c
                src/upsample_layer.c src/box.c src/normalization_layer.c src/avgpool_layer.c
                src/layer.c src/local_layer.c src/shortcut_layer.c src/logistic_layer.c
                src/activation_layer.c src/rnn_layer.c src/gru_layer.c src/crnn_layer.c
                src/demo.c src/batchnorm_layer.c src/region_layer.c src/reorg_layer.c
                src/tree.c src/ src/lstm_layer.c src/l2norm_layer.c src/yolo_layer.c)

# cuda related settings
find_package(CUDA)
if (CUDA_FOUND)
    add_definitions(-DGPU)

    set(CUDA_PROPAGATE_HOST_FLAGS OFF)
    list(APPEND CUDA_NVCC_FLAGS --compiler-options -fno-strict-aliasing -lineinfo -use_fast_math -Xptxas -dlcm=cg)
    list(APPEND CUDA_NVCC_FLAGS -gencode arch=compute_30,code=sm_30
                                -gencode arch=compute_35,code=sm_35
                                -gencode arch=compute_50,code=[sm_50,compute_50]
                                -gencode arch=compute_52,code=[sm_52,compute_52])

    #message(STATUS "CUDA_INCLUDE_DIRS: ${CUDA_INCLUDE_DIRS}")
    #message(STATUS "CUDA_LIBRARIES: ${CUDA_LIBRARIES}")
    #message(STATUS "CUDA_CUBLAS_LIBRARIES: ${CUDA_CUBLAS_LIBRARIES}")
    include_directories(${CUDA_INCLUDE_DIRS})

    find_package(CUDNN)
    if (CUDNN_FOUND)
        add_definitions(-DCUDNN)
        message(STATUS "CUDNN_INCLUDE_DIRS: ${CUDNN_INCLUDE_DIRS}")
        include_directories(CUDNN_INCLUDE_DIRS})
    endif ()

    ### including the cuda implementation source files ###
    list(APPEND DARKNET_LIB_SRC src/convolutional_kernels.cu src/deconvolutional_kernels.cu
                            src/activation_kernels.cu src/im2col_kernels.cu
                            src/col2im_kernels.cu src/blas_kernels.cu
                            src/crop_layer_kernels.cu src/dropout_layer_kernels.cu
                            src/maxpool_layer_kernels.cu src/avgpool_layer_kernels.cu)

endif ()

# OpenMP
find_package(OpenMP)
if (OpenMP_FOUND)
    #message(STATUS "OpenMP_C_FLAGS: ${OpenMP_C_FLAGS}")
    #message(STATUS "OpenMP_CXX_FLAGS: ${OpenMP_CXX_FLAGS}")
    #message(STATUS "OpenMP_EXE_LINKER_FLAGS: ${OpenMP_EXE_LINKER_FLAGS}")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${OpenMP_C_FLAGS}")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} ${OpenMP_EXE_LINKER_FLAGS}")
endif ()

# OpenCV
find_package(OpenCV)
if (OpenCV_FOUND)
    include_directories(${OpenCV_INCLUDE_DIRS})
    add_definitions(-DOPENCV)
endif ()

######################################################################################
# the static library
cuda_add_library(darknet_static STATIC ${DARKNET_LIB_SRC})
######################################################################################


######################################################################################
# the shared library
cuda_add_library(darknet_shared SHARED ${DARKNET_LIB_SRC})
if (CUDA_FOUND)
    # see https://cmake.org/cmake/help/v3.0/module/FindCUDA.html
    target_link_libraries(darknet_shared ${CUDA_LIBRARIES} ${CUDA_CUBLAS_LIBRARIES}
                                         ${CUDA_cupti_LIBRARY} ${CUDA_curand_LIBRARY}
                                         ${CUDA_cusparse_LIBRARY})
    if (CUDNN_FOUND)
        # message(STATUS "CUDNN_LIBRARIES: ${CUDNN_LIBRARIES}")
        target_link_libraries(darknet_shared ${CUDNN_LIBRARIES})
    endif ()
endif ()

if (OpenMP_FOUND)
    target_link_libraries(darknet_shared ${OpenMP_LIBRARIES})
endif ()

if (OpenCV_FOUND)
    target_link_libraries(darknet_shared ${OpenCV_LIBRARIES})
endif ()
######################################################################################


######################################################################################
# the darknet executable
set(DARKNET_SRC examples/captcha.c examples/lsd.c examples/super.c
                examples/art.c examples/tag.c examples/cifar.c
                examples/go.c examples/rnn.c examples/segmenter.c
                examples/regressor.c examples/classifier.c examples/coco.c
                examples/yolo.c examples/detector.c examples/nightmare.c
                examples/darknet.c)

cuda_add_executable(darknet ${DARKNET_SRC})

# linke the static library
target_link_libraries(darknet darknet_static)

if (CUDA_FOUND)
    # see https://cmake.org/cmake/help/v3.0/module/FindCUDA.html
    target_link_libraries(darknet ${CUDA_LIBRARIES} ${CUDA_CUBLAS_LIBRARIES}
                                  ${CUDA_cupti_LIBRARY} ${CUDA_curand_LIBRARY}
                                  ${CUDA_cusparse_LIBRARY})
    if (CUDNN_FOUND)
        # message(STATUS "CUDNN_LIBRARIES: ${CUDNN_LIBRARIES}")
        target_link_libraries(darknet ${CUDNN_LIBRARIES})
    endif ()
endif ()

if (OpenMP_FOUND)
    target_link_libraries(darknet ${OpenMP_LIBRARIES})
endif ()

if (OpenCV_FOUND)
    target_link_libraries(darknet ${OpenCV_LIBRARIES})
endif ()
######################################################################################


######################################################################################
# dynamic linked darknent executable
cuda_add_executable(darknet_dynamic_linked ${DARKNET_SRC})
target_link_libraries(darknet_dynamic_linked darknet_shared)
######################################################################################
