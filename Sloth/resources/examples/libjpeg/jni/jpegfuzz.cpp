#include "lib/fuzz.h"

int main(int argc, char** argv) {
    const uint8_t data = 0;
    libQemuFuzzerTestOneInput(&data, 1);
    return 0;
}
