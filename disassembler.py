import sys

f = open("reverse_my_vm.vmr", "rb")

registers = [0]*8

registers_index = [0, 1, 2, 3, 4, 5, 15, 18]

class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def is_empty(self):
        return len(self.items) == 0

stack = Stack()

def jump(f, byte):
    pos = registers[6]
    registers[6] += 1
    offset = int.from_bytes(f.read(1), sys.byteorder, signed=True)
    if (registers[0] != 0):
        for i in range(offset-1):
            f.read(1)
            registers[6] += 1
    else:
        for i in range(3):
            f.read(1)
            registers[6] += 1
    print(f"{pos} : {hex(ord((byte)))} {hex(offset)}      : jnz($0) {offset+registers[6]}")

def movc(f, byte):
    pos = registers[6]
    registers[6] += 1
    arg1 = f.read(1)
    arg2 = f.read(1)
    index_of_register = ord(arg1) - 0x41
    for i in range(len(registers)):
        if index_of_register == registers_index[i]:
            registers[i] = ord(arg2)
            print(f"{pos} : {hex(ord((byte)))} {hex(ord((arg1)))} {hex(ord((arg2)))} : movc ${registers_index.index(index_of_register)}, #{registers[i]}")
            f.read(1)
            registers[6] += 1
            f.read(1)
            registers[6] += 1
            f.read(1)
            registers[6] += 1
            break
    
def puts(f, byte):
    pos = registers[6]
    registers[6] += 1
    print(f"{pos}: {hex(ord((byte)))}          : puts($0)")

def getline(f, byte):
    pos = registers[6]
    registers[6] += 1
    registers[7] -= registers[1]
    for e in "INPUT": 
        stack.push(e)
        registers[7] += 1
    print(f"{pos} : {hex(ord((byte)))} : getline() (Input pushed to stack) ($1 = {registers[1]})")
    ##print(f"\t\tStack : {stack.items}")

def andl(f, byte):
    pos = registers[6]
    registers[6] += 1
    arg1 = f.read(1)
    arg2 = f.read(1)
    r1 = ord(arg1)-0x41
    r2 = ord(arg2)-0x41
    registers[6] += 1
    registers[6] += 1
    i = registers_index.index(r1)
    registers[i] = r1 & r2
    print(f"{pos} : {hex(ord((byte)))} {hex(ord((arg1)))} {hex(ord((arg2)))} : andl ${i}, ${registers_index.index(r2)}")
    

def call(f, byte):
    pos = registers[6]
    registers[6] += 1
    temp_string = []
    arg1 = f.read(1)
    size_of_memory = ord(arg1)
    registers[6] += 1
    temp_str = ""
    instruction_string = ""
    temp_arg = 0
    for i in range(size_of_memory):
        temp_arg = f.read(1)
        instruction_string += temp_arg.decode() + " "
        temp_str += chr(temp_arg[0])
        registers[6] += 1
    print(f"{pos} : {hex(ord((byte)))} {hex((size_of_memory))} {instruction_string} : call {temp_str}")
    
def ret(f, byte):
    pos = registers[6]
    registers[6] += 1
    print("ret")

def add(f, byte):
    pos = registers[6]
    registers[6] += 1
    arg1 = f.read(1)
    arg2 = f.read(1)
    r1 = ord(arg1)-0x41
    r2 = ord(arg2)-0x41
    registers[6] += 1
    registers[6] += 1
    i = registers_index.index(r1)
    registers[i] = r1 + r2
    print(f"{pos} : {hex(ord(byte))} {hex(ord(arg1))} {hex(ord(arg2))} : add ${registers_index.index(r1)}, ${registers_index.index(r2)}")

def sub(f, byte):
    pos = registers[6]
    registers[6] += 1
    arg1 = f.read(1)
    arg2 = f.read(1)
    r1 = ord(arg1)-0x41
    r2 = ord(arg2)-0x41
    registers[6] += 1
    registers[6] += 1
    i = registers_index.index(r1)
    registers[i] = r1 - r2
    print(f"{pos} : {hex(ord(byte))} {hex(ord(arg1))} {hex(ord(arg2))} : sub ${registers_index.index(r1)}, ${registers_index.index(r2)}")


def exit_routine(f, byte):
    pos = registers[6]
    registers[6] += 1
    print(f"{pos} : {hex(ord(byte))} : exit_routine")

