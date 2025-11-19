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
        
        # Mapping based on Tanenbaum's MIC-1 (Standard)
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
                # Update Flags (Pass through ALU logic conceptually)
                self.alu.update_flags(val)
                self.signals['read_mem'] = True
                self.signals['active_path'] = ['Cache', 'MBR', 'AC']
                self.last_action_desc = f"LODD: AC <- Mem[{self.mar.read()}] ({val})"
                self.mpc = 0

            # --- LODL (Load Local) ---
            case 50:
                offset = self.ir.read() & 0xFFF
                # Simulate ALU addition: SP + offset
                addr = (self.sp.read() + offset) & 0xFFF
                self.mar.write(addr)
                self.signals['alu_op'] = 'ADD'
                self.signals['active_path'] = ['SP', 'IR', 'ALU', 'MAR']
                self.last_action_desc = f"LODL: MAR <- SP + {offset} ({addr})"
                self.mpc = 51
            case 51:
                val = self.cache.read(self.mar.read())
                self.mbr.write(val)
                self.ac.write(val)
                # Update Flags
                self.alu.update_flags(val)
                self.signals['read_mem'] = True
                self.signals['active_path'] = ['Cache', 'MBR', 'AC']
                self.last_action_desc = f"LODL: AC <- Mem[{self.mar.read()}] ({val})"
                self.mpc = 0

            # --- STOL (Store Local) ---
            case 55:
                offset = self.ir.read() & 0xFFF
                addr = (self.sp.read() + offset) & 0xFFF
                self.mar.write(addr)
                self.signals['alu_op'] = 'ADD'
                self.signals['active_path'] = ['SP', 'IR', 'ALU', 'MAR']
                self.last_action_desc = f"STOL: MAR <- SP + {offset} ({addr})"
                self.mpc = 56
            case 56:
                self.mbr.write(self.ac.read())
                self.cache.write(self.mar.read(), self.mbr.read())
                self.signals['write_mem'] = True
                self.signals['active_path'] = ['AC', 'MBR', 'Cache']
                self.last_action_desc = f"STOL: Mem[{self.mar.read()}] <- AC ({self.ac.read()})"
                self.mpc = 0

            # --- ADDL (Add Local) ---
            case 60:
                offset = self.ir.read() & 0xFFF
                addr = (self.sp.read() + offset) & 0xFFF
                self.mar.write(addr)
                self.signals['alu_op'] = 'ADD'
                self.signals['active_path'] = ['SP', 'IR', 'ALU', 'MAR']
                self.last_action_desc = f"ADDL: MAR <- SP + {offset} ({addr})"
                self.mpc = 61
            case 61:
                val = self.cache.read(self.mar.read())
                self.mbr.write(val)
                self.signals['read_mem'] = True
                self.signals['active_path'] = ['Cache', 'MBR']
                self.last_action_desc = f"ADDL: MBR <- Mem[{self.mar.read()}] ({val})"
                self.mpc = 62
            case 62:
                old_ac = self.ac.read()
                res = self.alu.add(old_ac, self.mbr.read())
                self.ac.write(res)
                self.signals['alu_op'] = 'ADD'
                self.signals['active_path'] = ['AC', 'MBR', 'ALU', 'AC']
                self.last_action_desc = f"ADDL: AC <- {old_ac} + {self.mbr.read()} = {res}"
                self.mpc = 0

            # --- SUBL (Sub Local) ---
            case 65:
                offset = self.ir.read() & 0xFFF
                addr = (self.sp.read() + offset) & 0xFFF
                self.mar.write(addr)
                self.signals['alu_op'] = 'ADD'
                self.signals['active_path'] = ['SP', 'IR', 'ALU', 'MAR']
                self.last_action_desc = f"SUBL: MAR <- SP + {offset} ({addr})"
                self.mpc = 66
            case 66:
                val = self.cache.read(self.mar.read())
                self.mbr.write(val)
                self.signals['read_mem'] = True
                self.signals['active_path'] = ['Cache', 'MBR']
                self.last_action_desc = f"SUBL: MBR <- Mem[{self.mar.read()}] ({val})"
                self.mpc = 67
            case 67:
                old_ac = self.ac.read()
                res = self.alu.sub(old_ac, self.mbr.read())
                self.ac.write(res)
                self.signals['alu_op'] = 'SUB'
                self.signals['active_path'] = ['AC', 'MBR', 'ALU', 'AC']
                self.last_action_desc = f"SUBL: AC <- {old_ac} - {self.mbr.read()} = {res}"
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
                self.signals['active_path'] = ['IR', 'MAR']
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
            # --- JPOS (Jump if Positive) ---
            case 30:
                jumped = False
                self.signals['active_path'] = ['AC'] # Visually still related to AC/Flags
                # Use ALU flags: Positive means NOT Negative and NOT Zero
                if not self.alu.n_flag and not self.alu.z_flag:
                     self.pc.write(self.ir.read() & 0xFFF)
                     jumped = True
                     self.signals['active_path'] = ['AC', 'IR', 'PC']
                self.last_action_desc = f"JPOS: {'Pulou' if jumped else 'Não pulou'} (N={self.alu.n_flag}, Z={self.alu.z_flag})"
                self.mpc = 0

            # --- JZER (Jump if Zero) ---
            # --- JZER (Jump if Zero) ---
            case 35:
                jumped = False
                self.signals['active_path'] = ['AC']
                if self.alu.z_flag:
                    self.pc.write(self.ir.read() & 0xFFF)
                    jumped = True
                    self.signals['active_path'] = ['AC', 'IR', 'PC']
                self.last_action_desc = f"JZER: {'Pulou' if jumped else 'Não pulou'} (Z={self.alu.z_flag})"
                self.mpc = 0

            # --- JNEG (Jump if Negative) ---
            # --- JNEG (Jump if Negative) ---
            case 70:
                jumped = False
                self.signals['active_path'] = ['AC']
                if self.alu.n_flag:
                     self.pc.write(self.ir.read() & 0xFFF)
                     jumped = True
                     self.signals['active_path'] = ['AC', 'IR', 'PC']
                self.last_action_desc = f"JNEG: {'Pulou' if jumped else 'Não pulou'} (N={self.alu.n_flag})"
                self.mpc = 0

            # --- JNZE (Jump if Non-Zero) ---
            # --- JNZE (Jump if Non-Zero) ---
            case 75:
                jumped = False
                self.signals['active_path'] = ['AC']
                if not self.alu.z_flag:
                    self.pc.write(self.ir.read() & 0xFFF)
                    jumped = True
                    self.signals['active_path'] = ['AC', 'IR', 'PC']
                self.last_action_desc = f"JNZE: {'Pulou' if jumped else 'Não pulou'} (Z={self.alu.z_flag})"
                self.mpc = 0

            # --- JUMP (Unconditional) ---
            case 40:
                addr = self.ir.read() & 0xFFF
                self.pc.write(addr)
                self.signals['active_path'] = ['IR', 'PC']
                self.last_action_desc = f"JUMP: PC <- {addr}"
                self.mpc = 0

            # --- LOCO (Load Constant) ---
            # --- LOCO (Load Constant) ---
            case 45:
                val = self.ir.read() & 0xFFF
                self.ac.write(val)
                self.alu.update_flags(val)
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
            # --- Type F (Stack / Special) ---
            case 90:
                # Use bits 11-8 of the 12-bit address field as discriminator
                # IR: [Opcode 4][Addr 12]
                # Addr 12: [Discriminator 4][Operand 8]
                # low_bits = IR & 0xFFF
                low_bits = self.ir.read() & 0xFFF
                sub_opcode = (low_bits >> 8) & 0xF
                operand = low_bits & 0xFF

                if sub_opcode == 0x0: # PSHI (0x000)
                    # Mem[SP-1] <- Mem[AC]; SP <- SP-1
                    self.sp.write(self.sp.read() - 1)
                    self.signals['active_path'] = ['SP']
                    self.last_action_desc = "PSHI: Decrementa SP"
                    self.mpc = 100 # Jump to PSHI routine
                
                elif sub_opcode == 0x2: # POPI (0x200)
                    # Mem[AC] <- Mem[SP]; SP <- SP+1
                    self.mar.write(self.sp.read())
                    self.signals['active_path'] = ['SP', 'MAR']
                    self.last_action_desc = "POPI: MAR <- SP"
                    self.mpc = 105 # Jump to POPI routine

                elif sub_opcode == 0x4: # PUSH (0x400)
                    self.sp.write(self.sp.read() - 1)
                    self.signals['active_path'] = ['SP']
                    self.last_action_desc = "PUSH: Decrementa SP"
                    self.mpc = 91

                elif sub_opcode == 0x6: # POP (0x600)
                    self.mar.write(self.sp.read())
                    self.signals['active_path'] = ['SP', 'MAR']
                    self.last_action_desc = "POP: MAR <- SP"
                    self.mpc = 94

                elif sub_opcode == 0x8: # RETN (0x800)
                    self.mar.write(self.sp.read())
                    self.signals['active_path'] = ['SP', 'MAR']
                    self.last_action_desc = "RETN: MAR <- SP"
                    self.mpc = 97

                elif sub_opcode == 0xA: # SWAP (0xA00)
                    tmp = self.ac.read()
                    self.ac.write(self.sp.read())
                    self.sp.write(tmp)
                    self.signals['active_path'] = ['AC', 'SP']
                    self.last_action_desc = "SWAP: Troca AC e SP"
                    self.mpc = 0

                elif sub_opcode == 0xC: # INSP (0xC00)
                    # INSP: SP <- SP + operand
                    self.sp.write(self.sp.read() + operand)
                    self.signals['active_path'] = ['SP', 'IR', 'ALU', 'SP']
                    self.last_action_desc = f"INSP: SP <- SP + {operand}"
                    self.mpc = 0

                elif sub_opcode == 0xE: # DESP (0xE00)
                    # DESP: SP <- SP - operand
                    self.sp.write(self.sp.read() - operand)
                    self.signals['active_path'] = ['SP', 'IR', 'ALU', 'SP']
                    self.last_action_desc = f"DESP: SP <- SP - {operand}"
                    self.mpc = 0
                else:
                    self.last_action_desc = f"Instrução F Desconhecida (Sub: {sub_opcode:X})"
                    self.mpc = 0

            # --- PSHI Implementation ---
            case 100:
                # Need to read Mem[AC]. So MAR <- AC
                self.mar.write(self.ac.read())
                self.signals['active_path'] = ['AC', 'MAR']
                self.last_action_desc = "PSHI: MAR <- AC"
                self.mpc = 101
            case 101:
                val = self.cache.read(self.mar.read())
                self.mbr.write(val)
                self.signals['read_mem'] = True
                self.signals['active_path'] = ['Cache', 'MBR']
                self.last_action_desc = f"PSHI: MBR <- Mem[AC] ({val})"
                self.mpc = 102
            case 102:
                # Now write MBR to Mem[SP] (SP was decremented in case 90)
                self.mar.write(self.sp.read())
                self.signals['active_path'] = ['SP', 'MAR']
                self.last_action_desc = "PSHI: MAR <- SP"
                self.mpc = 103
            case 103:
                self.cache.write(self.mar.read(), self.mbr.read())
                self.signals['write_mem'] = True
                self.signals['active_path'] = ['MBR', 'Cache']
                self.last_action_desc = f"PSHI: Mem[SP] <- MBR ({self.mbr.read()})"
                self.mpc = 0

            # --- POPI Implementation ---
            case 105:
                # MAR <- SP (done in 90). Read Mem[SP]
                val = self.cache.read(self.mar.read())
                self.mbr.write(val)
                self.signals['read_mem'] = True
                self.signals['active_path'] = ['Cache', 'MBR']
                self.last_action_desc = f"POPI: MBR <- Mem[SP] ({val})"
                self.mpc = 106
            case 106:
                # Now write MBR to Mem[AC]
                self.mar.write(self.ac.read())
                self.signals['active_path'] = ['AC', 'MAR']
                self.last_action_desc = "POPI: MAR <- AC"
                self.mpc = 107
            case 107:
                self.cache.write(self.mar.read(), self.mbr.read())
                self.sp.write(self.sp.read() + 1) # Increment SP
                self.signals['write_mem'] = True
                self.signals['active_path'] = ['MBR', 'Cache', 'SP']
                self.last_action_desc = f"POPI: Mem[AC] <- MBR ({self.mbr.read()}), Inc SP"
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
