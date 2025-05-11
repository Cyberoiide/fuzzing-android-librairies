#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <jpeglib.h>

extern "C" int libQemuFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
    if (Size < 10 || Size > 4096) return 0;

    struct jpeg_decompress_struct cinfo;
    struct jpeg_error_mgr jerr;

    cinfo.err = jpeg_std_error(&jerr);
    jpeg_create_decompress(&cinfo);

    jpeg_mem_src(&cinfo, Data, Size);

    if (jpeg_read_header(&cinfo, TRUE) != JPEG_HEADER_OK) {
        jpeg_destroy_decompress(&cinfo);
        return 0;
    }

    jpeg_start_decompress(&cinfo);

    while (cinfo.output_scanline < cinfo.output_height) {
        uint8_t buffer[1024];
        jpeg_read_scanlines(&cinfo, (JSAMPARRAY)&buffer, 1);
    }

    jpeg_finish_decompress(&cinfo);
    jpeg_destroy_decompress(&cinfo);
    return 0;
}