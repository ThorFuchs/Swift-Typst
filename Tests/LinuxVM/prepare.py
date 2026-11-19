"""Extract the Alpine ARM64 kernel and build a minimal initramfs for a smoke test."""

import gzip
import os
import stat
import subprocess
import sys
import zlib

iso, init, binary, output_dir = sys.argv[1:]
wrapped = subprocess.check_output(["bsdtar", "-xOf", iso, "boot/vmlinuz-virt"])
images = []
offset = 0
while (offset := wrapped.find(b"\x1f\x8b\x08", offset)) >= 0:
    try:
        decoder = zlib.decompressobj(31)
        image = decoder.decompress(wrapped[offset:]) + decoder.flush()
        if len(image) > 1_000_000 and image[56:60] == b"ARM\x64":
            images.append(image)
    except zlib.error:
        pass
    offset += 1
if len(images) != 1:
    raise SystemExit(f"Expected one ARM64 Linux image, found {len(images)}")
with open(os.path.join(output_dir, "Image"), "wb") as kernel:
    kernel.write(images[0])

with gzip.open(os.path.join(output_dir, "initramfs.gz"), "wb", compresslevel=1) as out:
    def entry(name, mode, path=None, rmajor=0, rminor=0):
        size = os.path.getsize(path) if path else 0
        encoded = name.encode() + b"\0"
        fields = [1, mode, 0, 0, 1, 0, size, 0, 0, rmajor, rminor, len(encoded), 0]
        header = b"070701" + b"".join(f"{field:08x}".encode() for field in fields)
        out.write(header + encoded)
        out.write(b"\0" * (-(len(header) + len(encoded)) % 4))
        if path:
            with open(path, "rb") as source:
                while chunk := source.read(1024 * 1024):
                    out.write(chunk)
        out.write(b"\0" * (-size % 4))

    entry("dev", stat.S_IFDIR | 0o755)
    entry("proc", stat.S_IFDIR | 0o555)
    entry("dev/console", stat.S_IFCHR | 0o600, rmajor=5, rminor=1)
    entry("init", stat.S_IFREG | 0o755, init)
    entry("Consumer", stat.S_IFREG | 0o755, binary)
    entry("TRAILER!!!", 0)
