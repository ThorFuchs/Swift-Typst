"""Exact-byte archive checks; absence of transformed data is not implied."""
import mmap


def verify_font_bytes(archive_path, excluded, included):
    """Check mappings of font names to bytes against one archive."""
    with archive_path.open("rb") as file, mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as archive:
        for name, data in excluded.items():
            if archive.find(data) >= 0:
                raise ValueError(f"Excluded font bytes found in archive: {name}")
        for name, data in included.items():
            if archive.find(data) < 0:
                raise ValueError(f"Expected STIX font bytes not found: {name}")
