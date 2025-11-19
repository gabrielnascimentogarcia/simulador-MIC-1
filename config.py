# config.py

# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

# Layout constants
REG_WIDTH = 160
REG_HEIGHT = 40
GAP_Y = 10

# --- THEME SYSTEM (Dracula / Dark Modern Inspired) ---

# Palette
COLOR_BG_DARK = (40, 42, 54)       # Dracula Background
COLOR_BG_PANEL = (68, 71, 90)      # Dracula Current Line / Selection
COLOR_FG_MAIN = (248, 248, 242)    # Dracula Foreground
COLOR_FG_DIM = (98, 114, 164)      # Dracula Comment
COLOR_ACCENT = (139, 233, 253)     # Dracula Cyan
COLOR_ACCENT_2 = (189, 147, 249)   # Dracula Purple
COLOR_HIGHLIGHT = (255, 184, 108)  # Dracula Orange
COLOR_ERROR = (255, 85, 85)        # Dracula Red
COLOR_SUCCESS = (80, 250, 123)     # Dracula Green
COLOR_WARNING = (241, 250, 140)    # Dracula Yellow

# Semantic Colors
THEME_BG = COLOR_BG_DARK
THEME_PANEL_BG = (30, 30, 35)      # Slightly darker for panels
THEME_PANEL_BORDER = (80, 80, 90)
THEME_TEXT_MAIN = COLOR_FG_MAIN
THEME_TEXT_DIM = COLOR_FG_DIM
THEME_TEXT_ACCENT = COLOR_ACCENT
THEME_ACCENT = COLOR_ACCENT

THEME_REGISTER_BG = (50, 50, 60)
THEME_REGISTER_BORDER = (100, 100, 120)
THEME_REGISTER_ACTIVE = (70, 70, 100) # When active in path
THEME_REGISTER_GLOW = (255, 184, 108) # Orange glow

THEME_HIGHLIGHT_PC = (60, 70, 100) # Subtle blueish background for current line
THEME_HIGHLIGHT_MEM = (80, 80, 50) # Subtle yellowish background for memory access

THEME_BUTTON_BG = (68, 71, 90)
THEME_BUTTON_HOVER = (100, 110, 130)
THEME_BUTTON_TEXT = COLOR_FG_MAIN

THEME_EDITOR_BG = (25, 25, 28)
THEME_EDITOR_GUTTER = (35, 35, 40)
THEME_EDITOR_SELECTION = (68, 71, 90)
THEME_CURSOR = (80, 250, 123) # Green neon cursor

THEME_CACHE_HIT = COLOR_SUCCESS
THEME_CACHE_MISS = COLOR_ERROR
THEME_CACHE_NONE = (60, 60, 60)

# Opcodes
OPCODES = {
    'LODD': 0x1,
    'STOD': 0x2,
    'ADDD': 0x3,
    'SUBD': 0x4,
    'JPOS': 0x5,
    'JZER': 0x6,
    'JUMP': 0x7,
    'LOCO': 0x8,
    'LODL': 0x9,
    'STOL': 0xA,
    'ADDL': 0xB,
    'SUBL': 0xC,
    'JNEG': 0xD,
    'JNZE': 0xE,
    'CALL': 0xF,
    'PSHI': 0xF, 
    'POPI': 0xF, 
    'PUSH': 0xF, 
    'POP':  0xF, 
    'RETN': 0xF, 
    'SWAP': 0xF, 
    'INSP': 0xF, 
    'DESP': 0xF  
}
