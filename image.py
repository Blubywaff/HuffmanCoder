from PIL import Image
import numpy as np
import math


class HeapNode:
    def __init__(self, frequency):
        self._frequency = frequency

    @property
    def frequency(self):
        return self._frequency


class HeapInternal(HeapNode):
    def __init__(self, children):
        super().__init__(children[0].frequency + children[1].frequency)
        self._left_child = children[0]
        self._right_child = children[1]

    @property
    def left_child(self):
        return self._left_child

    @property
    def right_child(self):
        return self._right_child


class HeapLeaf(HeapNode):
    def __init__(self, frequency, key):
        super().__init__(frequency)
        self._key = key

    @property
    def key(self):
        return self._key


def find_freqs(content):
    keys = {}
    for key in content:
        if key not in keys:
            keys[key] = 0
        keys[key] += 1
    return keys


def sort_add(heap, value):
    low = 0
    r = len(heap)
    while low < r:
        m = math.floor((low + r) / 2)
        if heap[m].frequency < value.frequency:
            low = m + 1
        else:
            r = m
    heap = heap[:low] + [value] + heap[low:]
    return heap


def create_tree(keys):
    lst = []

    for key in keys:
        lst = sort_add(lst, HeapLeaf(keys[key], key))

    while len(lst) > 1:
        node = HeapInternal((lst[0], lst[1]))
        del lst[0]
        del lst[0]
        lst = sort_add(lst, node)
    return lst[0]


def gen_codes(root):
    code = {}
    stack = [(root, '')]

    while len(stack) > 0:
        path = stack[-1][1]
        lc = (stack[-1][0].left_child, path + '0')
        rc = (stack[-1][0].right_child, path + '1')
        del stack[-1]
        if isinstance(lc[0], HeapLeaf):
            code[lc[0].key] = lc[1]
        else:
            stack.append(lc)
        if isinstance(rc[0], HeapLeaf):
            code[rc[0].key] = rc[1]
        else:
            stack.append(rc)
    return code


def encode(content, codes):
    return ''.join([codes[key] for key in content])


def encode_table(keys):
    freq_len = int(max([keys[key] for key in keys])).bit_length()
    key_len = int(max([key for key in keys])).bit_length()

    # Number of keys
    # Bit length of highest frequency
    # Bit length of longest key
    encoded_table = bin(len(keys))[2:].rjust(32, '0') \
                    + bin(freq_len)[2:].rjust(6, '0') \
                    + bin(key_len)[2:].rjust(6, '0')

    data = ''.join([i for key in keys for i in
                   [format(int(key), f'0{key_len}b'),
                    format(int(keys[key]), f'0{freq_len}b')]])

    return encoded_table + data


def format_bin(enc_table, bits_encoded):
    encoded = '101100011011101011111111' + enc_table + bits_encoded
    encoded = encoded.rjust((-(-len(encoded) // 8)) * 8, '0')
    return encoded


def encode_complete(content):
    keys = find_freqs(content)
    root = create_tree(keys)
    codes = gen_codes(root)
    bits_encoded = encode(content, codes)
    enc_table = encode_table(keys)
    bin_total = format_bin(enc_table, bits_encoded)
    return bin_total


# Reconstructor Functions
def decode(enc_bits, root):
    decoded = []
    node = root

    for bit in enc_bits:
        if bit == '0':
            node = node.left_child
        elif bit == '1':
            node = node.right_child
        else:
            raise ValueError("Bitsequence does not match tree!")
        if isinstance(node, HeapLeaf):
            decoded.append(node.key)
            node = root
    return decoded


def reconstruct_table(enc_table):
    i = 0
    table = {}

    entries = int(enc_table[i:i + 32], 2)
    i += 32

    num_len = int(enc_table[i:i+6], 2)
    i += 6

    key_len = int(enc_table[i:i+6], 2)
    i += 6

    for _ in range(entries):
        if len(enc_table[i:i + num_len]) == 0:
            raise ValueError("Incomplete Table")

        key_bits = enc_table[i:i + key_len]
        key = int(key_bits, 2)
        i += key_len

        num = int(enc_table[i:i + num_len], 2)
        i += num_len

        if key in table:
            raise ValueError(
                "Invalid Table: Multiple Entries for identical keys")

        table[key] = num

    return table, i


def decode_complete(encoded_bits):
    start = encoded_bits.index('1')
    encoded_bits = encoded_bits[start:]
    encoded_bits = encoded_bits[24:]
    freq_table, enc_table_len = reconstruct_table(encoded_bits)
    tree_root = create_tree(freq_table)
    encoded_bits = encoded_bits[enc_table_len:]
    return decode(encoded_bits, tree_root)


def convert_to_bmp(filename):
    Image.open(filename).save('.'.join(filename.split('.')[:-1]) + '.bmp')


if __name__ == "__main__":
    img = np.asarray(Image.open('image.jpg'))
    pixels_1d = np.reshape(img, (50246, 3))
    content = np.reshape(pixels_1d, (150738))
    encoded = encode_complete(content)
    dec = decode_complete(encoded)