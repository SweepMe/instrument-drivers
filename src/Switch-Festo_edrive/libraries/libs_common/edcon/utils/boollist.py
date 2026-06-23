"""Helper functions for converting lists of boolean values"""


def bytes_to_boollist(data: bytes, num_bytes: int = None):
    """Converts data in byte representation to a list of bools"""
    # Compose list of single bytes
    chunkeddata = [data[i:i + 1] for i in range(0, len(data), 1)]
    # Compose a list of single boolean values
    boollist = sum(([int.from_bytes(chunk, 'little') >> i & 1 == 1 for i in range(
        8)] for chunk in chunkeddata), [])

    if num_bytes is None:
        num_bytes = len(data)

    if num_bytes > len(data):
        boollist += [False] * ((num_bytes - len(data)) * 8)

    boollist = boollist[:num_bytes * 8]

    return boollist


def boollist_to_bytes(boollist: list):
    """Converts a list of bools to byte representation"""
    # Compose list of chunks of 8 bools
    chunkedlist = [boollist[i:i + 8] for i in range(0, len(boollist), 8)]
    # Compose a list where every chunk is an int
    intlist = [sum(int(bit) << position for (position, bit)
                   in enumerate(chunk)) for chunk in chunkedlist]
    return bytes(intlist)
