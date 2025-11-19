# cpu.py
from hardware import Register, Memory, Cache, ALU
from config import OPCODES

class CPU:
    def __init__(self):
        # Registers
        self.pc = Register("PC")
        self.ac = Register("AC")
        self.sp = Register("SP")
        self.ir = Register("IR")
        self.tir = Register("TIR")
        self.mar = Register("MAR")
        self.mbr = Register("MBR")
        
        # Hardware
        self.memory = Memory()
        self.cache = Cache(self.memory)
        self.alu = ALU()
        
        # Control State
        self.mpc = 0 # Micro Program Counter
        
        # Signals for GUI visualization
        self.signals = {
            'read_mem': False,
            'write_mem': False,
            'alu_op': None,
            'active_path': [] # List of components active
        }
        self.last_action_desc = "CPU Inicializada"

    def reset_signals(self):
        self.signals = {
            'read_mem': False,
            'write_mem': False,
            'alu_op': None,
            'active_path': []
        }

    def decode_instruction(self, ir_value):
        """
        Maps the opcode (high 4 bits of IR) to the starting MPC address
        of the corresponding microroutine.
        """
        opcode = (ir_value >> 12) & 0xF
        
        # Mapping based on Tanenbaum's MIC-1 (simplified)
        mapping = {
            0x0: 10, # LODD
            0x1: 15, # STOD
            0x2: 20, # ADDD
            0x3: 25, # SUBD
            0x4: 30, # JPOS
            0x5: 35, # JZER
            0x6: 40, # JUMP
            0x7: 45, # LOCO
            0x8: 50, # LODL
            0x9: 55, # STOL
            0xA: 60, # ADDL
            0xB: 65, # SUBL
            0xC: 70, # JNEG
            0xD: 75, # JNZE
            0xE: 80, # CALL
            0xF: 90  # PSHI/POP/etc (Special decoding needed)
        }
        
        return mapping.get(opcode, 0) # Default to 0 (reset) if unknown

    def cycle(self):
        """
        Executes ONE micro-instruction step.
        Returns True if running, False if halted (not really used here).
        """
        self.reset_signals()
        
        match self.mpc:
            # --- FETCH CYCLE (0-2) ---
            case 0:
                # MAR <- PC; MPC = 1
                self.mar.write(self.pc.read())
                self.signals['active_path'] = ['PC', 'MAR']
                self.last_action_desc = f"Busca: MAR <- PC ({self.pc.read()})"
                self.mpc = 1
                
            case 1:
                # PC <- PC + 1; MBR <- Memory[MAR]; MPC = 2
                old_pc = self.pc.read()
                self.pc.write(old_pc + 1)
                val = self.cache.read(self.mar.read())
                self.mbr.write(val)
                
                self.signals['read_mem'] = True
                self.signals['active_path'] = ['PC', 'ALU', 'PC', 'Cache', 'MBR']
                self.last_action_desc = f"Busca: PC incrementado ({old_pc}->{self.pc.read()}), MBR <- Mem[{self.mar.read()}] ({val})"
                self.mpc = 2
                
            case 2:
                # IR <- MBR; MPC = decode(IR)
                self.ir.write(self.mbr.read())
                self.signals['active_path'] = ['MBR', 'IR']
                self.last_action_desc = f"Busca: IR <- MBR ({self.mbr.read()}). Decodificando..."
                self.mpc = self.decode_instruction(self.ir.read())

            # --- LODD (Load Direct) ---
            case 10:
                addr = self.ir.read() & 0xFFF
                self.mar.write(addr)
                self.signals['active_path'] = ['IR', 'MAR']
                self.last_action_desc = f"LODD: MAR <- Endereço ({addr})"
                self.mpc = 11
            case 11:
                val = self.cache.read(self.mar.read())
                self.mbr.write(val)
                self.ac.write(val)
                self.signals['read_mem'] = True
                self.signals['active_path'] = ['Cache', 'MBR', 'AC']
                self.last_action_desc = f"LODD: AC <- Mem[{self.mar.read()}] ({val})"
                self.mpc = 0

            # --- STOD (Store Direct) ---
            case 15:
                addr = self.ir.read() & 0xFFF
                self.mar.write(addr)
                self.signals['active_path'] = ['IR', 'MAR']
                self.last_action_desc = f"STOD: MAR <- Endereço ({addr})"
                self.mpc = 16
            case 16:
                self.mbr.write(self.ac.read())
                self.cache.write(self.mar.read(), self.mbr.read())
                self.signals['write_mem'] = True
                self.signals['active_path'] = ['AC', 'MBR', 'Cache']
                self.last_action_desc = f"STOD: Mem[{self.mar.read()}] <- AC ({self.ac.read()})"
                self.mpc = 0

            # --- ADDD (Add Direct) ---
            case 20:
                addr = self.ir.read() & 0xFFF
                self.mar.write(addr)
                self.signals['active_path'] = ['IR', 'MAR']
                self.last_action_desc = f"ADDD: MAR <- Endereço ({addr})"
                self.mpc = 21
            case 21:
                val = self.cache.read(self.mar.read())
                self.mbr.write(val)
                self.signals['read_mem'] = True
                self.signals['active_path'] = ['Cache', 'MBR']
                self.last_action_desc = f"ADDD: MBR <- Mem[{self.mar.read()}] ({val})"
                self.mpc = 22
            case 22:
                old_ac = self.ac.read()
                res = self.alu.add(old_ac, self.mbr.read())
                self.ac.write(res)
                self.signals['alu_op'] = 'ADD'
                self.signals['active_path'] = ['AC', 'MBR', 'ALU', 'AC']
                self.last_action_desc = f"ADDD: AC <- {old_ac} + {self.mbr.read()} = {res}"
                self.mpc = 0

            # --- SUBD (Sub Direct) ---
            case 25:
                addr = self.ir.read() & 0xFFF
                self.mar.write(addr)
                self.last_action_desc = f"SUBD: MAR <- Endereço ({addr})"
                self.mpc = 26
            case 26:
                val = self.cache.read(self.mar.read())
                self.mbr.write(val)
                self.signals['read_mem'] = True
                self.signals['active_path'] = ['Cache', 'MBR']
                self.last_action_desc = f"SUBD: MBR <- Mem[{self.mar.read()}] ({val})"
                self.mpc = 27
            case 27:
                old_ac = self.ac.read()
                res = self.alu.sub(old_ac, self.mbr.read())
                self.ac.write(res)
                self.signals['alu_op'] = 'SUB'
                self.signals['active_path'] = ['AC', 'MBR', 'ALU', 'AC']
                self.last_action_desc = f"SUBD: AC <- {old_ac} - {self.mbr.read()} = {res}"
                self.mpc = 0

            # --- JPOS (Jump if Positive) ---
            case 30:
                jumped = False
                self.signals['active_path'] = ['AC']
                if (self.ac.read() & 0x8000) == 0:
                     self.pc.write(self.ir.read() & 0xFFF)
                     jumped = True
                     self.signals['active_path'] = ['AC', 'IR', 'PC']
                self.last_action_desc = f"JPOS: {'Pulou' if jumped else 'Não pulou'} (AC={self.ac.read()})"
                self.mpc = 0

            # --- JZER (Jump if Zero) ---
            case 35:
                jumped = False
                self.signals['active_path'] = ['AC']
                if self.ac.read() == 0:
                    self.pc.write(self.ir.read() & 0xFFF)
                    jumped = True
                    self.signals['active_path'] = ['AC', 'IR', 'PC']
                self.last_action_desc = f"JZER: {'Pulou' if jumped else 'Não pulou'} (AC={self.ac.read()})"
                self.mpc = 0

            # --- JUMP (Unconditional) ---
            case 40:
                addr = self.ir.read() & 0xFFF
                self.pc.write(addr)
                self.signals['active_path'] = ['IR', 'PC']
                self.last_action_desc = f"JUMP: PC <- {addr}"
                self.mpc = 0

            # --- LOCO (Load Constant) ---
            case 45:
                val = self.ir.read() & 0xFFF
                self.ac.write(val)
                self.signals['active_path'] = ['IR', 'AC']
                self.last_action_desc = f"LOCO: AC <- Constante {val}"
                self.mpc = 0
            
            # --- CALL (Call Subroutine) ---
            case 80:
                self.sp.write(self.sp.read() - 1)
                self.signals['active_path'] = ['SP']
                self.last_action_desc = f"CALL: Decrementa SP ({self.sp.read()})"
                self.mpc = 81
            case 81:
                self.mar.write(self.sp.read())
                self.mbr.write(self.pc.read())
                self.signals['active_path'] = ['SP', 'MAR', 'PC', 'MBR']
                self.last_action_desc = f"CALL: MAR <- SP, MBR <- PC ({self.pc.read()})"
                self.mpc = 82
            case 82:
                self.cache.write(self.mar.read(), self.mbr.read())
                self.signals['write_mem'] = True
                self.signals['active_path'] = ['MBR', 'Cache']
                self.last_action_desc = f"CALL: Salva PC na Pilha (Mem[{self.mar.read()}])"
                self.mpc = 83
            case 83:
                addr = self.ir.read() & 0xFFF
                self.pc.write(addr)
                self.signals['active_path'] = ['IR', 'PC']
                self.last_action_desc = f"CALL: PC <- Endereço Subrotina ({addr})"
                self.mpc = 0

            # --- Type F (Stack / Special) ---
            case 90:
                low_bits = self.ir.read() & 0xFFF
                if low_bits == 0x001: 
                    self.sp.write(self.sp.read() - 1)
                    self.signals['active_path'] = ['SP']
                    self.last_action_desc = "PUSH: Decrementa SP"
                    self.mpc = 91
                elif low_bits == 0x002:
                    self.mar.write(self.sp.read())
                    self.signals['active_path'] = ['SP', 'MAR']
                    self.last_action_desc = "POP: MAR <- SP"
                    self.mpc = 94
                elif low_bits == 0x003:
                    self.mar.write(self.sp.read())
                    self.signals['active_path'] = ['SP', 'MAR']
                    self.last_action_desc = "RETN: MAR <- SP"
                    self.mpc = 97
                elif low_bits == 0x004:
                    tmp = self.ac.read()
                    self.ac.write(self.sp.read())
                    self.sp.write(tmp)
                    self.signals['active_path'] = ['AC', 'SP']
                    self.last_action_desc = "SWAP: Troca AC e SP"
                    self.mpc = 0
                elif low_bits == 0x005:
                    self.sp.write(self.sp.read() + 1)
                    self.signals['active_path'] = ['SP']
                    self.last_action_desc = "INSP: Incrementa SP"
                    self.mpc = 0
                elif low_bits == 0x006:
                    self.sp.write(self.sp.read() - 1)
                    self.signals['active_path'] = ['SP']
                    self.last_action_desc = "DESP: Decrementa SP"
                    self.mpc = 0
                else:
                    self.last_action_desc = "Instrução Desconhecida"
                    self.mpc = 0

            # --- PUSH Implementation ---
            case 91:
                self.mar.write(self.sp.read())
                self.mbr.write(self.ac.read())
                self.signals['active_path'] = ['SP', 'MAR', 'AC', 'MBR']
                self.last_action_desc = "PUSH: MAR <- SP, MBR <- AC"
                self.mpc = 92
            case 92:
                self.cache.write(self.mar.read(), self.mbr.read())
                self.signals['write_mem'] = True
                self.last_action_desc = f"PUSH: Mem[{self.mar.read()}] <- AC ({self.ac.read()})"
                self.mpc = 0

            # --- POP Implementation ---
            case 94:
                val = self.cache.read(self.mar.read())
                self.mbr.write(val)
                self.signals['read_mem'] = True
                self.signals['active_path'] = ['Cache', 'MBR']
                self.last_action_desc = f"POP: MBR <- Mem[{self.mar.read()}] ({val})"
                self.mpc = 95
            case 95:
                self.ac.write(self.mbr.read())
                self.sp.write(self.sp.read() + 1)
                self.signals['active_path'] = ['MBR', 'AC', 'SP']
                self.last_action_desc = f"POP: AC <- MBR, Incrementa SP"
                self.mpc = 0

            # --- RETN Implementation ---
            case 97:
                val = self.cache.read(self.mar.read())
                self.mbr.write(val)
                self.signals['read_mem'] = True
                self.signals['active_path'] = ['Cache', 'MBR']
                self.last_action_desc = f"RETN: MBR <- Mem[{self.mar.read()}] ({val})"
                self.mpc = 98
            case 98:
                self.pc.write(self.mbr.read())
                self.sp.write(self.sp.read() + 1)
                self.signals['active_path'] = ['MBR', 'PC', 'SP']
                self.last_action_desc = f"RETN: PC <- MBR ({self.mbr.read()}), Incrementa SP"
                self.mpc = 0

            case _:
                self.last_action_desc = "Ciclo Desconhecido"
                self.mpc = 0
