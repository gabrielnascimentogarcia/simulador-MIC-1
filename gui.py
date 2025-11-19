import pygame
from config import *

class Button:
    def __init__(self, x, y, w, h, text, action_name):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action_name = action_name
        self.color = (70, 70, 70)
        self.hover_color = (100, 100, 100)
        self.text_color = COLOR_TEXT
        self.font = pygame.font.SysFont("Arial", 14, bold=True)

    def draw(self, screen, mouse_pos):
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, COLOR_REGISTER_BORDER, self.rect, 2)
        
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

class Editor:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.lines = ["LOCO 10", "STOD 500", "LODD 500", "ADDD 500", "JUMP 0"] # Codigo padrao
        self.font = pygame.font.SysFont("Consolas", 16)
        self.active = False
        self.cursor_line = 0
        self.cursor_col = 0
        self.line_height = 20
        self.scroll_y = 0

    def ensure_cursor_visible(self):
        cursor_y = 10 + self.cursor_line * self.line_height
        if cursor_y < self.scroll_y:
            self.scroll_y = cursor_y
        elif cursor_y + self.line_height > self.scroll_y + self.rect.height - 20:
            self.scroll_y = cursor_y + self.line_height - (self.rect.height - 20)

    def copy(self):
        if self.cursor_line < len(self.lines):
            text = self.lines[self.cursor_line]
            pygame.scrap.put(pygame.SCRAP_TEXT, text.encode('utf-8'))

    def cut(self):
        if self.cursor_line < len(self.lines):
            text = self.lines[self.cursor_line]
            pygame.scrap.put(pygame.SCRAP_TEXT, text.encode('utf-8'))
            self.lines.pop(self.cursor_line)
            if not self.lines:
                self.lines = [""]
            self.cursor_line = max(0, min(self.cursor_line, len(self.lines) - 1))
            self.cursor_col = 0

    def paste(self):
        try:
            text = pygame.scrap.get(pygame.SCRAP_TEXT)
            if text:
                if isinstance(text, bytes):
                    text = text.decode('utf-8', errors='ignore')
                
                text = text.replace('\r\n', '\n').replace('\r', '\n')
                text = text.replace('\x00', '')
                
                new_lines = text.split('\n')
                
                current_line = self.lines[self.cursor_line]
                prefix = current_line[:self.cursor_col]
                suffix = current_line[self.cursor_col:]
                
                self.lines[self.cursor_line] = prefix + new_lines[0]
                
                for i in range(1, len(new_lines)):
                    self.lines.insert(self.cursor_line + i, new_lines[i])
                
                last_paste_line_idx = self.cursor_line + len(new_lines) - 1
                if len(new_lines) > 1:
                    self.lines[last_paste_line_idx] += suffix
                    self.cursor_col = len(new_lines[-1])
                else:
                    self.lines[last_paste_line_idx] += suffix
                    self.cursor_col += len(new_lines[0])
                
                self.cursor_line = last_paste_line_idx
                
        except Exception as e:
            print(f"Erro ao colar: {e}")

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
                # Handle click with scroll
                rel_y = event.pos[1] - self.rect.y + self.scroll_y - 10
                self.cursor_line = max(0, min(len(self.lines) - 1, int(rel_y // self.line_height)))
                self.cursor_col = len(self.lines[self.cursor_line])
                self.ensure_cursor_visible()
            else:
                self.active = False
        
        elif event.type == pygame.MOUSEWHEEL:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.scroll_y -= event.y * self.line_height
                # Clamp scroll
                max_scroll = max(0, len(self.lines) * self.line_height - self.rect.height + 20)
                self.scroll_y = max(0, min(self.scroll_y, max_scroll))

        if self.active and event.type == pygame.KEYDOWN:
            ctrl = event.mod & pygame.KMOD_CTRL
            
            if ctrl and event.key == pygame.K_c:
                self.copy()
            elif ctrl and event.key == pygame.K_x:
                self.cut()
            elif ctrl and event.key == pygame.K_v:
                self.paste()
            elif ctrl and event.key == pygame.K_a:
                self.select_all_active = True
                return

            if getattr(self, 'select_all_active', False):
                if event.key in [pygame.K_BACKSPACE, pygame.K_DELETE]:
                    self.lines = [""]
                    self.cursor_line = 0
                    self.cursor_col = 0
                    self.select_all_active = False
                    return
                elif event.unicode and event.unicode.isprintable():
                    self.lines = [""]
                    self.cursor_line = 0
                    self.cursor_col = 0
                    self.select_all_active = False
                else:
                    self.select_all_active = False

            if event.key == pygame.K_RETURN:
                current_line = self.lines[self.cursor_line]
                new_line = current_line[self.cursor_col:]
                self.lines[self.cursor_line] = current_line[:self.cursor_col]
                self.lines.insert(self.cursor_line + 1, new_line)
                self.cursor_line += 1
                self.cursor_col = 0
            elif event.key == pygame.K_BACKSPACE:
                if self.cursor_col > 0:
                    line = self.lines[self.cursor_line]
                    self.lines[self.cursor_line] = line[:self.cursor_col-1] + line[self.cursor_col:]
                    self.cursor_col -= 1
                elif self.cursor_line > 0:
                    prev_len = len(self.lines[self.cursor_line-1])
                    self.lines[self.cursor_line-1] += self.lines[self.cursor_line]
                    self.lines.pop(self.cursor_line)
                    self.cursor_line -= 1
                    self.cursor_col = prev_len
            elif event.key == pygame.K_DELETE:
                if self.cursor_col < len(self.lines[self.cursor_line]):
                    line = self.lines[self.cursor_line]
                    self.lines[self.cursor_line] = line[:self.cursor_col] + line[self.cursor_col+1:]
                elif self.cursor_line < len(self.lines) - 1:
                    self.lines[self.cursor_line] += self.lines[self.cursor_line+1]
                    self.lines.pop(self.cursor_line+1)
            elif event.key == pygame.K_LEFT:
                if self.cursor_col > 0:
                    self.cursor_col -= 1
                elif self.cursor_line > 0:
                    self.cursor_line -= 1
                    self.cursor_col = len(self.lines[self.cursor_line])
            elif event.key == pygame.K_RIGHT:
                if self.cursor_col < len(self.lines[self.cursor_line]):
                    self.cursor_col += 1
                elif self.cursor_line < len(self.lines) - 1:
                    self.cursor_line += 1
                    self.cursor_col = 0
            elif event.key == pygame.K_UP:
                self.cursor_line = max(0, self.cursor_line - 1)
                self.cursor_col = min(self.cursor_col, len(self.lines[self.cursor_line]))
            elif event.key == pygame.K_DOWN:
                self.cursor_line = min(len(self.lines) - 1, self.cursor_line + 1)
                self.cursor_col = min(self.cursor_col, len(self.lines[self.cursor_line]))
            elif not ctrl:
                if event.unicode and event.unicode.isprintable():
                    line = self.lines[self.cursor_line]
                    self.lines[self.cursor_line] = line[:self.cursor_col] + event.unicode + line[self.cursor_col:]
                    self.cursor_col += 1

    def draw(self, screen, current_pc=None):
        pygame.draw.rect(screen, (40, 40, 40), self.rect)
        pygame.draw.rect(screen, COLOR_REGISTER_BORDER, self.rect, 2)
        
        font_title = pygame.font.SysFont("Arial", 16, bold=True)
        title = font_title.render("Editor de Código (Assembly)", True, COLOR_TEXT)
        screen.blit(title, (self.rect.x, self.rect.y - 25))

        for i, line in enumerate(self.lines):
            y = self.rect.y + 10 + i * self.line_height - self.scroll_y
            if y < self.rect.y: continue
            if y > self.rect.bottom - 20: break 
            
            if current_pc is not None and i == current_pc:
                pygame.draw.rect(screen, (60, 60, 0), (self.rect.x + 2, y, self.rect.width - 4, self.line_height))
            
            if getattr(self, 'select_all_active', False):
                 pygame.draw.rect(screen, (0, 0, 100), (self.rect.x + 2, y, self.rect.width - 4, self.line_height))

            text_surf = self.font.render(f"{i:02}: {line}", True, COLOR_TEXT)
            screen.blit(text_surf, (self.rect.x + 10, y))

            if self.active and i == self.cursor_line:
                prefix = f"{i:02}: "
                prefix_width, _ = self.font.size(prefix)
                content_before_cursor = line[:self.cursor_col]
                content_width, _ = self.font.size(content_before_cursor)
                cursor_x = self.rect.x + 10 + prefix_width + content_width
                
                if (pygame.time.get_ticks() // 500) % 2 == 0:
                    pygame.draw.line(screen, COLOR_ACCENT, (cursor_x, y), (cursor_x, y + self.line_height), 2)

    def get_text(self):
        return self.lines

class HistoryLog:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.logs = []
        self.font = pygame.font.SysFont("Consolas", 14)
        # Calculate max logs based on height (minus title padding)
        self.line_height = 18
        self.max_logs = (h - 25) // self.line_height

    def add_log(self, message):
        if not message: return
        if self.logs and self.logs[-1] == message:
            return
        self.logs.append(message)
        # Keep only the last N logs that fit
        if len(self.logs) > self.max_logs:
            self.logs = self.logs[-self.max_logs:]

    def draw(self, screen):
        pygame.draw.rect(screen, (20, 20, 20), self.rect)
        pygame.draw.rect(screen, COLOR_REGISTER_BORDER, self.rect, 2)
        
        title_font = pygame.font.SysFont("Arial", 14, bold=True)
        title = title_font.render("Histórico de Execução", True, (200, 200, 200))
        screen.blit(title, (self.rect.x + 5, self.rect.y - 20))

        y = self.rect.y + 5
        for i, log in enumerate(self.logs):
            # Fade out older logs
            alpha = 255 if i == len(self.logs) - 1 else 150
            color = (200, 255, 200) if i == len(self.logs) - 1 else (150, 150, 150)
            
            log_surf = self.font.render(f"> {log}", True, color)
            # Clip text if too long
            if log_surf.get_width() > self.rect.width - 10:
                area = pygame.Rect(0, 0, self.rect.width - 10, self.line_height)
                screen.blit(log_surf, (self.rect.x + 5, y), area)
            else:
                screen.blit(log_surf, (self.rect.x + 5, y))
            y += self.line_height
            
class MemoryView:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.font = pygame.font.SysFont("Consolas", 14)
        self.title_font = pygame.font.SysFont("Arial", 14, bold=True)
        self.scroll_y = 0
        self.total_lines = 4096 # Total memory size

    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.scroll_y -= event.y
                # Clamp scroll
                max_scroll = self.total_lines - 10 # Approx
                self.scroll_y = max(0, min(self.scroll_y, max_scroll))

    def draw(self, screen, memory, last_access_addr=None):
        pygame.draw.rect(screen, (30, 30, 35), self.rect)
        pygame.draw.rect(screen, COLOR_REGISTER_BORDER, self.rect, 2)
        
        # Title
        title = self.title_font.render("Memória (RAM)", True, COLOR_TEXT)
        screen.blit(title, (self.rect.x + 5, self.rect.y + 5))
        
        # Header
        header = self.font.render("Endereço | Valor", True, (150, 150, 150))
        screen.blit(header, (self.rect.x + 5, self.rect.y + 25))
        pygame.draw.line(screen, (100, 100, 100), (self.rect.x + 5, self.rect.y + 42), (self.rect.right - 5, self.rect.y + 42))
        
        # Content
        y_start = self.rect.y + 45
        line_h = 18
        lines_visible = (self.rect.height - 50) // line_h
        
        start_idx = int(self.scroll_y)
        end_idx = min(len(memory.data), start_idx + lines_visible + 1)
        
        y = y_start
        for addr in range(start_idx, end_idx):
            if y + line_h > self.rect.bottom - 5: break
            
            val = memory.data[addr]
            
            # Background for zebra striping
            if addr % 2 == 0:
                pygame.draw.rect(screen, (35, 35, 40), (self.rect.x + 2, y, self.rect.width - 4, line_h))

            # Highlight last access
            if last_access_addr == addr:
                pygame.draw.rect(screen, THEME_HIGHLIGHT_MEM, (self.rect.x + 2, y, self.rect.width - 4, line_h))
                color = (255, 255, 255) # White text on highlight
            else:
                color = COLOR_TEXT

            text = f"{addr:04} ({addr:03X}) | {val:05} (0x{val:04X})"
            surf = self.font.render(text, True, color)
            screen.blit(surf, (self.rect.x + 5, y))
            y += line_h

class GUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Simulador MIC-1 - Modo Gráfico")
        pygame.scrap.init()
        self.font = pygame.font.SysFont("Consolas", 16)
        self.value_font = pygame.font.SysFont("Consolas", 14)
        self.title_font = pygame.font.SysFont("Arial", 20, bold=True)
        self.clock = pygame.time.Clock()
        
        btn_y = SCREEN_HEIGHT - 60
        self.buttons = [
            Button(50, btn_y, 100, 40, "PASSO", "STEP"),
            Button(170, btn_y, 120, 40, "EXECUTAR", "RUN"),
            Button(310, btn_y, 100, 40, "REINICIAR", "RESET"),
            Button(800, btn_y, 100, 40, "CARREGAR", "LOAD")
        ]
        
        self.editor = Editor(800, 50, 350, 600)
        # Adjusted height to prevent overlap with buttons
        self.history_log = HistoryLog(50, 550, 700, 180) 
        
        self.status_message = "Pronto. Digite o código e clique em CARREGAR."
        self.status_color = COLOR_TEXT
        
        # Memory View
        self.memory_view = MemoryView(550, 120, 200, 250)
        
        # Glow Logic Removed
        self.prev_reg_values = {}

    def get_explanation(self, mpc):
        explanations = {
            0: "Busca: PC envia endereço para MAR (Endereço de Memória).",
            1: "Busca: Incrementa PC. Memória lê dados para MBR.",
            2: "Busca: MBR envia instrução para IR. Decodifica próxima microinstrução.",
            10: "LODD: IR envia endereço do operando para MAR.",
            11: "LODD: Lê dado da memória para MBR e salva no Acumulador (AC).",
            15: "STOD: IR envia endereço de destino para MAR.",
            16: "STOD: Envia valor do AC para MBR e escreve na Memória.",
            20: "ADDD: IR envia endereço do operando para MAR.",
            21: "ADDD: Lê dado da memória para MBR.",
            22: "ADDD: Soma AC + MBR e salva resultado no AC.",
            25: "SUBD: IR envia endereço do operando para MAR.",
            26: "SUBD: Lê dado da memória para MBR.",
            27: "SUBD: Subtrai AC - MBR e salva resultado no AC.",
            30: "JPOS: Se AC >= 0, atualiza PC com novo endereço.",
            35: "JZER: Se AC == 0, atualiza PC com novo endereço.",
            40: "JUMP: Atualiza PC incondicionalmente com novo endereço.",
            45: "LOCO: Carrega constante (do IR) diretamente no AC.",
            80: "CALL: Prepara para salvar retorno. Decrementa SP.",
            81: "CALL: Salva PC atual na pilha (apontada por SP).",
            82: "CALL: Escreve na memória.",
            83: "CALL: Pula para o endereço da subrotina.",
            91: "PUSH: Coloca valor do AC na pilha.",
            92: "PUSH: Escreve na memória.",
            94: "POP: Lê valor da pilha para MBR.",
            95: "POP: Move valor para AC e restaura SP.",
            97: "RETN: Lê endereço de retorno da pilha.",
            98: "RETN: Restaura PC e SP. Retorna da subrotina.",
        }
        return explanations.get(mpc, f"Executando microinstrução no endereço {mpc}...")

    def draw_rect_with_text(self, x, y, w, h, text, value=None, active=False, highlight=False):
        color = COLOR_ACCENT if active else (COLOR_HIGHLIGHT if highlight else COLOR_REGISTER)
        border_color = COLOR_REGISTER_BORDER
        
        pygame.draw.rect(self.screen, color, (x, y, w, h))
        pygame.draw.rect(self.screen, border_color, (x, y, w, h), 2)
        
        # Center text
        label_surf = self.font.render(text, True, COLOR_TEXT)
        label_rect = label_surf.get_rect(midtop=(x + w//2, y + 5))
        self.screen.blit(label_surf, label_rect)
        
        if value is not None:
            # Use ALU helper for signed conversion
            from hardware import ALU
            signed_val = ALU.to_signed(value)
            val_str = f"{signed_val} (0x{value:04X})"
            val_surf = self.value_font.render(val_str, True, COLOR_TEXT)
            # Center and clamp
            val_rect = val_surf.get_rect(midbottom=(x + w//2, y + h - 2))
            if val_rect.width > w - 4:
                # If still too wide, scale it down (simple scaling)
                scale_factor = (w - 4) / val_rect.width
                new_w = int(val_rect.width * scale_factor)
                new_h = int(val_rect.height * scale_factor)
                val_surf = pygame.transform.smoothscale(val_surf, (new_w, new_h))
                val_rect = val_surf.get_rect(midbottom=(x + w//2, y + h - 2))
            
            self.screen.blit(val_surf, val_rect)

    def draw_cpu(self, cpu):
        self.screen.fill(COLOR_BACKGROUND)
        mouse_pos = pygame.mouse.get_pos()
        
        if hasattr(cpu, 'last_action_desc'):
             self.history_log.add_log(cpu.last_action_desc)
        
        x_left = 50
        y = 50
        regs_left = [('MAR', cpu.mar), ('MBR', cpu.mbr), ('PC', cpu.pc), ('SP', cpu.sp), ('AC', cpu.ac)]
        for name, reg in regs_left:
            val = reg.read()
            is_active = name in cpu.signals['active_path']
            self.draw_rect_with_text(x_left, y, REG_WIDTH, REG_HEIGHT, name, val, active=is_active)
            y += REG_HEIGHT + GAP_Y

        x_right = 300
        y = 50
        regs_right = [('IR', cpu.ir), ('TIR', cpu.tir)]
        for name, reg in regs_right:
            val = reg.read()
            is_active = name in cpu.signals['active_path']
            self.draw_rect_with_text(x_right, y, REG_WIDTH, REG_HEIGHT, name, val, active=is_active)
            y += REG_HEIGHT + GAP_Y
            
        alu_active = 'ALU' in cpu.signals['active_path']
        self.draw_rect_with_text(x_right, y + 20, REG_WIDTH, REG_HEIGHT, "ULA (ALU)", active=alu_active)
        
        x_mem = 550
        y_mem = 50
        cache_status = cpu.cache.last_access_type
        color_cache = COLOR_CACHE_HIT if cache_status == "HIT" else (COLOR_CACHE_MISS if cache_status == "MISS" else COLOR_INACTIVE)
        pygame.draw.rect(self.screen, color_cache, (x_mem, y_mem, 150, 50))
        pygame.draw.rect(self.screen, COLOR_REGISTER_BORDER, (x_mem, y_mem, 150, 50), 2)
        status_text = f"CACHE: {cache_status}"
        text_surf = self.font.render(status_text, True, COLOR_TEXT)
        self.screen.blit(text_surf, (x_mem + 10, y_mem + 15))
        
        # Draw Memory View
        last_access = cpu.mar.read() if cpu.signals['read_mem'] or cpu.signals['write_mem'] else None
        self.memory_view.draw(self.screen, cpu.memory, last_access_addr=last_access)
        
        y_sig = 400
        x_sig = 50
        signals_str = f"Leitura: {cpu.signals['read_mem']} | Escrita: {cpu.signals['write_mem']} | ULA: {cpu.signals['alu_op']}"
        sig_surf = self.font.render(signals_str, True, COLOR_TEXT)
        self.screen.blit(sig_surf, (x_sig, y_sig))
        
        mpc_str = f"MPC: {cpu.mpc}"
        mpc_surf = self.title_font.render(mpc_str, True, COLOR_HIGHLIGHT)
        self.screen.blit(mpc_surf, (x_sig, y_sig + 30))
        
        # --- Explanation Panel ---
        exp_y = y_sig + 70 # 470
        pygame.draw.rect(self.screen, (50, 50, 60), (x_sig, exp_y, 700, 60))
        pygame.draw.rect(self.screen, COLOR_REGISTER_BORDER, (x_sig, exp_y, 700, 60), 2)
        
        explanation = self.get_explanation(cpu.mpc)
        exp_surf = self.font.render(explanation, True, (255, 255, 200))
        self.screen.blit(exp_surf, (x_sig + 10, exp_y + 20))
        
        # --- History Log ---
        # Title at y - 20, so rect.y must be > exp_y + 60 + 20 = 550
        self.history_log.rect.y = exp_y + 90 # 560
        self.history_log.rect.height = 130   # Ends at 690
        self.history_log.max_logs = (self.history_log.rect.height - 25) // self.history_log.line_height
        self.history_log.draw(self.screen)
        
        # --- Buttons ---
        btn_y = 720
        for i, btn in enumerate(self.buttons):
            btn.rect.y = btn_y
        
        for btn in self.buttons:
            btn.draw(self.screen, mouse_pos)

        # Status Bar (Bottom)
        status_y = 770
        status_color = (255, 50, 50) if "Erro" in self.status_message else self.status_color
        status_surf = self.font.render(f"Status: {self.status_message}", True, status_color)
        self.screen.blit(status_surf, (x_sig, status_y))
        
        # --- Editor ---
        self.editor.draw(self.screen, current_pc=cpu.pc.read())

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            
            self.editor.handle_event(event)
            self.memory_view.handle_event(event)
            
            for btn in self.buttons:
                if btn.is_clicked(event):
                    return btn.action_name
            
            if not self.editor.active and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return "STEP"
                if event.key == pygame.K_r:
                    return "RUN"
                    
        return None
