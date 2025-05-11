LOCAL_PATH := $(call my-dir)
FULL_PATH_TO_ROOTFS := /rootfs/

# Build libjpeg (static)
include $(CLEAR_VARS)
LOCAL_MODULE    := jpeg
LOCAL_SRC_FILES := libjpeg/jpeglib.c libjpeg/jidctint.c libjpeg/jmemmgr.c libjpeg/jutils.c libjpeg/jerror.c libjpeg/jdatasrc.c
LOCAL_C_INCLUDES := $(LOCAL_PATH)/libjpeg
include $(BUILD_STATIC_LIBRARY)

# Build shared fuzz target
include $(CLEAR_VARS)
LOCAL_MODULE    := libJpegFuzz
LOCAL_SRC_FILES := lib/fuzz.cpp
LOCAL_C_INCLUDES := $(LOCAL_PATH)/libjpeg $(LOCAL_PATH)/libjpeg/internal
LOCAL_STATIC_LIBRARIES := jpeg
LOCAL_LDLIBS := -lz
include $(BUILD_SHARED_LIBRARY)

# Build executable
include $(CLEAR_VARS)
LOCAL_MODULE := jpegfuzz
LOCAL_SRC_FILES := jpegfuzz.cpp
LOCAL_SHARED_LIBRARIES := libJpegFuzz
LOCAL_LDLIBS := -lz -L$(FULL_PATH_TO_ROOTFS)/system/lib64/ \
    -Wl,-rpath-link=$(FULL_PATH_TO_ROOTFS)/system/lib64/ \
    -Wl,--dynamic-linker=/rootfs/system/bin/linker64
include $(BUILD_EXECUTABLE)
