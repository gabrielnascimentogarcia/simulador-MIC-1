# config.py

# MAC-1 Instruction Set Architecture Opcodes
OPCODES = {
    'LODD': 0x0, 'STOD': 0x1, 'ADDD': 0x2, 'SUBD': 0x3,
    'JPOS': 0x4, 'JZER': 0x5, 'JUMP': 0x6, 'LOCO': 0x7,
    'LODL': 0x8, 'STOL': 0x9, 'ADDL': 0xA, 'SUBL': 0xB,
    'JNEG': 0xC, 'JNZE': 0xD, 'CALL': 0xE, 'PSHI': 0xF,
    'POPI': 0xF, 'PUSH': 0xF, 'POP': 0xF, 'RETN': 0xF,
    'SWAP': 0xF, 'INSP': 0xF, 'DESP': 0xF
}

# Colors (RGB)
COLOR_BACKGROUND = (30, 30, 30)      # Dark Gray
COLOR_REGISTER = (50, 50, 50)        # Slightly lighter gray
COLOR_REGISTER_BORDER = (200, 200, 200) # White-ish
COLOR_TEXT = (255, 255, 255)         # White
COLOR_ACCENT = (0, 255, 0)           # Green (Active)
COLOR_INACTIVE = (100, 100, 100)     # Gray (Inactive lines)
COLOR_HIGHLIGHT = (255, 215, 0)      # Gold (Special highlight)
COLOR_CACHE_HIT = (0, 200, 0)        # Green
COLOR_CACHE_MISS = (200, 0, 0)       # Red

# Screen Settings
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Layout Constants
REG_WIDTH = 160
REG_HEIGHT = 40
GAP_Y = 20
