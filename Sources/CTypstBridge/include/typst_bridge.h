#ifndef SWIFT_TYPST_BRIDGE_H
#define SWIFT_TYPST_BRIDGE_H
#include <stddef.h>
#include <stdint.h>

typedef struct SwiftTypstResult SwiftTypstResult;

/* Buffers are borrowed for the call. The result and its buffers are Rust-owned. */
SwiftTypstResult *swift_typst_compile(
    const uint8_t *request, size_t request_len,
    const uint8_t *blob, size_t blob_len
);
const uint8_t *swift_typst_pdf_data(const SwiftTypstResult *result);
size_t swift_typst_pdf_length(const SwiftTypstResult *result);
const uint8_t *swift_typst_metadata_data(const SwiftTypstResult *result);
size_t swift_typst_metadata_length(const SwiftTypstResult *result);
void swift_typst_result_free(SwiftTypstResult *result);
#endif
