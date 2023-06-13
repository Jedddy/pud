from pathlib import Path


def parse_bytes(byte_cnt: int) -> str:
    """Parses byte count to a human readable format."""

    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']

    i = 0

    while byte_cnt > 1024:
        byte_cnt /= 1024
        i += 1

    return f"{byte_cnt:.1f}{units[i]}"


def get_dir_size(directory: Path) -> str:
    """Gets the total directory size."""

    size = 0

    for item in directory.iterdir():
        if item.is_file():
            stat = item.stat()
            size += stat.st_size
        else:
            size += get_dir_size(item)

    return size
