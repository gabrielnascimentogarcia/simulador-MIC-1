# Tutorial do Simulador MIC-1

Bem-vindo ao simulador da microarquitetura **MIC-1** (Micro-Architecture 1), baseada no design de Andrew S. Tanenbaum. Este simulador permite visualizar o funcionamento interno de um processador, ciclo a ciclo, executando instruções da arquitetura **MAC-1** (Macro-Architecture 1).

## 1. Requisitos e Instalação

Para executar o simulador, você precisa ter instalado:
- **Python 3.x**
- **Biblioteca Pygame**

### Instalação das dependências
Abra o terminal e execute:
```bash
pip install pygame
```

## 2. Como Executar

No diretório do projeto, execute o arquivo principal:
```bash
python main.py
```
Uma janela gráfica será aberta contendo o simulador.

## 3. Interface do Simulador

A interface é dividida em três partes principais:

### Caminho de Dados (Datapath)
Visualização gráfica dos componentes internos da CPU:
- **Registradores**: Caixas retangulares mostrando o valor atual (em decimal e hexadecimal).
  - **PC**: Program Counter (Contador de Programa).
  - **SP**: Stack Pointer (Ponteiro de Pilha).
  - **AC**: Accumulator (Acumulador - onde ocorrem as operações).
  - **MAR**: Memory Address Register (Registrador de Endereço de Memória).
  - **MBR**: Memory Buffer Register (Registrador de Buffer de Memória).
  - **IR**: Instruction Register (Registrador de Instrução).
  - **TIR**: Temporary Instruction Register.
- **ULA (ALU)**: Unidade Lógica e Aritmética.
- **Barramento**: Linhas que conectam os componentes. Elas acendem (ficam verdes) quando dados estão trafegando por elas.

### Memória e Cache
- **Cache**: Mostra o status do último acesso à memória (`HIT` ou `MISS`).
- **Sinais de Controle**: Mostra quais sinais estão ativos (Leitura, Escrita, Operação da ULA).
- **MPC**: Micro Program Counter - mostra qual microinstrução está sendo executada.
- **Explicação**: Um painel de texto explica o que a microinstrução atual está fazendo (ex: "Busca: PC envia endereço para MAR").

### Editor e Controles
- **Editor de Código**: Área à direita onde você pode escrever ou colar seu código Assembly.
- **Botões**:
  - **PASSO (STEP)**: Executa apenas um ciclo de clock (uma microinstrução). Atalho: `Espaço`.
  - **EXECUTAR (RUN)**: Executa continuamente até ser pausado. Atalho: `R`.
  - **REINICIAR (RESET)**: Limpa a memória e reinicia a CPU.
  - **CARREGAR (LOAD)**: Compila o código do editor e carrega na memória.

## 4. Programando em Assembly (MAC-1)

O simulador aceita um conjunto de instruções simplificado da arquitetura MAC-1.

### Sintaxe Básica
Cada linha deve conter uma instrução e, opcionalmente, um operando.
Comentários podem ser adicionados com `;`.

Exemplo:
```asm
LOCO 10   ; Carrega o valor 10 no Acumulador
ADDD 50   ; Soma o valor da memória no endereço 50 ao Acumulador
STOD 100  ; Salva o resultado no endereço 100
```

### Lista de Instruções (Opcodes)

| Mnemônico | Operando | Descrição |
|-----------|----------|-----------|
| **LODD**  | Endereço | Carrega dados da memória (Direct Addressing) para o AC. |
| **STOD**  | Endereço | Salva o valor do AC na memória. |
| **ADDD**  | Endereço | Soma (AC = AC + Memória[Endereço]). |
| **SUBD**  | Endereço | Subtrai (AC = AC - Memória[Endereço]). |
| **JPOS**  | Endereço | Pula se AC >= 0. |
| **JZER**  | Endereço | Pula se AC == 0. |
| **JUMP**  | Endereço | Pula incondicionalmente. |
| **LOCO**  | Constante| Carrega uma constante (0-4095) diretamente no AC. |
| **LODL**  | Endereço | Carrega local (Pilha + Deslocamento). |
| **STOL**  | Endereço | Salva local (Pilha + Deslocamento). |
| **ADDL**  | Endereço | Soma local. |
| **SUBL**  | Endereço | Subtrai local. |
| **JNEG**  | Endereço | Pula se AC < 0. |
| **JNZE**  | Endereço | Pula se AC != 0. |
| **CALL**  | Endereço | Chama subrotina (salva PC na pilha). |
| **PUSH**  | -        | Empilha o valor do AC. |
| **POP**   | -        | Desempilha para o AC. |
| **RETN**  | -        | Retorna de subrotina. |
| **SWAP**  | -        | Troca AC e SP (útil para manipulação de pilha). |

## 5. Exemplo Passo a Passo

1.  Abra o simulador.
2.  No editor (lado direito), digite o seguinte código:
    ```asm
    LOCO 5      ; Carrega 5 no AC
    STOD 500    ; Salva 5 no endereço 500
    LOCO 3      ; Carrega 3 no AC
    ADDD 500    ; Soma com o valor no endereço 500 (5 + 3 = 8)
    STOD 501    ; Salva o resultado (8) no endereço 501
    JUMP 0      ; Reinicia o programa (loop infinito)
    ```
3.  Clique em **CARREGAR**. O status mudará para "Codigo Carregado com Sucesso!".
4.  Clique em **PASSO** várias vezes para ver cada microinstrução sendo executada.
    - Observe o **PC** incrementando.
    - Observe o **MAR** recebendo endereços.
    - Observe o **AC** mudando de valor.
5.  Clique em **EXECUTAR** para ver rodando automaticamente.

## 6. Dicas
- Use **PASSO** para entender exatamente o que acontece em cada ciclo (Busca, Decodificação, Execução).
- O painel de "Histórico de Execução" mostra um log das últimas ações.
- Se houver erro no código (ex: mnemônico inválido), o status ficará vermelho com a mensagem de erro.
