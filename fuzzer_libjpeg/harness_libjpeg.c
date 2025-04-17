#include <stdio.h>
#include <stdlib.h>
#include <jpeglib.h>
#include <setjmp.h>

// Gestion d'erreur personnalisée pour éviter exit() brutal
struct my_error_mgr {
    struct jpeg_error_mgr pub;
    jmp_buf setjmp_buffer;
};

static void my_error_exit(j_common_ptr cinfo) {
    struct my_error_mgr *err = (struct my_error_mgr *) cinfo->err;
    longjmp(err->setjmp_buffer, 1);
}

// Fonction appelée automatiquement par le moteur de fuzzing
int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    if (size < 64) return 0; // trop petit pour être un vrai JPEG

    struct jpeg_decompress_struct cinfo;
    struct my_error_mgr jerr;

    cinfo.err = jpeg_std_error(&jerr.pub);
    jerr.pub.error_exit = my_error_exit;

    if (setjmp(jerr.setjmp_buffer)) {
        jpeg_destroy_decompress(&cinfo);
        return 0;
    }

    jpeg_create_decompress(&cinfo);
    jpeg_mem_src(&cinfo, data, size);

    if (jpeg_read_header(&cinfo, TRUE) != JPEG_HEADER_OK) {
        jpeg_destroy_decompress(&cinfo);
        return 0;
    }

    jpeg_start_decompress(&cinfo);

    JSAMPARRAY buffer = (*cinfo.mem->alloc_sarray)(
        (j_common_ptr) &cinfo,
        JPOOL_IMAGE,
        cinfo.output_width * cinfo.output_components,
        1
    );

    while (cinfo.output_scanline < cinfo.output_height) {
        jpeg_read_scanlines(&cinfo, buffer, 1);
    }

    jpeg_finish_decompress(&cinfo);
    jpeg_destroy_decompress(&cinfo);
    return 0;
}