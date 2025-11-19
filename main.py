# main.py
import pygame
import sys
from cpu import CPU
from hardware import Memory, Cache
from gui import GUI
from assembler import assemble
from config import COLOR_CACHE_HIT, COLOR_CACHE_MISS, COLOR_TEXT

def main():
    # 1. Initialize Components
    cpu = CPU()
    gui = GUI()
    
    # 2. Initial Setup
    # We don't load code automatically anymore, we wait for user to click LOAD
    gui.status_message = "Bem-vindo! Digite o codigo e clique em CARREGAR."

    # 3. Main Loop
    running = True
    auto_run = False
    
    while running:
        # Handle Input
        action = gui.handle_events()

        if action == "QUIT":
            running = False
        elif action == "STEP":
            cpu.cycle()
        elif action == "RUN":
            auto_run = not auto_run
        elif action == "RESET":
            # Reset CPU state
            cpu = CPU()
            # Reload current memory from last successful assembly
            # Or just clear it? Let's clear it and wait for Load
            cpu.memory = Memory() # Clear memory
            cpu.cache = Cache(cpu.memory)
            auto_run = False
            gui.status_message = "Reiniciado. Clique em CARREGAR."
            gui.status_color = COLOR_TEXT

        elif action == "LOAD":
            # Get code from editor
            code_lines = gui.editor.get_text()
            try:
                machine_code = assemble(code_lines)
                # Clear and Load Memory
                cpu = CPU() # Reset CPU
                for i, code in enumerate(machine_code):
                    cpu.memory.write(i, code)
                
                gui.status_message = "Codigo Carregado com Sucesso!"
                gui.status_color = COLOR_CACHE_HIT # Green
                auto_run = False
            except Exception as e:
                gui.status_message = f"Erro: {str(e)}"
                gui.status_color = COLOR_CACHE_MISS # Red
            
        if auto_run:
            cpu.cycle()
            
        # Draw
        gui.draw_cpu(cpu)
        gui.clock.tick(10 if auto_run else 30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
