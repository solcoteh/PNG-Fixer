import binascii
import sys
import png

# Constant file header
FILE_HEADER = b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a"

# Fixed list of possible chunks
PNG_CHUNKS_TYPE = [b"IHDR", b"PLTE", b"IDAT", b"IEND", b"bKGD", b"cHRM", b"dSIG", b"eXIf", b"gAMA", b"hIST", b"iCCP", b"iTXt", b"pHYs", b"sBIT", b"sPLT", b"sRGB", b"sTER", b"tEXt", b"tIME", b"tRNS", b"zTXt"]
SPLITTER = "-----------------------"

def validate_crc(type: bytes, data: bytes, crc: bytes) -> bool:
    """Validate if the CRC is valid given a type and data"""

    print("Validating CRC...")

    c2 = binascii.crc32(type + data)
    
    if c2 == crc:
        print("Valid")
        return True
    else:
        print("Invalid")
        print("Expected :", crc)
        print("Result   :", c2)
        return False

def validate_magicbytes(data) -> int:
    """Validate that the current magicbytes are valid PNG magicbytes"""

    print("Validating magicbytes...")

    magicbytes = data[0 : len(FILE_HEADER)]

    if magicbytes == FILE_HEADER:
        print("Valid")
        return len(FILE_HEADER)
    else:
        print("Invalid")
        print("Expected :", FILE_HEADER)
        print("Result   :", magicbytes)
        return 0

def repair_magicbytes(data: bytes) -> bytes:
    """Set the PNG magicbytes to the correct value"""

    print("Repairing magicbytes")
    
    return FILE_HEADER + data[len(FILE_HEADER):]

def parse_chunks(data: bytes, offset: int):
    """Parse the chunk at a given offset"""

    chunkLength = data[offset: offset + 4]
    length = int.from_bytes(chunkLength, "big")

    chunkType = data[offset + 4 : offset + 8]
    chunkData = data[offset + 8 : offset + length + 8]
    chunkCRC = data[offset + length + 8: offset + length + 12]
    crc = int.from_bytes(chunkCRC, "big")

    print("Parsing header :", chunkType, "at offset", offset + 4)  
    print("CRC :", crc)

    if chunkType not in PNG_CHUNKS_TYPE:
        print("Type is invalid")
        return 0

    if length != len(chunkData):
        print("Length is invalid")
        return -2

    if not validate_crc(chunkType, chunkData, crc):
        print("CRC is invalid")
        return -1
    
    return offset + 8 + length + 4

def repair_chunk_type(data: bytes, offset: int) -> bytes:
    """Replace the chunk type for a given chunk"""

    part1 = data[:offset + 4]
    chunkType = data[offset + 4: offset + 8]
    part2 = data[offset + 8:]

    print("Repairing chunk type")
    print("Current type :", chunkType)
    print("Possible choices :", PNG_CHUNKS_TYPE)

    header = input("Enter the header manually or enter 0 to save and exit: ").encode()

    if header == b'0':
        save_and_exit(data)

    if len(header) != 4:
        print("Wrong header type length. Exiting.")
        exit(1)

    return part1 + header + part2

def repair_chunk_crc(content: bytes, offset: int) -> bytes:
    chunkLength = content[offset: offset + 4]
    length = int.from_bytes(chunkLength, "big")

    chunkType = content[offset + 4 : offset + 8]
    chunkData = content[offset + 8 : offset + length + 8]

    part1 = content[:offset + length + 8]
    part2 = content[offset + length + 12:]

    print("Repairing chunk CRC (Replacing old CRC by actual CRC)")
    c2 = binascii.crc32(chunkType + chunkData)
    c2 = c2.to_bytes(4, "big")

    print("New CRC :", c2)

    return part1 + c2 + part2

def repair_chunk_length(content: bytes, offset: int) -> bytes:
    part1 = content[:offset]
    part2 = content[offset + 4:]
    data = content[offset + 8:]

    index = 99999999999999999
    for t in PNG_CHUNKS_TYPE:
        i = data.find(t)
        if i != -1 and i < index:
            index = i

    print("Found another chunk, resizing...")
    index = index - 8
    index = index.to_bytes(4, "big")

    return part1 + index + part2

def parse_and_repair_magicbytes(content: bytes) -> [bytes, int]:
    new_offset = validate_magicbytes(content)
    if new_offset == 0:
        content = repair_magicbytes(content)
        print("Retrying...")
        new_offset = validate_magicbytes(content)
    return content, new_offset

def parse_and_repair_chunk(content: bytes, offset: int) -> [bytes, int]:
    new_offset = parse_chunks(content, offset)
    if new_offset == 0:
        content = repair_chunk_type(content, offset)
        print("Retrying...")
        new_offset = parse_chunks(content, offset)
    
    if new_offset == -2:
        content = repair_chunk_length(content, offset)
        print("Retrying...")
        new_offset = parse_chunks(content, offset)

    if new_offset == -1:
        content = repair_chunk_crc(content, offset)
        print("Retrying...")
        new_offset = parse_chunks(content, offset)
    return content, new_offset

def save_and_exit(content):
    """Save current content to a PNG file and exit"""
    with open(sys.argv[2], "wb") as f:
        f.write(content)
    print("File saved as", sys.argv[2])
    exit(0)

def parse():
    if len(sys.argv) != 3:
        print("Usage : png_parser.py <input.png> <output.png>")
        exit(0)

    content = None
    with open(sys.argv[1], "rb") as f:
        content = f.read()

    content, offset = parse_and_repair_magicbytes(content)
    print(SPLITTER)

    while offset + 1 != len(content):
        content, offset = parse_and_repair_chunk(content, offset)
        print(SPLITTER)

    print("Done fixing, writing output image to", sys.argv[2])

    with open(sys.argv[2], "wb") as f:
        f.write(content)

if __name__ == "__main__":
    parse()
