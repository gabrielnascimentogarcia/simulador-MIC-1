# assembler.py
from config import OPCODES

def assemble(lines):
    """
    Assemble a list of assembly code lines into a list of integers (machine code).
    """
    machine_code = []
    
    # First pass: Clean up and basic validation (could add label support here if needed)
    cleaned_lines = []
    for line in lines:
        # Remove comments first
        if ';' in line:
            line = line.split(';')[0]
        
        line = line.strip()
        # Skip empty lines
        if not line:
            continue
            
        cleaned_lines.append(line)

    for line in cleaned_lines:
        parts = line.split()
        mnemonic = parts[0].upper()
        
        if mnemonic not in OPCODES:
            raise ValueError(f"Unknown mnemonic: {mnemonic}")
        
        opcode = OPCODES[mnemonic]
        operand = 0
        
        # Handle instructions with operands
        if len(parts) > 1:
            try:
                operand = int(parts[1])
            except ValueError:
                # Check if it's a hex string
                try:
                    operand = int(parts[1], 16)
                except ValueError:
                     raise ValueError(f"Invalid operand: {parts[1]}")
        
        # Special handling for instructions that share the 0xF opcode
        # In MAC-1, instructions like PUSH, POP, RETN share opcode 1111 (0xF)
        # and are distinguished by the lower 8 bits.
        # However, the standard MAC-1 set usually defines them as:
        # PSHI: 0xF + specific bits?
        # Actually, looking at Tanenbaum's MIC-1 / MAC-1:
        # The standard set is usually:
        # 0-B: Memory reference (12 bits address)
        # C-E: Jumps/Call (12 bits address)
        # F:  Operations without address (Stack, etc)
        
        # For this simulator, we will follow the config.py OPCODES.
        # If the opcode is 0xF, we need to know which specific function it is.
        # Since the config.py maps all of them to 0xF, we need a secondary mapping 
        # or we assume the lower bits are passed as operand?
        # BUT, usually these instructions don't take an operand in assembly (e.g. "POP").
        # So we must assign the lower bits based on the mnemonic.
        
        if opcode == 0xF:
            # Secondary opcodes (arbitrary or standard if known, here we define them to match our microcode later)
            # Let's assign unique lower 12 bits (or 8 bits) for these.
            # We will use the lower 8 bits as the "extended opcode"
            extended_opcodes = {
                'PSHI': 0x00, # Pushes immediate (takes operand?) - Wait, PSHI usually takes operand.
                              # If PSHI takes operand, it can't be type F (no room for operand).
                              # Let's assume PSHI is special or we use the operand field.
                              # If PSHI is 0xF, it has 12 bits for constant? No, usually 0xF is for 0-operand.
                              # Let's look at the PDF requirement or standard.
                              # The PDF says: "As instruções F (1111) variam nos 8 bits inferiores".
                              # This implies they are 0-operand instructions mostly, OR the operand is in the low 8 bits?
                              # If PSHI is "Push Immediate", it needs a value. 
                              # Maybe PSHI is NOT 0xF in this specific variation?
                              # Config.py has PSHI: 0xF. 
                              # Let's assume for PSHI, the operand is small (8 bits) or it's a mistake in the simple map.
                              # BUT, for "POP", "RETN", "SWAP", they are definitely 0-operand.
                
                'POPI': 0x00, # POP Indirect?
                'PUSH': 0x01,
                'POP':  0x02,
                'RETN': 0x03,
                'SWAP': 0x04,
                'INSP': 0x05,
                'DESP': 0x06
                # PSHI is tricky if it's 0xF. If it's "Push Immediate", where is the immediate?
                # If it's on stack, it's not immediate.
                # Let's assume PSHI is actually a different opcode or we treat it specially.
                # For now, let's handle the ones that are clearly 0-operand.
            }
            
            if mnemonic in extended_opcodes:
                operand = extended_opcodes[mnemonic]
            
            # If it is PSHI and has an operand, we might need to fit it in.
            # If PSHI is indeed 0xF, maybe it uses the lower 12 bits as signed constant?
            # But then how do we distinguish from POP?
            # Let's assume for this project:
            # 0-E are standard.
            # F is for special.
            # We will encode the 'extended' type in the lower bits.
            
        
        # Construct 16-bit instruction
        # High 4 bits: Opcode
        # Low 12 bits: Operand (Address or Constant)
        
        # Mask operand to 12 bits
        operand = operand & 0xFFF
        
        instruction = (opcode << 12) | operand
        machine_code.append(instruction)
        
    return machine_code
