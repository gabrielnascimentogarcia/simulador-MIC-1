; Exemplo 2: Contador Regressivo
; Conta de 5 ate 0

LOCO 5      ; Inicia contador com 5
STOD 100    ; Salva contador na memoria[100]

; Loop Principal
LODD 100    ; Carrega contador
JZER 10     ; Se for Zero, pula para o fim (endereco 10)
SUBD 200    ; Subtrai 1 (precisamos ter 1 na memoria[200])
STOD 100    ; Salva novo valor
JUMP 2      ; Volta para o inicio do loop (LODD 100 eh a linha 2 se contarmos do 0)
            ; Nota: JUMP usa enderecos absolutos, entao cuidado ao editar!

; Fim
LOCO 0      ; Limpa AC
JUMP 10     ; Loop infinito no fim

; Constantes (Gambiarra: MAC-1 nao tem instrucao de dados, entao usamos LOCO/STOD no inicio ou assumimos memoria)
; Para este exemplo funcionar, precisamos colocar 1 na memoria 200.
; Vamos fazer isso no codigo:
LOCO 1
STOD 200
JUMP 0      ; Comeca o programa real
