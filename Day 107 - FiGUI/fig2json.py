import zlib
import array
import zipfile
import io
import gzip


int32 = array.array('i', [0])
uint8 = array.array('B', int32.tobytes())
uint32 = array.array('I', int32.tobytes())


def transfer_8_to_32(file_byte: bytes, start: int, cache: bytes):
    cache[0] = file_byte[start + 0]
    cache[1] = file_byte[start + 1]
    cache[2] = file_byte[start + 2]
    cache[3] = file_byte[start + 3]


def calc_end(file_byte: bytes, start: int) -> int:
    transfer_8_to_32(file_byte, start, uint8)

    return uint32[0]


def fig_to_json(file_path):
    with open(file_path, 'rb') as f:
        file_buffer = f.read()

    schemaByte, dataByte = fig_to_binary_parts(file_buffer)

    print(schemaByte)
    print(dataByte)


def fig_to_binary_parts(file_buffer):
    file_byte = bytearray(file_buffer)

    if not file_byte.startswith(b"fig-kiwi"):
        #unzipped = zipfile.ZipFile(io.BytesIO(file_buffer))
        #file_buffer = unzipped.read("canvas.fig")

        unzipped = gzip.decompress(file_buffer)
        file = unzipped["canvas.fig"]
        file_buffer = file["buffer"]
        file_byte = bytearray(file_buffer)

    start = 8
    
    calc_end(file_byte, start)
    start += 4

    result = []
    while start < len(file_byte):
        end = calc_end(file_byte, start)
        start += 4

        byte_temp = file_byte[start:start+end]

        if file_byte[start] != 137 and file_byte[start + 1] == 80:
            #byte_temp = zlib.decompress(byte_temp)
            byte_temp = zipfile.ZipFile(io.BytesIO(byte_temp)).read()

        result.append(byte_temp)
        start += end

    return result
