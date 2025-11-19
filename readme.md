
**Contexto:**
Você é um Engenheiro de Software Sênior e deve criar um simulador completo e funcional da microarquitetura **MIC-1** (que implementa o conjunto de instruções MAC-1), utilizando **Python** e **Pygame**. O projeto deve ser modular, orientado a objetos e containerizável (Docker).

O objetivo é ter um backend que simule o ciclo de busca, decodificação e execução microinstrução por microinstrução (conforme o livro do Tanenbaum), e um frontend que desenhe o caminho de dados (Datapath).

**Estrutura de Arquivos Obrigatória:**
O projeto deve ser dividido nos seguintes arquivos:
1.  `config.py`: Constantes, mapas de opcodes e configurações de tela.
2.  `hardware.py`: Classes para Registradores, Memória RAM, Cache e ULA (ALU).
3.  `cpu.py`: A Unidade de Controle (Micro-sequenciador) e lógica de transição de estados.
4.  `assembler.py`: Tradutor de Assembly (.asm) para Código de Máquina.
5.  `gui.py`: Interface gráfica usando Pygame.
6.  `main.py`: Arquivo principal de execução.

---

### Especificações Detalhadas por Módulo

#### 1. `config.py`
Defina as constantes exatas da ISA MAC-1:
- **Instruções:**
  ```python
  OPCODES = {
      'LODD': 0x0, 'STOD': 0x1, 'ADDD': 0x2, 'SUBD': 0x3,
      'JPOS': 0x4, 'JZER': 0x5, 'JUMP': 0x6, 'LOCO': 0x7,
      'LODL': 0x8, 'STOL': 0x9, 'ADDL': 0xA, 'SUBL': 0xB,
      'JNEG': 0xC, 'JNZE': 0xD, 'CALL': 0xE, 'PSHI': 0xF,
      'POPI': 0xF, 'PUSH': 0xF, 'POP': 0xF, 'RETN': 0xF,
      'SWAP': 0xF, 'INSP': 0xF, 'DESP': 0xF
  }
  # Nota: As instruções F (1111) variam nos 8 bits inferiores (ver PDF), trate isso no assembler.
  ```
- Defina cores (RGB) para: Fundo, Registradores, Texto, Linhas Ativas (Verde) e Linhas Inativas (Cinza).

#### 2. `hardware.py`
Implemente as classes físicas:
- **`Register`**: Deve armazenar um valor de 16-bit (`self.value`). Métodos: `read()`, `write(val)`.
- **`Memory`**: Array de 4096 posições (inteiros). Métodos: `read(addr)`, `write(addr, val)`.
- **`Cache` (Requisito Crítico)**:
  - Implemente uma Cache de Mapeamento Direto.
  - Tamanho sugerido: 16 linhas.
  - Estrutura: `lines` contendo `{valid: bool, tag: int, data: int}`.
  - Lógica: Ao ler da memória, verifique a cache. Se `Hit`, retorne rápido. Se `Miss`, busque na `Memory`, atualize a cache e retorne.
  - Deve ter um flag `last_access_type` ("HIT" ou "MISS") para a GUI mostrar.
- **`ALU`**: Métodos para soma, subtração, AND e deslocamento (shift). Deve setar flags globais `N` (negativo) e `Z` (zero).

#### 3. `assembler.py`
Crie uma função `assemble(lines) -> list[int]`.
- Deve ler linha por linha.
- Identificar Mnemônicos (ex: `LODD`).
- Converter operandos numéricos para binário.
- **Formato da Instrução (16 bits):**
  - Bits 15-12: Opcode.
  - Bits 11-0: Endereço/Constante.
- Tratamento especial para instruções do tipo `1111` (PUSH, POP, etc), onde o opcode é fixo e os bits inferiores definem a operação (consulte a tabela MAC-1 padrão).

#### 4. `cpu.py` (O Coração do Simulador)
Classe `CPU`.
- **Componentes:** Instancie `PC`, `AC`, `SP`, `IR`, `TIR`, `MAR`, `MBR`, `Memory`, `Cache`.
- **Estado:** `MPC` (Micro Program Counter) inicia em 0.
- **Método `cycle()`**: Executa **APENAS UM** passo do microcódigo por chamada.
- **Lógica do Micro-sequenciador:**
  Utilize um `match self.mpc` para implementar as linhas 0 a 78 do PDF.
  *Exemplo de lógica:*
  - `case 0`: (Fetch) `MAR <- PC`; `MPC = 1`.
  - `case 1`: `PC <- PC + 1`; `MBR <- Cache.read(MAR)`; `MPC = 2`.
  - `case 2`: `IR <- MBR`; `MPC = decode_instruction(IR)`.
  
  **Função `decode_instruction(ir)`**:
  Em vez de simular a lógica binária complexa de decodificação do hardware original, faça um mapeamento direto em Python:
  - Se opcode é `LODD` (0000) -> Retorna `6` (início da microrrotina LODD).
  - Se opcode é `ADDD` (0010) -> Retorna `12`.
  - E assim por diante para todas as instruções.

#### 5. `gui.py` (Visualização)
Use Pygame.
- **Layout:**
  - Desenhe retângulos verticais representando a pilha de registradores (como na Página 3 do PDF): `MAR`, `MBR`, `PC`, `SP`, `AC` na esquerda; `IR`, `TIR`, `ALU` na direita.
  - Desenhe linhas conectando-os (Barramento).
- **Animação:**
  - Método `draw(screen, cpu)`:
    - Desenha cada registrador com seu valor atual (Hex e Decimal).
    - Se `cpu.signals['write_ac']` for True, desenhe o registrador AC com borda Verde brilhante.
    - Se houver leitura de memória, mostre um indicador visual de "CACHE HIT" ou "CACHE MISS" baseado no status da classe Cache.
  - Inclua uma área de texto na lateral mostrando o Código Assembly carregado e destacando a linha atual (baseado no PC).

#### 6. `main.py`
- Inicialize o Pygame.
- Carregue um programa de exemplo (hardcoded ou arquivo).
  - *Exemplo de programa:* `LOCO 10`, `STOD 500`, `LODD 500`, `ADDD 500`, `JUMP 0`.
- Loop Principal:
  - Verifique eventos (botão "Step" ou "Run").
  - Chame `cpu.cycle()`.
  - Chame `gui.draw()`.

---

### Requisitos Especiais para a IA
1.  **Simplicidade na Decodificação:** Não tente implementar o decodificador de hardware original (4-to-16 decoder). Use lógica Python (`if/else`) para saltar do Fetch (`MPC=2`) para o início da microrrotina correta.
2.  **Microcódigo:** Implemente explicitamente o fluxo de controle das microinstruções básicas (LODD, STOD, ADDD, SUBD, JUMPS, LOCO). As instruções complexas (CALL, PSHI) podem ser deixadas como "TODO" se o código ficar muito longo, mas a estrutura deve estar lá.
3.  **Robustez:** O código deve tratar erros de sintaxe no Assembly com mensagens claras no console.

**Ação:** Gere o código completo, arquivo por arquivo, pronto para ser executado. Comece pelo `config.py` e vá até o `main.py`.