def inc_ic(f, byte):
    pos = registers[6]
    registers[6] += 1
    print(f"{pos} : {hex(ord(byte))} : inc_ic")

def fopen(f, byte):
    pos = registers[6]
    registers[6] += 1
    print(f"{pos} : {hex(ord(byte))} : fopen")

def mov(f, byte):
    pos = registers[6]
    registers[6] += 1
    arg1 = f.read(1)
    arg2 = f.read(1)
    r1 = ord(arg1)-0x41
    r2 = ord(arg2)-0x41
    registers[6] += 1
    registers[6] += 1
    i = registers_index.index(r1)
    registers[i] = registers[registers_index.index(r2)]
    print(f"{pos} : {hex(ord(byte))} {hex(ord(arg1))} {hex(ord(arg2))} : mov ${registers_index.index(r1)}, ${registers_index.index(r2)}")

def pop(f, byte):
    pos = registers[6]
    registers[6] += 1
    arg1 = f.read(1)
    r1 = ord(arg1)-0x41
    registers[registers_index.index(r1)] = stack.pop()
    registers[6] += 1
    print(f"{pos} : {hex(ord(byte))} {hex(ord(arg1))}      : pop ${registers_index.index(r1)}")
    #print(f"\t\tStack : {stack.items}")

def push(f, byte):
    pos = registers[6]
    registers[6] += 1
    arg1 = f.read(1)
    r1 = ord(arg1)-0x41
    for e in registers[registers_index.index(r1)]:
        stack.push(e)
    registers[6] += 1
    print(f"{pos} : {hex(ord(byte))} {hex(ord(arg1))}      : push ${registers_index.index(r1)} ()")
    #print(f"\t\tStack : {stack.items}")

def xorl(f, byte):
    pos = registers[6]
    registers[6] += 1
    arg1 = f.read(1)
    registers[6] += 1
    r1 = ord(arg1)-0x41
    arg2 = f.read(1)
    registers[6] += 1
    r2 = ord(arg2)-0x41
    i = registers_index.index(r1)
    j = registers_index.index(r2)
    registers[i] = registers[j]
    print(f"{pos} : {hex(ord(byte))} {hex(ord(arg1))} {hex(ord(arg2))} : xorl ${i}, ${j}")

def push_n_sized_memory_to_stack(f, byte):
    
    pos = registers[6]
    registers[6] += 1
    temp_stack = []
    size_of_memory = ord(f.read(1))
    f.read(1)
    registers[6] += 1
    f.read(1)
    registers[6] += 1
    f.read(1)
    registers[6] += 1
    for i in range(size_of_memory):
        #stack.push(chr(f.read(1)[0]))
        temp_stack.append(chr(f.read(1)[0]))
        registers[6] += 1
    
    
    print(f"{pos} : {hex(ord(byte))} {hex(size_of_memory)} []   : push_n_sized_memory_to_stack {size_of_memory} {temp_stack}")
    #print(f"\t\tStack : {stack.items}")


actions = {
    b'\x21': jump,
    b'\x23': movc,
    b'\x24': puts,
    b'\x25': getline,
    b'\x26': andl,
    b'\x28': call,
    b'\x29': ret,
    b'\x2b': add,
    b'\x2d': sub,
    b'\x2e': exit_routine,
    b'\x20': inc_ic,
    b'\x2f': fopen,
    b'\x3a': mov,
    b'\x3c': pop,
    b'\x3e': push,
    b'\x5e': xorl,
    b'\x7c': push_n_sized_memory_to_stack,
}


def search_for_function(f, string):
    while True:
        byte = f.read(1)
        if not byte:
            break
    
        if byte == b'\x01':
            size = f.read(1)
        
        if not size:
            break

        string_bytes = f.read(ord(size))
        if not string_bytes:
            break

        string_decoded = string_bytes.decode()

        if string_decoded == string:

            next_byte = f.read(1)
            if next_byte == b'\x02':
                return f.tell()

    return None


def parse_file_byte_by_byte(f, actions):
    print("\nRegisters $0, $1, $2, $3, $4, $5 are storage. $6 is IC, $7 is SP\n")
    byte = f.read(1)
    while byte:
        if byte in actions:
            actions[byte](f, byte)
        byte = f.read(1)
    print("\n\n")


registers[6] = search_for_function(f, "main")
parse_file_byte_by_byte(f , actions)