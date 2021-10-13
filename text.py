import math


class HeapNode():
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


def find_freqs(message):
    chars = {}
    for character in message:
        if character not in chars:
            chars[character] = 0
        chars[character] += 1
    return chars


def sort_add(heap, value):
    l = 0
    r = len(heap)
    while l < r:
        m = math.floor((l + r) / 2)
        if heap[m].frequency < value.frequency:
            l = m + 1
        else:
            r = m
    heap = heap[:l] + [value] + heap[l:]
    return heap


def create_tree(chars):
    lst = []

    for key in chars:
        lst = sort_add(lst, HeapLeaf(chars[key], key))

    while len(lst) > 1:
        node = HeapInternal((lst[0], lst[1]))
        del lst[0]
        del lst[0]
        lst = sort_add(lst, node)
    return lst[0]


def gen_codes(chars_root):
    code = {}
    stack = [(chars_root, '')]

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


def encode(message, codes):
    return ''.join([codes[char] for char in message])


def encode_table(chars):
    encoded_table = ''
    for char in chars:
        encoded_table += ''.join([bin(byte)[2:].rjust(8, '0') for byte in bytearray(char, 'utf8')])
        encoded_table += format(chars[char], '032b')
    return encoded_table


def format_bin(enc_table, bits_encoded):
    complete_message = '101100011011101011111111' + enc_table + '111110' + bits_encoded
    complete_message = complete_message.rjust((-(-len(complete_message) // 8)) * 8, '0')
    return complete_message


def encode_complete(message):
    chars = find_freqs(message)
    root = create_tree(chars)
    codes = gen_codes(root)
    bits_encoded = encode(message, codes)
    enc_table = encode_table(chars)
    bin_total = format_bin(enc_table, bits_encoded)
    return bin_total


## Reconstructor Functions
def decode(message, chars_root):
    decoded = ''
    node = chars_root

    for bit in message:
        if bit == '0':
            node = node.left_child
        elif bit == '1':
            node = node.right_child
        else:
            raise ValueError("Bitsequence does not match tree!")
        if isinstance(node, HeapLeaf):
            decoded += node.key
            node = chars_root
    return decoded


def reconstruct_table(enc_table):
    i = 0
    table = {}
    while True:
        if len(enc_table[i:i + 32]) == 0:
            break

        utf_char_len = 8 * max(1, len(enc_table[i:i + 8].split('0')[0]))
        if utf_char_len > 32:
            break
        utf_char_bits = enc_table[i:i + utf_char_len]
        char = int(utf_char_bits, 2).to_bytes((len(utf_char_bits) + 7) // 8, byteorder='big').decode('utf-8')

        i += utf_char_len

        num = int(enc_table[i:i + 32], 2)
        i += 32

        table[char] = num
    return (table, i)


def decode_complete(encoded_bits):
    start = encoded_bits.index('1')
    encoded_bits = encoded_bits[start:]
    encoded_bits = encoded_bits[24:]
    freq_table, enc_table_len = reconstruct_table(encoded_bits)
    tree_root = create_tree(freq_table)
    encoded_bits = encoded_bits[enc_table_len + 6:]
    return decode(encoded_bits, tree_root)


def write_bits_file(filename, bits):
    with open(filename, 'wb') as file:
        return file.write((int(bits, 2)).to_bytes(-((-len(bits)) // 8), 'big'))


def read_bits_file(filename):
    with open(filename, 'rb') as file:
        bytes = file.read()
        bits = bin(int.from_bytes(bytes, 'big'))
        return bits[2:]


def read_file(filename):
    bits = read_bits_file(filename)
    bytes = int(bits, 2).to_bytes((len(bits) + 7) // 8, 'big')
    text = bytes.decode('utf-8')
    return text


def write_file(filename, write):
    with open(filename, 'w') as file:
        return file.write(write)


if __name__ == "__main__":

    menu_top_lvl = "-Blubywaff's Text Coder-" \
                   "\n1. Read Text File" \
                   "\n2. Write Text File" \
                   "\n3. Encode Text File" \
                   "\n4. Decode File" \
                   "\n5. Read Encoded File" \
                   "\n0. Exit" \
                   "\nAction? "

    fread_prompt = "File to read (empty to cancel)? "
    fwrite_prompt = "File to write (empty to cancel)? "

    while True:
        try:
            user = int(input(menu_top_lvl))
        except ValueError:
            continue
        if user == 0:
            break
        elif user == 1:
            filename = input(fread_prompt)
            if filename == "":
                continue
            print(read_file(filename))
        elif user == 2:
            content = input("content?\n")
            filename = input(fwrite_prompt)
            if filename == "":
                continue
            print(f"Wrote {write_file(filename, content)} bytes to file '{filename}'")
        elif user == 3:
            fileread = input(fread_prompt)
            filewrite = input(fwrite_prompt)
            if fileread == "" or filewrite == "":
                continue
            read = read_file(fileread)
            bits = encode_complete(read)
            print(f"Read {len(read)} bytes from file '{fileread}' "
                  f"and wrote {write_bits_file(filewrite, bits)} to file '{filewrite}'")
        elif user == 4:
            fileread = input(fread_prompt)
            filewrite = input(fwrite_prompt)
            if fileread == "" or filewrite == "":
                continue
            bits = read_bits_file(fileread)
            text = decode_complete(bits)
            print(f"Read {len(bits) / 8} bytes from file '{fileread}' "
                  f"and wrote {write_file(filewrite, text)} bits to file '{filewrite}'")
        elif user == 5:
            filename = input(fread_prompt)
            if filename == "":
                continue
            bits = read_bits_file(filename)
            text = decode_complete(bits)
            print(text)


    def err_test():
        import time

        text = read_file('shake.txt')

        start = time.time_ns()
        decode_complete(encode_complete(text))
        print(start - time.time_ns())

        write_bits_file('text.b1baff', encode_complete(text))
        decode_complete(read_bits_file('text.b1baff'))