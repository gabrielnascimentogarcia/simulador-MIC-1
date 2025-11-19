# hardware.py

class Register:
    def __init__(self, name, value=0):
        self.name = name
        self._value = value # Internal 16-bit value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        # Ensure 16-bit wrapping
        self._value = val & 0xFFFF

    def read(self):
        return self._value

    def write(self, val):
        self.value = val

class Memory:
    def __init__(self, size=4096):
        self.size = size
        self.data = [0] * size

    def reset(self):
        self.data = [0] * self.size

    def read(self, addr):
        if 0 <= addr < self.size:
            return self.data[addr]
        return 0

    def write(self, addr, val):
        if 0 <= addr < self.size:
            self.data[addr] = val & 0xFFFF

class Cache:
    def __init__(self, memory, size=16):
        self.memory = memory
        self.size = size
        # Cache lines: list of dicts {valid, tag, data}
        self.lines = [{'valid': False, 'tag': 0, 'data': 0} for _ in range(size)]
        self.last_access_type = "NONE" # "HIT" or "MISS"

    def reset(self):
        self.lines = [{'valid': False, 'tag': 0, 'data': 0} for _ in range(self.size)]
        self.last_access_type = "NONE"

    def _get_index_tag(self, addr):
        # Direct Mapping:
        # Assuming 4096 words (12 bits address)
        # Cache size 16 (4 bits index)
        # Tag = remaining bits (12 - 4 = 8 bits)
        index = addr % self.size
        tag = addr // self.size
        return index, tag

    def read(self, addr):
        index, tag = self._get_index_tag(addr)
        line = self.lines[index]

        if line['valid'] and line['tag'] == tag:
            self.last_access_type = "HIT"
            return line['data']
        else:
            self.last_access_type = "MISS"
            # Fetch from memory
            data = self.memory.read(addr)
            # Update cache
            self.lines[index] = {'valid': True, 'tag': tag, 'data': data}
            return data

    def write(self, addr, val):
        # Write-Allocate + Write-Through Policy:
        # 1. Always write to memory (Write-Through)
        self.memory.write(addr, val)
        
        # 2. Update Cache (Write-Allocate)
        # Whether it was a Hit or Miss, we bring/update the block in cache
        # so next read is a Hit.
        index, tag = self._get_index_tag(addr)
        
        # Check if it was a hit just for stats (optional, but good for visualization)
        if self.lines[index]['valid'] and self.lines[index]['tag'] == tag:
             self.last_access_type = "HIT"
        else:
             self.last_access_type = "MISS"
             
        # Update the line
        self.lines[index] = {'valid': True, 'tag': tag, 'data': val}

class ALU:
    def __init__(self):
        self.n_flag = False
        self.z_flag = False

    def update_flags(self, result):
        # Result is treated as 16-bit signed for flags usually, 
        # but here we stick to simple checks on the 16-bit unsigned result
        # If bit 15 is 1, it's negative in 2's complement
        self.z_flag = (result == 0)
        self.n_flag = (result & 0x8000) != 0

    def add(self, a, b):
        res = (a + b) & 0xFFFF
        self.update_flags(res)
        return res

    def sub(self, a, b):
        # a - b
        # In 2's complement: a + (~b + 1)
        res = (a - b) & 0xFFFF
        self.update_flags(res)
        return res

    def band(self, a, b):
        res = (a & b) & 0xFFFF
        self.update_flags(res)
        return res
    
    def inv(self, a):
        res = (~a) & 0xFFFF
        self.update_flags(res)
        return res
    
    def lshift(self, a):
        res = (a << 1) & 0xFFFF
        self.update_flags(res)
        return res
    
    def rshift(self, a):
        # Arithmetic shift right usually preserves sign, but let's do logical for simplicity unless specified
        # Tanenbaum MIC-1 usually does simple shifts.
        res = (a >> 1) & 0xFFFF
        self.update_flags(res)
        return res
