# assembler.py
from config import OPCODES

def assemble(lines):
    """
    Assemble a list of assembly code lines into a list of integers (machine code).
    Supports Labels (e.g. "LOOP: JUMP LOOP") using a two-pass approach.
    """
    
    # --- Pass 1: Symbol Table Generation ---
    symbol_table = {}
    cleaned_lines = [] # Lines without labels and comments
    
    current_address = 0
    
    for line in lines:
        # 1. Remove comments
        if ';' in line:
            line = line.split(';')[0]
        
        line = line.strip()
        if not line:
            continue
            
        # 2. Check for Label
        if ':' in line:
            parts = line.split(':')
            label = parts[0].strip().upper()
            instruction_part = parts[1].strip()
            
            # Register label
            if label in symbol_table:
                raise ValueError(f"Duplicate label: {label}")
            symbol_table[label] = current_address
            
            # If there is code after label, keep it
            if instruction_part:
                cleaned_lines.append(instruction_part)
                current_address += 1
            # If line ends with label (e.g. "LOOP:"), don't increment address yet, 
            # next line will be at this address.
        else:
            cleaned_lines.append(line)
            current_address += 1

    # --- Pass 2: Code Generation ---
    machine_code = []
    
    for line in cleaned_lines:
        parts = line.split()
        mnemonic = parts[0].upper()
        
        if mnemonic not in OPCODES:
            raise ValueError(f"Unknown mnemonic: {mnemonic}")
        
        opcode = OPCODES[mnemonic]
        operand_val = 0
        
        # Handle operands
        REQUIRES_OPERAND = {
            'LODD', 'STOD', 'ADDD', 'SUBD', 
            'JPOS', 'JZER', 'JUMP', 'LOCO', 
            'LODL', 'STOL', 'ADDL', 'SUBL', 
            'JNEG', 'JNZE', 'CALL'
        }

        if len(parts) > 1:
            operand_str = parts[1]
            
            # Check if operand is a Label
            if operand_str.upper() in symbol_table:
                operand_val = symbol_table[operand_str.upper()]
            else:
                # Try numeric
                try:
                    if operand_str.startswith('0x'):
                        operand_val = int(operand_str, 16)
                    else:
                        operand_val = int(operand_str)
                except ValueError:
                    raise ValueError(f"Invalid operand: {operand_str}")
        elif mnemonic in REQUIRES_OPERAND:
             raise ValueError(f"Syntax Error: The instruction '{mnemonic}' requires an operand.")
        
        # Handle Special Opcodes (0xF)
        if opcode == 0xF:
            extended_opcodes = {
                'PSHI': 0x00, # Placeholder if needed
                'POPI': 0x00, 
                'PUSH': 0x01,
                'POP':  0x02,
                'RETN': 0x03,
                'SWAP': 0x04,
                'INSP': 0x05,
                'DESP': 0x06
            }
            if mnemonic in extended_opcodes:
                operand_val = extended_opcodes[mnemonic]
        
        # Construct 16-bit instruction
        # Mask operand to 12 bits
        operand_val = operand_val & 0xFFF
        instruction = (opcode << 12) | operand_val
        machine_code.append(instruction)
        
    return machine_code
